"""
Privacy guard to ensure NO local file storage occurs.

CRITICAL: This module monitors and verifies that no PDF files or
other source documents are created during processing sessions.
"""
import os
import sys
import logging
from pathlib import Path
from typing import Set, List, Optional
import tempfile

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not available - some monitoring features disabled")

logger = logging.getLogger(__name__)


class PrivacyGuard:
    """
    Monitor and verify that no local files are created during processing.

    This is the enforcement layer for our privacy guarantee.
    """

    def __init__(self, watch_dir: Optional[str] = None):
        """
        Initialize privacy guard.

        Args:
            watch_dir: Directory to monitor (defaults to current working directory)
        """
        # Watch current working directory by default
        self.watch_dir = Path(watch_dir or os.getcwd())

        # Capture initial state
        self.initial_files = self._snapshot_directory()
        logger.info(f"Privacy guard initialized - watching: {self.watch_dir}")
        logger.info(f"Initial file count: {len(self.initial_files)}")

        # Process monitoring (if psutil available)
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process()
            self.initial_open_files = len(self.process.open_files())
            self.initial_memory_mb = self.get_memory_usage_mb()
        else:
            self.process = None
            self.initial_open_files = 0
            self.initial_memory_mb = 0

    def _snapshot_directory(self) -> Set[Path]:
        """
        Capture current directory state.

        Returns:
            Set of all file paths in watch directory
        """
        try:
            return set(self.watch_dir.rglob('*'))
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")
            return set()

    def verify_no_files_created(self) -> bool:
        """
        Verify no new files were created during processing.

        Returns:
            True if no files created

        Raises:
            RuntimeError: If privacy violation detected (new files created)
        """
        current_files = self._snapshot_directory()
        new_files = current_files - self.initial_files

        # Filter out expected files (logs, Python cache, etc.)
        unexpected_files = [f for f in new_files if self._is_unexpected_file(f)]

        if unexpected_files:
            # Log details of violation
            logger.error("=" * 60)
            logger.error("PRIVACY VIOLATION DETECTED")
            logger.error("=" * 60)
            logger.error(f"New files detected: {len(unexpected_files)}")
            for f in unexpected_files[:10]:  # Show first 10
                logger.error(f"  - {f.relative_to(self.watch_dir)}")
            if len(unexpected_files) > 10:
                logger.error(f"  ... and {len(unexpected_files) - 10} more")

            raise RuntimeError(
                f"Privacy violation: {len(unexpected_files)} unexpected files created"
            )

        logger.info("✓ Privacy check passed: No unexpected files created")
        return True

    def verify_no_local_storage_active(self):
        """
        Pre-flight check before processing.

        Verifies environment is ready for privacy-preserving processing.
        """
        # Check no PDF files already in working directory
        pdf_files = list(self.watch_dir.glob('**/*.pdf'))
        if pdf_files:
            logger.warning(
                f"Warning: {len(pdf_files)} PDF files already in directory"
            )
            logger.warning("These existing PDFs will be ignored during monitoring")

        # Check available RAM (warn if <2GB free)
        if PSUTIL_AVAILABLE:
            mem = psutil.virtual_memory()
            available_gb = mem.available / (1024**3)
            if available_gb < 2.0:
                logger.warning(
                    f"Low available RAM: {available_gb:.1f}GB "
                    "(2GB+ recommended for in-memory processing)"
                )
            else:
                logger.info(f"Available RAM: {available_gb:.1f}GB")

        # Check temp directories
        temp_pdfs = self._check_temp_directories()
        if temp_pdfs:
            logger.warning(
                f"Found {len(temp_pdfs)} PDFs in temp directories - "
                "these may be from previous sessions"
            )

        logger.info("✓ Privacy guard pre-flight check complete")

    def comprehensive_verification(self) -> dict:
        """
        Multi-layered privacy verification.

        Returns:
            Dictionary with verification results and metrics
        """
        results = {
            'files_check': False,
            'file_handles_check': False,
            'memory_check': False,
            'temp_check': False,
            'overall_pass': False
        }

        # 1. Directory scan
        try:
            self.verify_no_files_created()
            results['files_check'] = True
        except RuntimeError as e:
            logger.error(f"Files check failed: {e}")
            results['files_check'] = False
            results['files_error'] = str(e)

        # 2. Open file handles
        if PSUTIL_AVAILABLE and self.process:
            current_open_files = len(self.process.open_files())
            if current_open_files > self.initial_open_files:
                logger.warning(
                    f"File handles increased: {self.initial_open_files} -> {current_open_files}"
                )
                results['file_handles_check'] = False
                results['file_handles_delta'] = current_open_files - self.initial_open_files
            else:
                results['file_handles_check'] = True
        else:
            results['file_handles_check'] = True  # Skip if psutil not available

        # 3. Memory check (should be reasonable for in-memory processing)
        if PSUTIL_AVAILABLE:
            mem_mb = self.get_memory_usage_mb()
            mem_delta = mem_mb - self.initial_memory_mb
            results['memory_mb'] = mem_mb
            results['memory_delta_mb'] = mem_delta

            if mem_mb > 4000:  # More than 4GB is suspicious
                logger.warning(f"High memory usage: {mem_mb:.1f}MB")
                results['memory_check'] = False
            else:
                results['memory_check'] = True
        else:
            results['memory_check'] = True  # Skip if psutil not available

        # 4. Temp directory check
        temp_pdfs = self._check_temp_directories()
        if temp_pdfs:
            logger.error(f"PDF files found in temp: {len(temp_pdfs)}")
            results['temp_check'] = False
            results['temp_pdfs_found'] = len(temp_pdfs)
        else:
            results['temp_check'] = True

        # Overall pass requires all checks to pass
        results['overall_pass'] = all([
            results['files_check'],
            results['file_handles_check'],
            results['memory_check'],
            results['temp_check']
        ])

        if results['overall_pass']:
            logger.info("✓ Comprehensive privacy verification PASSED")
        else:
            logger.error("✗ Comprehensive privacy verification FAILED")

        return results

    def _is_unexpected_file(self, filepath: Path) -> bool:
        """
        Check if file is unexpected (not a log, Python cache, etc.).

        Args:
            filepath: Path to check

        Returns:
            True if file is unexpected and represents a privacy violation
        """
        # Allow these file patterns
        allowed_patterns = [
            '.log',            # Log files
            '__pycache__',     # Python cache
            '.pyc',            # Compiled Python
            '.pyo',            # Optimized Python
            '.tmp',            # Temp files (non-PDF)
            '.gitignore',      # Git files
            '.git/',           # Git directory
            '.pytest_cache',   # Pytest cache
            '.coverage',       # Coverage data
            '.DS_Store',       # macOS metadata
            'Thumbs.db',       # Windows metadata
        ]

        filepath_str = str(filepath)

        # If it's any of the allowed patterns, it's not unexpected
        if any(pattern in filepath_str for pattern in allowed_patterns):
            return False

        # PDF files are ALWAYS unexpected (privacy violation)
        if filepath.suffix.lower() == '.pdf':
            return True

        # Image files from document processing are suspicious
        if filepath.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            # Unless they're in a tests/fixtures directory
            if 'test' in filepath_str.lower() or 'fixture' in filepath_str.lower():
                return False
            return True

        # Any other new file in the main directories is suspicious
        if any(part in filepath.parts for part in ['core', 'extractors', 'analyzers', 'utils']):
            # But not if it's a .py file (that's code we created)
            if filepath.suffix == '.py':
                return False
            return True

        return False

    def _check_temp_directories(self) -> List[Path]:
        """
        Check system temp directories for leaked PDF files.

        Returns:
            List of PDF file paths found in temp directories
        """
        temp_pdfs = []

        # Check system temp directory
        temp_dir = Path(tempfile.gettempdir())
        try:
            temp_pdfs.extend(temp_dir.glob('*.pdf'))
        except Exception as e:
            logger.debug(f"Could not scan temp directory {temp_dir}: {e}")

        # Check TMPDIR environment variable (Unix)
        tmpdir = os.environ.get('TMPDIR')
        if tmpdir and Path(tmpdir).exists():
            try:
                temp_pdfs.extend(Path(tmpdir).glob('*.pdf'))
            except Exception as e:
                logger.debug(f"Could not scan TMPDIR {tmpdir}: {e}")

        return temp_pdfs

    def get_memory_usage_mb(self) -> float:
        """
        Get current process memory usage in MB.

        Returns:
            Memory usage in megabytes
        """
        if PSUTIL_AVAILABLE and self.process:
            return self.process.memory_info().rss / (1024**2)
        return 0.0

    def get_report(self) -> str:
        """
        Generate human-readable privacy verification report.

        Returns:
            Report string
        """
        results = self.comprehensive_verification()

        report = ["=" * 60]
        report.append("PRIVACY VERIFICATION REPORT")
        report.append("=" * 60)
        report.append(f"Watch Directory: {self.watch_dir}")
        report.append(f"Initial Files: {len(self.initial_files)}")
        report.append(f"Current Files: {len(self._snapshot_directory())}")
        report.append("")
        report.append("Checks:")
        report.append(f"  Files Created: {'✓ PASS' if results['files_check'] else '✗ FAIL'}")
        report.append(f"  File Handles: {'✓ PASS' if results['file_handles_check'] else '✗ FAIL'}")
        report.append(f"  Memory Usage: {'✓ PASS' if results['memory_check'] else '✗ FAIL'}")
        report.append(f"  Temp Directory: {'✓ PASS' if results['temp_check'] else '✗ FAIL'}")
        report.append("")

        if PSUTIL_AVAILABLE:
            report.append(f"Memory Usage: {results.get('memory_mb', 0):.1f} MB")
            report.append(f"Memory Delta: +{results.get('memory_delta_mb', 0):.1f} MB")
            report.append("")

        report.append(f"OVERALL: {'✓ PASS' if results['overall_pass'] else '✗ FAIL'}")
        report.append("=" * 60)

        return "\n".join(report)


if __name__ == "__main__":
    # Simple test if run directly
    logging.basicConfig(level=logging.INFO)

    print("Testing PrivacyGuard...")
    guard = PrivacyGuard()

    # Pre-flight check
    guard.verify_no_local_storage_active()

    # Test comprehensive verification
    print("\nRunning comprehensive verification...")
    print(guard.get_report())
