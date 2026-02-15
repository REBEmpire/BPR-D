"""
Initialize Hugging Face dataset with proper schema.

Run ONCE at project start to create the private HF dataset.

Usage:
    python scripts/init_hf_dataset.py [--repo your-username/repo-name]
"""
import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datasets import Dataset, DatasetDict
from huggingface_hub import login, create_repo, HfApi
from config.hf_config import HFConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_dataset(repo_name: str = None, token: str = None):
    """
    Initialize Hugging Face dataset with schema.

    Args:
        repo_name: HF repository name (default from config)
        token: HF authentication token (default from env)
    """
    # Use config defaults if not provided
    repo_name = repo_name or HFConfig.DEFAULT_REPO
    token = token or HFConfig.HF_TOKEN

    if not token:
        logger.error("No HF token provided. Please set HF_TOKEN environment variable.")
        logger.error("You can get a token from: https://huggingface.co/settings/tokens")
        sys.exit(1)

    # Login to HF
    logger.info("Logging in to Hugging Face...")
    try:
        login(token=token)
        logger.info("✓ Login successful")
    except Exception as e:
        logger.error(f"Login failed: {e}")
        sys.exit(1)

    # Create repository if it doesn't exist
    logger.info(f"Creating repository: {repo_name}")
    try:
        api = HfApi()
        create_repo(
            repo_id=repo_name,
            repo_type='dataset',
            private=HFConfig.PRIVATE,
            token=token,
            exist_ok=True
        )
        logger.info("✓ Repository created/verified")
    except Exception as e:
        logger.error(f"Failed to create repository: {e}")
        sys.exit(1)

    # Get all schemas
    all_features = HFConfig.get_all_features()
    logger.info(f"Creating {len(all_features)} tables...")

    # Create empty datasets for each table
    dataset_dict = {}
    for table_name, features in all_features.items():
        logger.info(f"  Creating table: {table_name}")
        # Create empty dataset with schema
        empty_dataset = Dataset.from_dict({}, features=features)
        dataset_dict[table_name] = empty_dataset

    # Wrap in DatasetDict
    dataset = DatasetDict(dataset_dict)

    # Push to HF Hub
    logger.info(f"Pushing dataset to HF Hub: {repo_name}")
    try:
        dataset.push_to_hub(
            repo_name,
            private=HFConfig.PRIVATE,
            token=token
        )
        logger.info("✓ Dataset pushed successfully")
    except Exception as e:
        logger.error(f"Failed to push dataset: {e}")
        sys.exit(1)

    # Verify it worked
    logger.info("Verifying dataset...")
    try:
        from datasets import load_dataset
        loaded = load_dataset(repo_name, token=token)
        logger.info(f"✓ Dataset verified - {len(loaded)} tables created:")
        for table_name in loaded.keys():
            logger.info(f"    - {table_name}")
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        sys.exit(1)

    # Success!
    logger.info("")
    logger.info("=" * 60)
    logger.info("SUCCESS!")
    logger.info("=" * 60)
    logger.info(f"Dataset initialized: https://huggingface.co/datasets/{repo_name}")
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Update HF_DATASET_REPO in .env file with your repo name")
    logger.info("2. Run tests: pytest tests/")
    logger.info("3. Start processing: python scripts/run_session.py")
    logger.info("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Initialize Hugging Face dataset for Epstein document analysis'
    )
    parser.add_argument(
        '--repo',
        type=str,
        default=None,
        help='HF repository name (e.g., your-username/epstein-docs-analysis)'
    )
    parser.add_argument(
        '--token',
        type=str,
        default=None,
        help='HF authentication token (or use HF_TOKEN env var)'
    )

    args = parser.parse_args()

    # If repo not provided, prompt user
    if not args.repo:
        print("=" * 60)
        print("Hugging Face Dataset Initialization")
        print("=" * 60)
        print()
        print("This script will create a PRIVATE dataset on Hugging Face Hub")
        print("to store analysis results (NOT source documents).")
        print()

        repo_input = input("Enter your HF repository name (e.g., username/epstein-docs): ").strip()
        if not repo_input:
            print("Error: Repository name required")
            sys.exit(1)
        args.repo = repo_input

    init_dataset(repo_name=args.repo, token=args.token)


if __name__ == "__main__":
    main()
