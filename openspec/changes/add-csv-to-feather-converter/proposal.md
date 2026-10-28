# Proposal

## Why

Les jeux de données tabulaires utilisés pour le machine learning et les tâches d'IA sont souvent livrés en CSV, un format textuel lent à relire, sans types de colonnes et volumineux. Le format Feather (Apache Arrow IPC) permet un chargement rapide et typé dans pandas/polars/pyarrow. Le dépôt est vide : il faut créer l'outil Python (Poetry) qui réalise cette conversion, en préparant dès le départ l'ajout futur d'autres formats (Apache Parquet, Zarr, SQLite, ...).

## What Changes

- Création d'un projet Python packagé avec Poetry, en layout `src/` (package `ia_data_format_converter`), conforme à `AGENTS.md` (Makefile, tests pytest, lint Ruff, `conf/`, README).
- Nouvelle fonction de conversion réutilisable : lecture d'un fichier CSV tabulaire et écriture au format Feather (Arrow IPC v2), avec options de base (séparateur, encodage, compression).
- Registre de formats de sortie extensible : chaque format cible est un « writer » enregistré sous un nom (`feather` dans cette version). Ajouter Parquet, Zarr ou SQLite plus tard consistera à ajouter un writer, sans modifier la CLI ni la lecture CSV.
- Nouvelle commande CLI `ia-convert` : `ia-convert INPUT.csv --to feather [-o OUTPUT]`, avec configuration YAML optionnelle depuis `conf/`, refus d'écraser une sortie existante sauf `--overwrite`, et code de sortie non nul en cas d'erreur.
- Hors périmètre : implémentation de Parquet, Zarr, SQLite ; formats d'entrée autres que CSV ; traitement en streaming de fichiers plus grands que la mémoire ; transformations de données (nettoyage, encodage de features).

## Capabilities

### New Capabilities
- `tabular-conversion`: lecture d'un CSV tabulaire et conversion vers un format de sortie enregistré (Feather pour l'instant), via un registre extensible de formats.
- `converter-cli`: interface en ligne de commande `ia-convert` (arguments, configuration YAML, gestion de l'écrasement, rapport d'erreurs et codes de sortie).

### Modified Capabilities
<!-- Aucune : pas de spec existante. -->

## Impact

- Nouveau code : `pyproject.toml`, `poetry.lock`, `src/ia_data_format_converter/`, `tests/`, `conf/`, `Makefile`, `.gitignore`, mise à jour de `README.md`.
- Dépendances d'exécution : `pyarrow` (lecture CSV et écriture Feather ; servira aussi pour Parquet), `pyyaml` (configuration).
- Dépendances de développement : `pytest`, `ruff`.
- Python supporté : >= 3.11.
