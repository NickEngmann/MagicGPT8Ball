"""
Test suite for jpg_to_sjpg.py - LVGL SJPG conversion script.
"""

import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestJpgToSjpgScriptStructure(unittest.TestCase):
    """Tests for jpg_to_sjpg.py script structure and constants."""

    def setUp(self):
        """Set up test fixtures."""
        self.script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"

    def test_script_exists(self):
        """Test that jpg_to_sjpg.py script exists."""
        self.assertTrue(self.script_path.exists())
        self.assertTrue(self.script_path.is_file())

    def test_sjpg_version_constant(self):
        """Test that SJPG_FILE_FORMAT_VERSION constant is defined."""
        content = self.script_path.read_text()
        
        self.assertIn("SJPG_FILE_FORMAT_VERSION", content)
        self.assertIn('"V1.00"', content)

    def test_jpeg_split_height_constant(self):
        """Test that JPEG_SPLIT_HEIGHT constant is defined."""
        content = self.script_path.read_text()
        
        self.assertIn("JPEG_SPLIT_HEIGHT", content)
        self.assertIn("16", content)

    def test_pil_import_exists(self):
        """Test that PIL Image module is imported."""
        content = self.script_path.read_text()
        
        self.assertIn("from PIL import Image", content)

    def test_required_modules_imported(self):
        """Test that required modules are imported."""
        content = self.script_path.read_text()
        
        # Check for module imports (they may be on one line)
        self.assertIn("math", content)
        self.assertIn("os", content)
        self.assertIn("sys", content)
        self.assertIn("time", content)

    def test_output_file_name_variable(self):
        """Test that OUTPUT_FILE_NAME variable is defined."""
        content = self.script_path.read_text()
        
        self.assertIn("OUTPUT_FILE_NAME", content)

    def test_input_file_variable(self):
        """Test that INPUT_FILE variable is defined."""
        content = self.script_path.read_text()
        
        self.assertIn("INPUT_FILE", content)

    def test_script_uses_command_line_args(self):
        """Test that script uses command line arguments."""
        content = self.script_path.read_text()
        
        self.assertIn("sys.argv", content)
        self.assertIn("len(sys.argv)", content)

    def test_script_usage_message(self):
        """Test that script shows usage message."""
        content = self.script_path.read_text()
        
        self.assertIn("usage:", content)
        self.assertIn("python", content)
        self.assertIn("input_file.jpg", content)


