# Spec Delta

## Purpose

Convertir des données tabulaires fournies en CSV vers un format de stockage binaire adapté aux usages machine learning et IA, en commençant par Feather et en permettant l'ajout d'autres formats de sortie.

## ADDED Requirements

### Requirement: Conversion CSV vers Feather
Le système SHALL lire un fichier CSV tabulaire avec une ligne d'en-tête et écrire un fichier Feather (Arrow IPC v2) contenant les mêmes colonnes, dans le même ordre, et le même nombre de lignes.

#### Scenario: Conversion réussie
- **WHEN** un CSV valide de 3 colonnes et 100 lignes est converti vers `feather`
- **THEN** un fichier Feather est créé, lisible par une bibliothèque Arrow standard, avec les 3 colonnes dans l'ordre d'origine et 100 lignes

#### Scenario: Valeurs préservées
- **WHEN** le Feather produit est relu
- **THEN** les valeurs de chaque cellule correspondent à celles du CSV source

### Requirement: Inférence des types de colonnes
Le système SHALL inférer le type de chaque colonne (entier, flottant, booléen, chaîne, date/heure) et le conserver dans la sortie. Les cellules vides SHALL être représentées comme valeurs nulles.

#### Scenario: Colonnes numériques typées
- **WHEN** une colonne ne contient que des entiers et une autre que des décimaux
- **THEN** la sortie contient respectivement une colonne entière et une colonne flottante

#### Scenario: Cellules vides
- **WHEN** une cellule d'une colonne numérique est vide
- **THEN** la valeur correspondante dans la sortie est nulle et le type de la colonne reste numérique

### Requirement: Options de lecture CSV
Le système SHALL permettre de préciser le séparateur de champs (par défaut `,`) et l'encodage du fichier (par défaut UTF-8).

#### Scenario: Séparateur point-virgule
- **WHEN** un CSV utilisant `;` est converti avec le séparateur `;`
- **THEN** les colonnes sont correctement séparées dans la sortie

#### Scenario: Encodage non UTF-8
- **WHEN** un CSV encodé en Latin-1 contenant des caractères accentués est converti avec l'encodage `latin-1`
- **THEN** les caractères accentués sont correctement restitués dans la sortie

### Requirement: Compression Feather
Le système SHALL permettre de choisir la compression du fichier Feather parmi `lz4` (par défaut), `zstd` et `uncompressed`.

#### Scenario: Compression choisie
- **WHEN** la conversion est demandée avec la compression `zstd`
- **THEN** le fichier Feather produit est compressé en zstd et reste lisible

#### Scenario: Compression invalide
- **WHEN** une compression non supportée est demandée
- **THEN** la conversion échoue avec une erreur nommant la valeur invalide et les valeurs acceptées, sans créer de fichier de sortie

### Requirement: Formats de sortie enregistrés
Le système SHALL exposer la liste des formats de sortie disponibles, identifiés par un nom, et SHALL refuser un format inconnu. Dans cette version, seul `feather` est disponible.

#### Scenario: Liste des formats
- **WHEN** la liste des formats disponibles est demandée
- **THEN** elle contient `feather`

#### Scenario: Format inconnu
- **WHEN** une conversion est demandée vers `parquet` alors qu'il n'est pas encore disponible
- **THEN** la conversion échoue avec une erreur indiquant le format inconnu et les formats disponibles, sans créer de fichier

### Requirement: Protection de la sortie existante
Le système SHALL refuser d'écrire sur un fichier de sortie existant, sauf si l'écrasement est explicitement autorisé.

#### Scenario: Sortie existante sans autorisation
- **WHEN** le fichier de sortie existe déjà et l'écrasement n'est pas autorisé
- **THEN** la conversion échoue avec une erreur et le fichier existant reste inchangé

#### Scenario: Sortie existante avec autorisation
- **WHEN** le fichier de sortie existe déjà et l'écrasement est autorisé
- **THEN** le fichier est remplacé par le résultat de la conversion

### Requirement: Erreurs d'entrée explicites
Le système SHALL signaler une erreur claire, sans laisser de fichier de sortie partiel, lorsque le fichier d'entrée est absent, vide ou mal formé.

#### Scenario: Fichier d'entrée absent
- **WHEN** le chemin d'entrée n'existe pas
- **THEN** la conversion échoue avec une erreur mentionnant le chemin

#### Scenario: CSV mal formé
- **WHEN** une ligne du CSV contient un nombre de champs différent de l'en-tête
- **THEN** la conversion échoue avec une erreur et aucun fichier de sortie n'est laissé
