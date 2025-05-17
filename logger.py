# logger.py

import logging
import os

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("toolkit.log"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("pentest_logger")


def setup_logger(
    name: str = "pentest-toolkit",
    log_file: str = "pentest.log",
    level: int = logging.DEBUG,
    console_level: int = logging.WARNING
) -> logging.Logger:
    """
    Set up and return a logger with both file and console handlers.

    Args:
        name (str): Logger name.
        log_file (str): Path to the log file.
        level (int): Logging level for the file handler.
        console_level (int): Logging level for the console handler.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.hasHandlers():
        # Avoid adding multiple handlers if already configured
        return logger

    # Create file handler for detailed logs
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)

    # Create console handler for warnings and above by default
    ch = logging.StreamHandler()
    ch.setLevel(console_level)

    # Define a consistent log format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

# ✅ Create a default logger instance to be imported elsewhere
logger = setup_logger()
