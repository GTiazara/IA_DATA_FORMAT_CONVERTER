"""Main entry point for CSV <-> Feather conversion."""
import logging
import sys
from pathlib import Path
from typing import Optional

from omegaconf import OmegaConf

from csv_feather_converter.convert import convert

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main(config_path: Optional[str] = None):
    """
    Convert a file between CSV and Feather formats based on configuration.

    Args:
        config_path: Path to configuration file. If None, expects config as command line argument.
    """
    if config_path is None:
        if len(sys.argv) < 2:
            logger.error("Usage: csv-feather-convert <config.yaml>")
            sys.exit(1)
        config_path = sys.argv[1]

    if not Path(config_path).exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)

    config = OmegaConf.load(config_path)

    for field in ['input_file', 'output_file']:
        if field not in config:
            logger.error(f"Missing required configuration field: {field}")
            sys.exit(1)

    try:
        convert(
            input_file=config.input_file,
            output_file=config.output_file,
            direction=config.get('direction', None),
            delimiter=config.get('delimiter', ','),
            encoding=config.get('encoding', 'utf8'),
            compression=config.get('compression', 'zstd'),
            include_header=config.get('include_header', True),
        )
        logger.info("Conversion completed successfully!")
    except Exception as e:
        logger.error(f"Error during conversion: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
