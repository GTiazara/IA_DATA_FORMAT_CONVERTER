# Tasks

## 1. Initialisation du projet Poetry

- [x] 1.1 Créer `pyproject.toml` (PEP 621, `requires-python >=3.11`, deps `pyarrow` et `pyyaml`, groupe dev `pytest` et `ruff`, `[tool.poetry] packages` depuis `src`, script `ia-convert`, config pytest/ruff) et vérifier avec `poetry check`
- [x] 1.2 Créer le squelette `src/ia_data_format_converter/` (`__init__.py`, `__main__.py`, `writers/__init__.py`), `tests/`, `.gitignore` (venv, caches, sorties générées), et vérifier que `poetry install` réussit et génère `poetry.lock`
- [x] 1.3 Créer le `Makefile` (help, install, test, lint, format-check, run, check) conforme à `AGENTS.md` et vérifier que `make help` et `make lint` s'exécutent

## 2. Lecture CSV et erreurs

- [x] 2.1 Implémenter `errors.py` (`ConversionError`, `InputFileError`, `UnknownFormatError`, `OutputExistsError`, `InvalidOptionError`) et vérifier par import dans les tests
- [x] 2.2 Implémenter `readers.read_csv(path, sep, encoding)` retournant une `pyarrow.Table` (inférence de types, nulls sur cellules vides, erreurs réémises en `InputFileError`) et vérifier avec `tests/test_readers.py` : types int/float, cellules vides, séparateur `;`, encodage latin-1, fichier absent, fichier vide, ligne au nombre de champs incorrect

## 3. Registre de writers et Feather

- [x] 3.1 Définir le protocole `Writer` et le registre (`available_formats()`, `get_writer(name)` levant `UnknownFormatError` avec la liste des formats) dans `writers/__init__.py` et vérifier avec `tests/test_writers.py` (liste contient `feather`, `parquet` refusé)
- [x] 3.2 Implémenter `writers/feather.py` (extension `.feather`, compression `lz4` par défaut / `zstd` / `uncompressed`, `InvalidOptionError` sinon) et vérifier dans `tests/test_writers.py` la relecture via `pyarrow.feather` et le refus d'une compression invalide

## 4. Orchestration de la conversion

- [x] 4.1 Implémenter `converter.convert(input_path, output_path, fmt, *, sep, encoding, overwrite, **options)` : vérif. sortie existante avant lecture, écriture dans un temporaire du même dossier puis `os.replace`, nettoyage en cas d'échec ; exporter `convert`, `available_formats`, `ConversionError` dans `__init__.py`
- [x] 4.2 Vérifier avec `tests/test_converter.py` : conversion réussie (colonnes, ordre, nombre de lignes, valeurs), sortie existante refusée et inchangée, `overwrite=True` remplace, format inconnu sans fichier créé, CSV mal formé sans sortie partielle

## 5. Configuration YAML

- [x] 5.1 Implémenter `config.py` (`load_config(path)` via `yaml.safe_load`, clés autorisées `input`, `output`, `to`, `sep`, `encoding`, `compression`, `overwrite`, validation de type, `ConfigError` nommant le paramètre, chemins relatifs résolus depuis le dossier du fichier) et vérifier avec `tests/test_config.py` (config valide, clé inconnue, type invalide, résolution des chemins)
- [x] 5.2 Ajouter `conf/example.yaml` et `conf/README.md` décrivant les clés et la résolution des chemins, et vérifier que `load_config("conf/example.yaml")` passe dans un test

## 6. Interface en ligne de commande

- [x] 6.1 Implémenter `cli.py` (`main(argv=None) -> int`) : argparse avec `input`, `--to` (choix depuis le registre), `-o/--output`, `--sep`, `--encoding`, `--compression`, `--overwrite`, `--config` ; fusion défauts < config < CLI ; sortie par défaut = même nom avec l'extension du writer ; erreurs sur stderr sans trace et code 1 ; `__main__.py` appelle `main`
- [x] 6.2 Vérifier avec `tests/test_cli.py` (via `main([...])` et `capsys`) : conversion réussie code 0, `--help` liste les formats, sortie implicite, `--overwrite`, refus d'écrasement code non nul, fichier absent, format inconnu, valeurs issues de la config, priorité CLI sur config, config invalide

## 7. Documentation et vérification finale

- [x] 7.1 Rédiger `README.md` : installation (Poetry), version Python, commande `ia-convert` et options, exemple avec `conf/example.yaml`, entrées/sorties, ajout futur d'un format (Parquet, Zarr, SQLite) via un nouveau writer, lancement des tests ; vérifier que les commandes documentées s'exécutent telles quelles
- [x] 7.2 Exécuter `make check` et `make format-check` et vérifier qu'ils passent sans erreur
