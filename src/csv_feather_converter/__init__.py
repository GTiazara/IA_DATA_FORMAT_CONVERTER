"""Package for converting files between CSV and Feather formats."""
from .convert import convert, csv_to_feather, feather_to_csv
from .main import main

__all__ = ['convert', 'csv_to_feather', 'feather_to_csv', 'main']
