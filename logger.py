import logging
from pathlib import Path
from datetime import datetime

# Define the log format
# _LOG_FORMAT = f"%(asctime)s - [%(levelname)s] - %(name)s -> %(message)s"
_LOG_FORMAT = (
    "%(asctime)s - [%(levelname)s] - %(name)s - "
    "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
)
LOGFOLDER = "log"


def create_log_folder(log_dir: str) -> None:
    """
    Creates a log directory if it doesn't already exist.

    :param log_dir: The path to the log directory.
    :raises RuntimeError: If the directory creation fails.
    """
    try:
        log_path = Path(log_dir)
        if not log_path.exists():
            log_path.mkdir(parents=True, exist_ok=True)
            logging.info("Created log directory: %s", log_dir)
        else:
            logging.info("Log directory already exists: %s", log_dir)
    except Exception as e:
        raise RuntimeError(
            f"Failed to create log directory: {log_dir}. Error: {str(e)}"
        )


def get_file_handler() -> logging.FileHandler:
    """
    Creates a file handler for logging to a file with a timestamp in
    the filename.

    :return: A logging FileHandler instance.
    """
    create_log_folder(LOGFOLDER)

    # Generate a timestamp for the log filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"application_{timestamp}.log"

    file_handler = logging.FileHandler(Path(LOGFOLDER) / log_filename)
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    logging.debug(
        "File handler created for logging to %s", file_handler.baseFilename
    )
    return file_handler


def get_stream_handler() -> logging.StreamHandler:
    """
    Creates a stream handler for logging to the console.

    :return: A logging StreamHandler instance.
    """
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    logging.debug("Stream handler created for console logging.")
    return stream_handler


def get_logger(name: str) -> logging.Logger:
    """
    Creates or retrieves a logger with the specified name, adding file and
    stream handlers.

    :param name: The name of the logger.
    :return: A logging Logger instance.
    """
    logger = logging.getLogger(name)

    # Only add handlers if none exist
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.addHandler(get_file_handler())
        logger.addHandler(get_stream_handler())
        logging.debug("Logger '%s' created and handlers added.", name)

    return logger
