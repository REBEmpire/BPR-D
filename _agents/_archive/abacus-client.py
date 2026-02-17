import os
import logging
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logger (do not call basicConfig in a module)
logger = logging.getLogger(__name__)

# Abacus.AI SDK Configuration
# Note: Keys should be set via environment variables (e.g., in .env):
# ABACUS_PRIMARY_KEY
# ABACUS_BACKUP_KEY

PRIMARY_KEY = os.environ.get("ABACUS_PRIMARY_KEY")
BACKUP_KEY = os.environ.get("ABACUS_BACKUP_KEY")

try:
    from abacusai import ApiClient
    SDK_INSTALLED = True
except ImportError:
    ApiClient = None
    SDK_INSTALLED = False

def get_client(api_key=None, use_backup=False):
    """
    Initializes and returns the Abacus.AI client.

    :param api_key: Optional API key to override environment variables.
    :param use_backup: If True, uses the backup key if api_key is not provided.
    :return: An instance of ApiClient.
    :raises ImportError: If the abacusai package is not installed.
    :raises ValueError: If no API key is available.
    """
    if not SDK_INSTALLED:
        logger.error("abacusai Python SDK is not installed.")
        raise ImportError("abacusai package not found. Please run: pip install -r requirements.txt")

    if api_key is None:
        api_key = BACKUP_KEY if use_backup else PRIMARY_KEY

    if not api_key:
        logger.error("No Abacus API key found in environment variables.")
        raise ValueError("Missing ABACUS_PRIMARY_KEY or ABACUS_BACKUP_KEY environment variable.")

    return ApiClient(api_key=api_key)

if __name__ == "__main__":
    # For testing purposes only
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print("--- Abacus.AI SDK Configuration Check ---")
    print(f"SDK Installed: {SDK_INSTALLED}")
    print(f"Primary Key in Env: {'Yes' if PRIMARY_KEY else 'No'}")
    print(f"Backup Key in Env:  {'Yes' if BACKUP_KEY else 'No'}")

    if SDK_INSTALLED:
        if PRIMARY_KEY or BACKUP_KEY:
            logger.info("Configuration looks correct. SDK is present and keys are available.")
        else:
            logger.warning("SDK is present but keys are missing from environment.")
    else:
        logger.warning("SDK is missing. Run 'pip install -r requirements.txt'")
