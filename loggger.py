import logging
from logging.handlers import RotatingFileHandler

# Configure logger
def setup_logger(log_file='audit_logs.log'):
    logger = logging.getLogger('AuditLogger')
    logger.setLevel(logging.INFO)

    # Rotating file handler (5 MB max, 5 backups)
    handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s - %(IP)s - %(Device)s'
    )
    handler.setFormatter(formatter)

    # Add default values for extra keys
    class DefaultFilter(logging.Filter):
        def filter(self, record):
            record.Username = getattr(record, 'Username', 'Unknown')
            record.IP = getattr(record, 'IP', 'Unknown')
            record.Device = getattr(record, 'Device', 'Unknown')
            return True

    handler.addFilter(DefaultFilter())

    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(handler)

    return logger



# Instantiate the logger
logger = setup_logger()