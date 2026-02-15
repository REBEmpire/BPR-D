# Setup Guide
## DOJ Epstein Document Analysis System

Complete setup instructions for Research Focus Project #1.

---

## Prerequisites

- Python 3.9 or higher
- Hugging Face account (free): https://huggingface.co/join
- 4GB+ RAM recommended for in-memory PDF processing
- Git (for version control)

---

## Step 1: Environment Setup

### 1.1 Create Virtual Environment

```bash
cd research/corruption-investigation/briefs/epstein-doj-analysis

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 1.2 Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_lg
```

### 1.3 Configure Environment Variables

```bash
# Copy template
cp .env.template .env

# Edit .env file with your information
# Required:
#   - HF_TOKEN: Get from https://huggingface.co/settings/tokens
#   - HF_DATASET_REPO: Your dataset repo name (e.g., username/epstein-docs)
```

**Important:** Never commit `.env` file to git (already in `.gitignore`)

---

## Step 2: Hugging Face Setup

### 2.1 Create HF Account & Token

1. Sign up at: https://huggingface.co/join
2. Go to: https://huggingface.co/settings/tokens
3. Click "New token"
4. Token type: "Write" (to push dataset updates)
5. Copy token to `.env` file (`HF_TOKEN=...`)

### 2.2 Initialize Private Dataset

```bash
# Run initialization script
python scripts/init_hf_dataset.py

# Follow prompts to enter your repository name
# Example: your-username/epstein-docs-analysis

# Or provide repo name directly
python scripts/init_hf_dataset.py --repo your-username/epstein-docs-analysis
```

This creates a **PRIVATE** dataset on HF Hub with 9 tables.

### 2.3 Verify Dataset Created

Visit: `https://huggingface.co/datasets/your-username/epstein-docs-analysis`

---

## Step 3: Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=core --cov=utils
```

**Expected: All tests PASS ✓**

---

## Next Steps

Phase 0 complete! Ready for Phase 1 implementation.

See `README.md` for full documentation.
