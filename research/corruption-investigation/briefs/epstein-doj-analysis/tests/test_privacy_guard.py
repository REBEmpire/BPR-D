"""
Unit tests for PrivacyGuard.

CRITICAL: These tests verify that PrivacyGuard correctly detects
file creation and enforces the privacy guarantee.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.privacy_guard import PrivacyGuard


class TestPrivacyGuard:
    """Test suite for PrivacyGuard."""

    def test_initialization(self):
        """Test PrivacyGuard initializes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PrivacyGuard(watch_dir=tmpdir)

            assert guard.watch_dir == Path(tmpdir)
            assert isinstance(guard.initial_files, set)

    def test_no_files_created_passes(self):
        """Test that verification passes when no files are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PrivacyGuard(watch_dir=tmpdir)

            # Verify should pass - no files created
            result = guard.verify_no_files_created()
            assert result is True

    def test_detects_pdf_file_creation(self):
        """
        CRITICAL TEST: Verify PrivacyGuard detects PDF file creation.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PrivacyGuard(watch_dir=tmpdir)

            # Create a PDF file (PRIVACY VIOLATION)
            pdf_path = Path(tmpdir) / 'test.pdf'
            pdf_path.write_bytes(b'%PDF-1.4\nfake pdf content')

            # Verification should FAIL
            with pytest.raises(RuntimeError, match="Privacy violation"):
                guard.verify_no_files_created()

    def test_allows_log_files(self):
        """Test that log files are allowed (not considered violations)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PrivacyGuard(watch_dir=tmpdir)

            # Create a log file (ALLOWED)
            log_path = Path(tmpdir) / 'analysis.log'
            log_path.write_text('Log content here')

            # Verification should pass - log files are allowed
            result = guard.verify_no_files_created()
            assert result is True

    def test_allows_python_cache(self):
        """Test that Python cache files are allowed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PrivacyGuard(watch_dir=tmpdir)

            # Create Python cache (ALLOWED)
            pycache_dir = Path(tmpdir) / '__pycache__'
            pycache_dir.mkdir()
            (pycache_dir / 'test.pyc').write_bytes(b'compiled python')

            # Verification should pass
            result = guard.verify_no_files_created()
            assert result is True

    def test_detects_image_files(self):
        """Test that image files are detected (may contain document images)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PrivacyGuard(watch_dir=tmpdir)

            # Create an image file (SUSPICIOUS - could be from PDF)
            img_path = Path(tmpdir) / 'page1.jpg'
            img_path.write_bytes(b'fake image data')

            # Should be detected as violation
            with pytest.raises(RuntimeError, match="Privacy violation"):
                guard.verify_no_files_created()

    def test_pre_flight_check(self):
        """Test pre-flight check functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PrivacyGuard(watch_dir=tmpdir)

            # Should complete without errors
            guard.verify_no_local_storage_active()

    def test_comprehensive_verification(self):
        """Test comprehensive multi-layer verification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PrivacyGuard(watch_dir=tmpdir)

            # Run comprehensive check
            results = guard.comprehensive_verification()

            # Should pass all checks with no files created
            assert results['files_check'] is True
            assert results['overall_pass'] is True

    def test_comprehensive_verification_fails_on_pdf(self):
        """Test that comprehensive verification fails when PDF is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PrivacyGuard(watch_dir=tmpdir)

            # Create PDF (violation)
            pdf_path = Path(tmpdir) / 'document.pdf'
            pdf_path.write_bytes(b'%PDF-1.4\ncontent')

            # Comprehensive verification should fail
            results = guard.comprehensive_verification()

            assert results['files_check'] is False
            assert results['overall_pass'] is False

    def test_report_generation(self):
        """Test that privacy report generates correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PrivacyGuard(watch_dir=tmpdir)

            report = guard.get_report()

            # Report should be a string
            assert isinstance(report, str)

            # Should contain key sections
            assert 'PRIVACY VERIFICATION REPORT' in report
            assert 'Watch Directory' in report
            assert 'OVERALL' in report

    def test_detects_multiple_violations(self):
        """Test detection of multiple file violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PrivacyGuard(watch_dir=tmpdir)

            # Create multiple PDF files
            for i in range(3):
                pdf_path = Path(tmpdir) / f'doc{i}.pdf'
                pdf_path.write_bytes(b'%PDF content')

            # Should detect all violations
            with pytest.raises(RuntimeError, match="3 unexpected files"):
                guard.verify_no_files_created()

    def test_unexpected_file_classification(self):
        """Test the _is_unexpected_file method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PrivacyGuard(watch_dir=tmpdir)

            # PDF files are always unexpected
            assert guard._is_unexpected_file(Path('document.pdf')) is True

            # Log files are expected
            assert guard._is_unexpected_file(Path('app.log')) is False

            # Python cache is expected
            assert guard._is_unexpected_file(Path('__pycache__/module.pyc')) is False

            # Images are unexpected (could be from PDFs)
            assert guard._is_unexpected_file(Path('page1.jpg')) is True

            # New Python files are not unexpected (we're creating code)
            assert guard._is_unexpected_file(Path('core/new_module.py')) is False

    def test_temp_directory_check(self):
        """Test checking system temp directories for leaked PDFs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PrivacyGuard(watch_dir=tmpdir)

            # Check temp directories
            temp_pdfs = guard._check_temp_directories()

            # Should return a list (may be empty)
            assert isinstance(temp_pdfs, list)

    def test_memory_usage_tracking(self):
        """Test memory usage tracking (if psutil available)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PrivacyGuard(watch_dir=tmpdir)

            # Get memory usage
            mem_mb = guard.get_memory_usage_mb()

            # Should be a number (or 0 if psutil not available)
            assert isinstance(mem_mb, float)
            assert mem_mb >= 0


class TestPrivacyGuardIntegration:
    """Integration tests for PrivacyGuard with realistic scenarios."""

    def test_simulated_processing_session_clean(self):
        """Simulate a clean processing session with no file creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize guard
            guard = PrivacyGuard(watch_dir=tmpdir)

            # Pre-flight check
            guard.verify_no_local_storage_active()

            # Simulate processing (only allowed files)
            log_file = Path(tmpdir) / 'session.log'
            log_file.write_text('Processing started...\n')
            log_file.write_text('Processing complete.\n')

            # Verify privacy maintained
            result = guard.verify_no_files_created()
            assert result is True

            # Comprehensive verification
            results = guard.comprehensive_verification()
            assert results['overall_pass'] is True

    def test_simulated_processing_session_violation(self):
        """Simulate a processing session with privacy violation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize guard
            guard = PrivacyGuard(watch_dir=tmpdir)

            # Pre-flight check
            guard.verify_no_local_storage_active()

            # Simulate violation - PDF file created
            violation_file = Path(tmpdir) / 'downloaded.pdf'
            violation_file.write_bytes(b'%PDF-1.4\nThis should not exist')

            # Verify should fail
            with pytest.raises(RuntimeError, match="Privacy violation"):
                guard.verify_no_files_created()

    def test_full_session_with_report(self):
        """Test full session workflow with final report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PrivacyGuard(watch_dir=tmpdir)

            # Pre-flight
            guard.verify_no_local_storage_active()

            # Do some work (allowed files only)
            (Path(tmpdir) / 'analysis.log').write_text('Analysis log')
            (Path(tmpdir) / '__pycache__').mkdir()

            # Generate report
            report = guard.get_report()

            # Report should show pass
            assert '✓ PASS' in report
            assert 'OVERALL: ✓ PASS' in report


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, '-v'])