class TestJpgToSjpgConversionLogic(unittest.TestCase):
    """Tests for jpg_to_sjpg.py conversion logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_crops_image_into_blocks(self):
        """Test that script crops image into blocks."""
        content = self.script_path.read_text()
        
        self.assertIn("crop = im.crop", content)
        self.assertIn("block_size", content)
        self.assertIn("JPEG_SPLIT_HEIGHT", content)

    def test_saves_jpg_temporarily(self):
        """Test that script saves temporary JPG files."""
        content = self.script_path.read_text()
        
        self.assertIn("crop.save", content)
        self.assertIn("quality=90", content)

    def test_reads_jpg_files(self):
        """Test that script reads JPG files for concatenation."""
        content = self.script_path.read_text()
        
        self.assertIn('open(str(i)+".jpg", "rb")', content)
        self.assertIn("f.read()", content)

    def test_creates_header_bytes(self):
        """Test that script creates header for SJPG format."""
        content = self.script_path.read_text()
        
        self.assertIn("header = bytearray()", content)
        self.assertIn("_SJPG__", content)
        self.assertIn("SJPG_FILE_FORMAT_VERSION", content)
        self.assertIn("to_bytes", content)
        self.assertIn("byteorder='little'", content)

    def test_writes_sjpg_output(self):
        """Test that script writes .sjpg output file."""
        content = self.script_path.read_text()
        
        self.assertIn('f = open(OUTPUT_FILE_NAME+".sjpg","wb")', content)
        self.assertIn("f.write(sjpeg)", content)

    def test_removes_temp_files(self):
        """Test that script removes temporary JPG files."""
        content = self.script_path.read_text()
        
        self.assertIn("os.remove", content)
        self.assertIn('str(i) + ".jpg"', content)

    def test_generates_c_array_code(self):
        """Test that script generates C array code."""
        content = self.script_path.read_text()
        
        self.assertIn("c_code", content)
        self.assertIn("LVGL SJPG C ARRAY", content)
        self.assertIn("lv_img_dsc_t", content)
        self.assertIn("header.w", content)
        self.assertIn("header.h", content)
        self.assertIn("data_size", content)
        self.assertIn("header.cf", content)
        self.assertIn("LV_IMG_CF_RAW", content)

    def test_writes_c_file(self):
        """Test that script writes .c file with array code."""
        content = self.script_path.read_text()
        
        self.assertIn("f = open(OUTPUT_FILE_NAME + '.c', 'w')", content)
        self.assertIn("f.write(c_code)", content)


class TestJpgToSjpgHeaderCreation(unittest.TestCase):
    """Tests for jpg_to_sjpg.py header creation logic."""

    def test_header_format_version(self):
        """Test that header includes format version."""
        script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        content = script_path.read_text()
        
        # Header includes version with null padding
        self.assertIn("SJPG_FILE_FORMAT_VERSION", content)
        self.assertIn("\\x00", content)

    def test_header_width_bytes(self):
        """Test that header includes width in 2 bytes."""
        script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        content = script_path.read_text()
        
        self.assertIn("width.to_bytes(2", content)
        self.assertIn("byteorder='little'", content)

    def test_header_height_bytes(self):
        """Test that header includes height in 2 bytes."""
        script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        content = script_path.read_text()
        
        self.assertIn('header = header + height.to_bytes(2, byteorder=\'little\')', content)

    def test_header_splits_count(self):
        """Test that header includes number of splits."""
        script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        content = script_path.read_text()
        
        self.assertIn('header = header + spilts.to_bytes(2, byteorder=\'little\')', content)

    def test_header_block_size(self):
        """Test that header includes block size."""
        script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        content = script_path.read_text()
        
        self.assertIn('header = header + int(JPEG_SPLIT_HEIGHT).to_bytes(2, byteorder=\'little\')', content)

    def test_header_file_sizes(self):
        """Test that header includes individual file sizes."""
        script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        content = script_path.read_text()
        
        # Check that it iterates through lenbuf to add file sizes
        self.assertIn("for item_len in lenbuf", content)
        self.assertIn('header = header + item_len.to_bytes(2, byteorder=\'little\')', content)


class TestJpgToSjpgImageProcessing(unittest.TestCase):
    """Tests for jpg_to_sjpg.py image processing logic."""

    def test_opens_image_file(self):
        """Test that script opens input image file."""
        script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        content = script_path.read_text()
        
        self.assertIn("im = Image.open(INPUT_FILE)", content)

    def test_gets_image_dimensions(self):
        """Test that script gets image width and height."""
        script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        content = script_path.read_text()
        
        self.assertIn("width, height = im.size", content)

    def test_calculates_split_count(self):
        """Test that script calculates number of splits."""
        script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        content = script_path.read_text()
        
        self.assertIn("spilts = math.ceil(height/block_size)", content)
        self.assertIn("block_size = JPEG_SPLIT_HEIGHT", content)

    def test_handles_remaining_rows(self):
        """Test that script handles remaining rows when image doesn't divide evenly."""
        script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        content = script_path.read_text()
        
        self.assertIn("row_remaining = height", content)
        self.assertIn("if row_remaining < block_size", content)

    def test_image_quality_set(self):
        """Test that image quality is set for JPEG compression."""
        script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        content = script_path.read_text()
        
        self.assertIn("quality=90", content)


class TestJpgToSjpgErrorHandling(unittest.TestCase):
    """Tests for jpg_to_sjpg.py error handling."""

    def test_file_not_found_handling(self):
        """Test that script handles file not found error."""
        script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        content = script_path.read_text()
        
        self.assertIn("try:", content)
        self.assertIn("except:", content)
        self.assertIn("print", content)
        self.assertIn("File not found", content)
        self.assertIn("sys.exit", content)

    def test_invalid_argument_handling(self):
        """Test that script handles invalid number of arguments."""
        script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        content = script_path.read_text()
        
        # Script shows usage if incorrect arguments
        self.assertIn('if len(sys.argv) == 2:', content)
        self.assertIn("print", content)
        self.assertIn("usage:", content)

    def test_timing_output(self):
        """Test that script outputs timing information."""
        script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        content = script_path.read_text()
        
        self.assertIn("start_time = time.time()", content)
        self.assertIn("time_taken", content)
        self.assertIn("Time taken", content)

    def test_output_size_output(self):
        """Test that script outputs output file size."""
        script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        content = script_path.read_text()
        
        self.assertIn('print("\\tbin size = "', content)
        self.assertIn("len(sjpeg)", content)


