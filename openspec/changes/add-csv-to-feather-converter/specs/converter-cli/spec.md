# Spec Delta

## Purpose

Fournir une commande en ligne de commande permettant de lancer la conversion de données tabulaires, de la configurer par arguments ou par fichier YAML, et d'obtenir un statut de sortie exploitable dans des scripts.

## ADDED Requirements

### Requirement: Commande de conversion
Le système SHALL fournir la commande `ia-convert` prenant un chemin CSV en entrée et un format cible (`--to`), et produisant le fichier converti.

#### Scenario: Conversion par la CLI
- **WHEN** l'utilisateur exécute `ia-convert data.csv --to feather -o data.feather`
- **THEN** le fichier `data.feather` est créé et la commande se termine avec le code 0

#### Scenario: Aide
- **WHEN** l'utilisateur exécute `ia-convert --help`
- **THEN** l'aide décrit les arguments disponibles et les formats de sortie, avec le code 0

### Requirement: Chemin de sortie par défaut
Lorsque `-o/--output` n'est pas fourni, le système SHALL écrire la sortie à côté de l'entrée, avec le même nom de base et l'extension du format cible.

#### Scenario: Sortie implicite
- **WHEN** l'utilisateur exécute `ia-convert dir/data.csv --to feather` sans `-o`
- **THEN** le fichier `dir/data.feather` est créé

### Requirement: Options de conversion en ligne de commande
La commande SHALL accepter `--sep`, `--encoding`, `--compression` et `--overwrite`, avec le même comportement que les options de conversion correspondantes.

#### Scenario: Écrasement explicite
- **WHEN** la sortie existe et l'utilisateur passe `--overwrite`
- **THEN** la sortie est remplacée et la commande se termine avec le code 0

#### Scenario: Écrasement refusé
- **WHEN** la sortie existe et `--overwrite` n'est pas passé
- **THEN** la commande affiche une erreur sur la sortie d'erreur et se termine avec un code non nul

### Requirement: Configuration YAML
La commande SHALL accepter `--config FICHIER.yaml` fournissant des valeurs par défaut pour les options de conversion. Les arguments explicites de la ligne de commande SHALL être prioritaires sur le fichier. Les chemins relatifs du fichier SHALL être résolus par rapport au dossier du fichier de configuration.

#### Scenario: Valeurs issues de la configuration
- **WHEN** la configuration définit `sep: ";"` et `compression: zstd` et que la CLI ne les précise pas
- **THEN** la conversion utilise `;` et `zstd`

#### Scenario: Priorité de la ligne de commande
- **WHEN** la configuration définit `compression: zstd` et l'utilisateur passe `--compression lz4`
- **THEN** la conversion utilise `lz4`

#### Scenario: Configuration invalide
- **WHEN** la configuration contient une clé inconnue ou une valeur de type incorrect
- **THEN** la commande affiche une erreur nommant le paramètre invalide et se termine avec un code non nul

### Requirement: Rapport d'erreurs et codes de sortie
En cas d'échec, la commande SHALL afficher un message d'erreur lisible sur la sortie d'erreur, sans trace de pile, et se terminer avec un code non nul.

#### Scenario: Fichier d'entrée absent
- **WHEN** l'utilisateur exécute `ia-convert missing.csv --to feather`
- **THEN** un message mentionnant `missing.csv` est affiché sur la sortie d'erreur et le code de sortie est non nul

#### Scenario: Format inconnu
- **WHEN** l'utilisateur exécute `ia-convert data.csv --to zarr`
- **THEN** la commande indique que le format n'est pas disponible, liste les formats disponibles et se termine avec un code non nul
