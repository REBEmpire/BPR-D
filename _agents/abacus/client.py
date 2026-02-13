import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_client():
    """
    Returns an authenticated Abacus.AI client using credentials from environment variables.
    Tries ABACUS_PRIMARY_KEY first, then ABACUS_BACKUP_KEY.
    """
    try:
        from abacusai import AbacusApi
    except ImportError:
        raise ImportError(
            "The 'abacusai' package is required. Install it with: pip install abacusai"
        )

    api_key = os.getenv("ABACUS_PRIMARY_KEY")
    if not api_key:
        api_key = os.getenv("ABACUS_BACKUP_KEY")

    if not api_key:
        raise ValueError(
            "No Abacus API key found. Please set ABACUS_PRIMARY_KEY or ABACUS_BACKUP_KEY in your .env file."
        )

    return AbacusApi(api_key=api_key)

if __name__ == "__main__":
    try:
        client = get_client()
        print("Abacus client initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize client: {e}")
