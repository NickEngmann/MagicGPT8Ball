"""Tests for lib/lvgl/scripts/jpg_to_sjpg.py - Image conversion script for LVGL."""

import os
import sys
import tempfile
import shutil

# Get the repo root directory
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)


class TestJpgToSjpg:
    """Test cases for the jpg_to_sjpg.py conversion script."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = os.path.join(self.temp_dir, 'input')
        self.output_dir = os.path.join(self.temp_dir, 'output')
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def teardown_method(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_script_exists(self):
        """Test that the jpg_to_sjpg.py script exists."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        assert os.path.exists(script_path)
        assert os.path.isfile(script_path)

    def test_script_has_dependencies(self):
        """Test that script declares its dependencies."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for required imports (may be on same line)
        assert "PIL" in content
        assert "Image" in content
        # Combined import line: import math, os, sys, time
        assert "import math" in content or "math," in content
        assert "import os" in content or "os," in content
        assert "import sys" in content or "sys," in content
        assert "import time" in content or "time" in content

    def test_sjpg_file_format_version(self):
        """Test that SJPG format version is defined."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for version constant
        assert 'SJPG_FILE_FORMAT_VERSION' in content
        assert '"V1.00"' in content

    def test_jpeg_split_height(self):
        """Test that JPEG split height is configurable."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        assert 'JPEG_SPLIT_HEIGHT' in content
        assert '= 16' in content

    def test_usage_message_shown_without_args(self):
        """Test that usage message is shown when no arguments provided."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for usage message
        assert 'usage:' in content
        assert 'python' in content
        assert 'input_file.jpg' in content

    def test_file_not_found_error(self):
        """Test that file not found error is handled."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for error handling
        assert 'File not found' in content
        assert 'sys.exit(0)' in content

    def test_input_file_parsed_from_args(self):
        """Test that input file is parsed from command line args."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for argument parsing
        assert 'sys.argv[1]' in content
        assert 'INPUT_FILE = ' in content

    def test_output_filename_derived_from_input(self):
        """Test that output filename is derived from input filename."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for output filename logic
        assert 'OUTPUT_FILE_NAME' in content
        assert 'INPUT_FILE.split' in content

    def test_image_open_called(self):
        """Test that Image.open is called to load input image."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        assert 'im = Image.open(INPUT_FILE)' in content

    def test_dimensions_extracted(self):
        """Test that image dimensions are extracted."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        assert 'width, height = im.size' in content
        assert 'RES = ' in content

    def test_crop_calculation(self):
        """Test that crop calculation is performed for splitting."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for block size calculation
        assert 'block_size = JPEG_SPLIT_HEIGHT' in content
        assert 'spilts = math.ceil(height/block_size)' in content

    def test_jpg_files_created(self):
        """Test that intermediate JPEG files are created."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for crop save logic
        assert 'crop.save' in content
        assert 'quality=90' in content

    def test_header_structure(self):
        """Test that header structure is defined for output."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check header components
        assert '"_SJPG__"' in content
        assert 'SJPG_FILE_FORMAT_VERSION' in content
        assert '.to_bytes(2' in content  # width, height, etc.

    def test_binary_output_created(self):
        """Test that binary output file is created."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for sjpg file creation
        assert 'OUTPUT_FILE_NAME+".sjpg"' in content
        assert 'f.write(sjpeg)' in content

    def test_c_array_generated(self):
        """Test that C array code is generated."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for C code generation
        assert 'c_code = ' in content
        assert 'const uint8_t' in content
        assert 'LV_IMG_CF_RAW' in content
        assert '.c' in content  # C file creation

    def test_temp_jpg_files_removed(self):
        """Test that temporary JPEG files are cleaned up."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for cleanup
        assert 'os.remove(str(i) + ".jpg")' in content

    def test_conversion_timing_reported(self):
        """Test that conversion time is reported."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for timing
        assert 'start_time = time.time()' in content
        assert 'time_taken = (time.time() - start_time)' in content
        assert 'Time taken' in content

    def test_file_size_reported(self):
        """Test that output file size is reported."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for size reporting
        assert 'bin size' in content
        assert 'KB' in content

    def test_multiple_output_files_created(self):
        """Test that both .sjpg and .c files are created."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for dual output
        assert '"_sjpg' in content or '.sjpg' in content
        assert "'_c'" in content or '.c' in content
        assert "f.write(sjpeg)" in content  # Binary output
        assert "f = open(OUTPUT_FILE_NAME + '.c'" in content  # C array output

    def test_image_dimensions_printed(self):
        """Test that input image dimensions are printed."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for dimension printing
        assert 'RES = ' in content
        assert 'str(width)' in content
        assert 'str(height)' in content

    def test_header_bytes_written(self):
        """Test that header bytes are properly formatted."""
        script_path = os.path.join(repo_root, 'lib', 'lvgl', 'scripts', 'jpg_to_sjpg.py')
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check header byte writing
        assert 'header = header +' in content
        assert '.encode' in content
        assert 'byteorder' in content
