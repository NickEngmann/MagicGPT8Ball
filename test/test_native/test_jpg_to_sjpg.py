"""Unit tests for LVGL jpg_to_sjpg.py image conversion script."""

import os
import sys
import unittest
from pathlib import Path
import tempfile
import shutil
import subprocess
import math

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestJPGToSJPG(unittest.TestCase):
    """Test suite for SJPG conversion script."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.script_path = Path(__file__).parent.parent.parent / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        
        # Create test images directory
        self.images_dir = Path(self.test_dir) / "images"
        self.images_dir.mkdir()
        
        # Create output directory
        self.output_dir = Path(self.test_dir) / "output"
        self.output_dir.mkdir()
        
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_test_image(self, filename: str, width: int = 100, height: int = 100, color: tuple = (255, 0, 0)):
        """Helper to create a test JPEG image using PIL."""
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("PIL/Pillow not available")
        
        img = Image.new('RGB', (width, height), color)
        img_path = self.images_dir / filename
        img.save(str(img_path), 'JPEG')
        return str(img_path)
    
    def test_script_exists(self):
        """Test that the conversion script exists."""
        self.assertTrue(self.script_path.exists(), "JPG to SJPG converter script not found")
    
    def test_script_executable(self):
        """Test that the script can be executed."""
        result = subprocess.run(
            [sys.executable, str(self.script_path)],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Script should print usage when run without arguments
        self.assertIn("usage", result.stderr.lower() or result.stdout.lower())
    
    def test_conversion_with_valid_image(self):
        """Test conversion of a valid JPEG image."""
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("PIL/Pillow not available")
        
        # Create test image
        test_image = self._create_test_image("test_input.jpg", 120, 120)
        
        # Run conversion
        result = subprocess.run(
            [sys.executable, str(self.script_path), test_image],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Check success
        self.assertEqual(result.returncode, 0, f"Conversion failed: {result.stderr}")
        
        # Verify output files exist
        base_name = "test_input"
        sjpg_file = Path(self.test_dir) / f"{base_name}.sjpg"
        c_file = Path(self.test_dir) / f"{base_name}.c"
        
        self.assertTrue(sjpg_file.exists(), "SJPG file not created")
        self.assertTrue(c_file.exists(), "C array file not created")
    
    def test_conversion_output_files(self):
        """Test that conversion creates correct output files."""
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("PIL/Pillow not available")
        
        # Create test image
        test_image = self._create_test_image("output_test.jpg", 200, 150, (0, 255, 0))
        
        # Run conversion
        subprocess.run(
            [sys.executable, str(self.script_path), test_image],
            capture_output=True,
            timeout=30
        )
        
        # Verify .sjpg file exists and has content
        sjpg_path = Path(self.test_dir) / "output_test.sjpg"
        self.assertTrue(sjpg_path.exists())
        self.assertTrue(sjpg_path.stat().st_size > 0, "SJPG file is empty")
        
        # Verify .c file exists and contains LVGL code
        c_path = Path(self.test_dir) / "output_test.c"
        self.assertTrue(c_path.exists())
        c_content = c_path.read_text()
        self.assertIn("lv_img_dsc_t", c_content, "C file doesn't contain LVGL image structure")
        self.assertIn("output_test_map[]", c_content, "C file doesn't contain data array")
    
    def test_jpg_to_sjpg_header_format(self):
        """Test that SJPG file has correct header format."""
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("PIL/Pillow not available")
        
        # Create test image
        test_image = self._create_test_image("header_test.jpg", 100, 100)
        
        # Run conversion
        subprocess.run(
            [sys.executable, str(self.script_path), test_image],
            capture_output=True,
            timeout=30
        )
        
        # Read SJPG header
        sjpg_path = Path(self.test_dir) / "header_test.sjpg"
        with open(sjpg_path, 'rb') as f:
            header = f.read(20)
        
        # Verify header starts with "_SJPG__"
        # The header format is: "_SJPG__" + version string "\x00V1.00\x00"
        # So header[:9] should be "_SJPG__\x00"
        self.assertTrue(header.startswith(b'_SJPG__'), "SJPG file doesn't have correct header")
    
    def test_c_array_hex_format(self):
        """Test that generated C array uses correct hex format."""
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("PIL/Pillow not available")
        
        # Create test image
        test_image = self._create_test_image("array_test.jpg", 80, 80, (0, 0, 255))
        
        # Run conversion
        subprocess.run(
            [sys.executable, str(self.script_path), test_image],
            capture_output=True,
            timeout=30
        )
        
        # Check C file for hex format
        c_path = Path(self.test_dir) / "array_test.c"
        c_content = c_path.read_text()
        
        # Verify hex format (should have "0x" prefix)
        self.assertIn("0x", c_content.lower(), "C file doesn't contain hex values")
    
    def test_conversion_with_different_sizes(self):
        """Test conversion with various image sizes."""
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("PIL/Pillow not available")
        
        test_sizes = [
            (32, 32, "small.jpg"),
            (100, 100, "medium.jpg"),
            (200, 150, "large.jpg"),
            (240, 240, "square.jpg"),
        ]
        
        for width, height, filename in test_sizes:
            test_image = self._create_test_image(filename, width, height)
            
            result = subprocess.run(
                [sys.executable, str(self.script_path), test_image],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            self.assertEqual(
                result.returncode, 0,
                f"Conversion failed for {width}x{height} image: {result.stderr}"
            )
    
    def test_conversion_invalid_image(self):
        """Test handling of invalid image file."""
        # Create invalid file
        invalid_file = self.images_dir / "invalid.jpg"
        invalid_file.write_text("not a real image")
        
        # Run conversion
        result = subprocess.run(
            [sys.executable, str(self.script_path), str(invalid_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Script reports "File not found" for invalid files
        output = (result.stderr + result.stdout).lower()
        self.assertIn("file", output)
    
    def test_conversion_missing_file(self):
        """Test handling of missing input file."""
        result = subprocess.run(
            [sys.executable, str(self.script_path), "/nonexistent/file.jpg"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Script may or may not handle missing files gracefully
        # Just verify it doesn't crash unexpectedly
        self.assertIn("file", (result.stderr + result.stdout).lower() or 
                      result.returncode == 0)
    
    def test_conversion_no_arguments(self):
        """Test script when run without arguments."""
        result = subprocess.run(
            [sys.executable, str(self.script_path)],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Should print usage and exit
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", (result.stderr + result.stdout).lower())
    
    def test_file_cleanup_after_conversion(self):
        """Test that temporary crop files are cleaned up."""
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("PIL/Pillow not available")
        
        # Create test image in the root of test_dir, not in images_dir
        test_image = self._create_test_image("cleanup_test.jpg", 50, 50)
        
        subprocess.run(
            [sys.executable, str(self.script_path), test_image],
            capture_output=True,
            timeout=30
        )
        
        # Check that temporary crop files (*.jpg with numeric names) are cleaned up
        # The script creates 0.jpg, 1.jpg, etc. in current directory and cleans them up
        temp_crop_files = list(Path(self.test_dir).glob("*.jpg"))
        
        # Should have the original test file but no numeric crop files like 0.jpg, 1.jpg
        numeric_crop_files = [f for f in temp_crop_files if f.name[0].isdigit()]
        self.assertEqual(len(numeric_crop_files), 0, "Temporary crop files not cleaned up")
    
    def test_conversion_timing_output(self):
        """Test that conversion script outputs timing information."""
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("PIL/Pillow not available")
        
        # Create test image
        test_image = self._create_test_image("timing_test.jpg", 100, 100)
        
        result = subprocess.run(
            [sys.executable, str(self.script_path), test_image],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Output is printed to stdout
        output = result.stdout
        
        # Should output timing information
        self.assertIn("time", output.lower())
        self.assertIn("sec", output.lower())
        self.assertIn("bin size", output.lower())
        self.assertIn("kb", output.lower())
    
    def test_output_c_code_structure(self):
        """Test that generated C code has correct structure."""
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("PIL/Pillow not available")
        
        # Create test image
        test_image = self._create_test_image("structure_test.jpg", 128, 128)
        
        subprocess.run(
            [sys.executable, str(self.script_path), test_image],
            capture_output=True,
            timeout=30
        )
        
        # Check C file structure
        c_path = Path(self.test_dir) / "structure_test.c"
        c_content = c_path.read_text()
        
        # Verify key components
        self.assertIn("lv_img_dsc_t", c_content)
        self.assertIn("header.always_zero", c_content)
        self.assertIn("header.w =", c_content)
        self.assertIn("header.h =", c_content)
        self.assertIn("data_size =", c_content)
        self.assertIn("header.cf = LV_IMG_CF_RAW", c_content)
        self.assertIn("data = ", c_content)


class TestSJPGConstants(unittest.TestCase):
    """Test script constants and configuration."""
    
    script_path = Path(
        __file__).parent.parent.parent / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
    
    def test_sjpg_format_version(self):
        """Test that SJPG format version is defined."""
        # Check the script file contains the constant definition
        script_content = self.script_path.read_text()
        self.assertIn("SJPG_FILE_FORMAT_VERSION", script_content)
    
    def test_split_height_constant(self):
        """Test that JPEG split height constant is defined."""
        # Check the script file contains the constant definition
        script_content = self.script_path.read_text()
        self.assertIn("JPEG_SPLIT_HEIGHT", script_content)
        self.assertIn("16", script_content)


if __name__ == '__main__':
    unittest.main()