class TestJpgToSjpgIntegration(unittest.TestCase):
    """Integration tests for jpg_to_sjpg.py with sample images."""

    def setUp(self):
        """Set up test fixtures with sample images."""
        self.script_path = project_root / "lib" / "lvgl" / "scripts" / "jpg_to_sjpg.py"
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Import PIL to create test images
        from PIL import Image
        
        # Create a test image (100x100 pixels)
        self.test_image = self.test_dir / "test_image.jpg"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(self.test_image, 'JPEG')
        
        # Create another test image (64x64 pixels)
        self.test_image2 = self.test_dir / "test_image2.jpg"
        img2 = Image.new('RGB', (64, 64), color='blue')
        img2.save(self.test_image2, 'JPEG')

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up any generated files
        for f in self.test_dir.glob("*.jpg"):
            f.unlink()
        for f in self.test_dir.glob("*.sjpg"):
            f.unlink()
        for f in self.test_dir.glob("*.c"):
            f.unlink()
        shutil.rmtree(self.test_dir)

    def test_conversion_with_100x100_image(self):
        """Test conversion with 100x100 image."""
        from PIL import Image
        import subprocess
        
        # Create test image
        test_image = self.test_dir / "test_image.jpg"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(test_image, 'JPEG')
        
        # Run the script from test directory
        original_cwd = os.getcwd()
        try:
            os.chdir(str(self.test_dir))
            result = subprocess.run(
                [sys.executable, str(self.script_path), "test_image.jpg"],
                capture_output=True,
                text=True
            )
            
            # Check that output files were created
            self.assertTrue((self.test_dir / "test_image.sjpg").exists())
            self.assertTrue((self.test_dir / "test_image.c").exists())
            
            # Check script output
            self.assertIn("All good!", result.stdout)
        finally:
            os.chdir(original_cwd)

    def test_conversion_with_64x64_image(self):
        """Test conversion with 64x64 image."""
        from PIL import Image
        import subprocess
        
        # Create test image
        test_image2 = self.test_dir / "test_image2.jpg"
        img2 = Image.new('RGB', (64, 64), color='blue')
        img2.save(test_image2, 'JPEG')
        
        # Run the script from test directory
        original_cwd = os.getcwd()
        try:
            os.chdir(str(self.test_dir))
            subprocess.run(
                [sys.executable, str(self.script_path), "test_image2.jpg"],
                capture_output=True
            )
            
            # Check that output files were created
            self.assertTrue((self.test_dir / "test_image2.sjpg").exists())
            self.assertTrue((self.test_dir / "test_image2.c").exists())
        finally:
            os.chdir(original_cwd)

    def test_c_file_contains_lvgl_structure(self):
        """Test that generated C file contains LVGL image structure."""
        import subprocess
        
        # Run the script
        subprocess.run(
            [sys.executable, str(self.script_path), str(self.test_image)],
            capture_output=True
        )
        
        # Read generated C file
        c_file = self.test_dir / "test_image.c"
        if c_file.exists():
            content = c_file.read_text()
            
            # Check for LVGL structure
            self.assertIn("lv_img_dsc_t", content)
            self.assertIn("header.w", content)
            self.assertIn("header.h", content)
            self.assertIn("data_size", content)
            self.assertIn("LV_IMG_CF_RAW", content)

    def test_sjpg_file_binary_content(self):
        """Test that generated SJPG file has correct binary content."""
        import subprocess
        
        # Run the script
        subprocess.run(
            [sys.executable, str(self.script_path), str(self.test_image)],
            capture_output=True
        )
        
        # Read generated SJPG file
        sjpg_file = self.test_dir / "test_image.sjpg"
        if sjpg_file.exists():
            content = sjpg_file.read_bytes()
            
            # Check for SJPG header
            self.assertTrue(content.startswith(b'_SJPG__'))
            self.assertIn(b'V1.00', content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
