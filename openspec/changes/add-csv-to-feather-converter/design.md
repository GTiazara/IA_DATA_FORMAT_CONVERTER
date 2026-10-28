# Design

## Context

Dépôt vierge (seulement `README.md`, `AGENTS.md`, `openspec/`). `AGENTS.md` impose : Poetry, layout `src/`, CLI séparée de la logique, configuration dans `conf/`, tests pytest, Ruff, Makefile mince. Voir proposal.md pour la motivation et specs/ pour les exigences.

## Goals / Non-Goals

**Goals:**
- Conversion CSV → Feather fiable et typée, utilisable en bibliothèque et en CLI.
- Point d'extension unique et simple pour ajouter Parquet, Zarr, SQLite plus tard.

**Non-Goals:**
- Lecture en streaming / fichiers plus grands que la mémoire.
- Plugins externes chargés dynamiquement (entry points) : inutile tant que les formats sont internes.
- Schéma de colonnes imposé par l'utilisateur (types forcés) : pourra être ajouté ensuite.

## Decisions

### Structure du package

```text
src/ia_data_format_converter/
├── __init__.py        # API publique : convert, available_formats, ConversionError
├── __main__.py        # python -m ia_data_format_converter
├── cli.py             # argparse, chargement config, rapport d'erreurs, code retour
├── config.py          # chargement/validation YAML
├── errors.py          # ConversionError et sous-classes
├── readers.py         # read_csv(path, sep, encoding) -> pyarrow.Table
├── converter.py       # convert(input, output, fmt, ...) : orchestration + écriture atomique
└── writers/
    ├── __init__.py    # registre : nom -> Writer
    └── feather.py     # FeatherWriter
```

### Représentation pivot : `pyarrow.Table`
Le CSV est lu en `pyarrow.Table`, puis chaque writer consomme cette table.
- Pourquoi : Feather est l'IPC Arrow natif ; Parquet s'écrit directement depuis Arrow ; Zarr et SQLite peuvent convertir depuis Arrow (`to_pandas()` / batches). Un seul modèle en mémoire évite N×M conversions.
- Lecture via `pyarrow.csv.read_csv` : inférence de types (int, float, bool, timestamp, string), nulls sur cellules vides, erreur sur nombre de colonnes incohérent.
- Alternative écartée : pandas comme pivot — dépendance plus lourde, types moins fidèles (entiers nullables), et passage par Arrow de toute façon pour Feather.

### Registre de writers
Un `Protocol` `Writer` avec `name`, `extension`, `write(table, path, **options)`, et une validation des options propres au format (ex. `compression` pour Feather). Le registre est un simple dict `{"feather": FeatherWriter()}` dans `writers/__init__.py`, exposé par `available_formats()` et `get_writer(name)`.
- Ajouter un format = un module dans `writers/` + une ligne dans le registre + tests. La CLI lit la liste depuis le registre (`choices` et aide).
- Alternative écartée : entry points / découverte dynamique — complexité non justifiée.
- Les dépendances lourdes des futurs formats (zarr, …) seront importées paresseusement dans leur writer et pourront être déclarées en extras Poetry.

### Écriture atomique et protection de la sortie
`convert` vérifie l'existence de la sortie avant toute lecture (échec rapide sans `overwrite`), écrit dans un fichier temporaire du même dossier puis `os.replace` vers la cible. En cas d'erreur, le temporaire est supprimé : aucune sortie partielle (spec « Erreurs d'entrée explicites »).

### Erreurs
`ConversionError` (base) avec sous-classes `InputFileError`, `UnknownFormatError`, `OutputExistsError`, `InvalidOptionError`. Les erreurs `pyarrow` (`ArrowInvalid`, `UnicodeDecodeError`) sont capturées dans `readers.py` et réémises en `InputFileError`. La CLI attrape `ConversionError` et `ConfigError`, écrit sur stderr, retourne 1 ; argparse retourne 2 pour les erreurs d'usage.

### Configuration
YAML chargé avec `yaml.safe_load`. Clés autorisées : `input`, `output`, `to`, `sep`, `encoding`, `compression`, `overwrite`. Validation explicite (clé inconnue, type). Fusion : valeurs par défaut < fichier < arguments CLI explicites (argparse avec `default=None` pour détecter les arguments non fournis). Chemins relatifs résolus depuis le dossier du fichier de config. Exemple fourni : `conf/example.yaml` + `conf/README.md`.

### Outillage
`pyproject.toml` au format `[project]` (PEP 621) + `[tool.poetry] packages` pour `src/`, `requires-python = ">=3.11"`, script `ia-convert = "ia_data_format_converter.cli:main"`. Dev : pytest, ruff. Makefile conforme à `AGENTS.md`.

## Risks / Trade-offs

- [Lecture entière en mémoire] → acceptable pour la première version ; `pyarrow.csv.open_csv` (streaming) pourra être utilisé plus tard pour Feather/Parquet.
- [Inférence de types imparfaite (ex. codes postaux lus comme entiers)] → documenté ; option de types forcés envisageable ultérieurement.
- [Taille de `pyarrow` (~40 Mo)] → justifiée car elle couvre aussi Parquet.
- [Futur Zarr/SQLite pas naturellement colonnaires Arrow] → le contrat `write(table, path)` reste suffisant ; chaque writer gère sa conversion.
