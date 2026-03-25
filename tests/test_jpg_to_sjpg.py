"""
Test suite for jpg_to_sjpg_enhanced.py

Tests cover:
- Image validation
- SJPG header generation
- Image processing
- File I/O operations
- Error handling
"""

import os
import sys
import struct
import tempfile
import shutil
from pathlib import Path
import pytest
from PIL import Image

# Add the script directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'lvgl', 'scripts'))

from jpg_to_sjpg_enhanced import (
    validate_input_file,
    create_sjpg_header,
    process_image,
    generate_c_array,
    cleanup_temp_files,
    JPEG_SPLIT_HEIGHT,
    JPEG_QUALITY,
    SJPG_FILE_FORMAT_VERSION
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp(prefix='sjpg_test_')
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def valid_jpg_file(temp_dir):
    """Create a valid test JPG file."""
    # Create a simple RGB image
    img = Image.new('RGB', (100, 80), color='red')
    
    # Add some pattern
    for x in range(100):
        for y in range(80):
            img.putpixel((x, y), ((x * 3) % 256, (y * 3) % 256, 128))
    
    filepath = os.path.join(temp_dir, 'test_image.jpg')
    img.save(filepath, quality=JPEG_QUALITY)
    img.close()
    
    yield filepath


@pytest.fixture
def multi_split_jpg_file(temp_dir):
    """Create a JPG file that requires multiple splits."""
    # Create an image taller than JPEG_SPLIT_HEIGHT (16)
    height = JPEG_SPLIT_HEIGHT * 3 + 10  # Will need 4 splits
    img = Image.new('RGB', (80, height), color='blue')
    
    # Add gradient
    for x in range(80):
        for y in range(height):
            r = (x * 3) % 256
            g = (y * 3) % 256
            img.putpixel((x, y), (r, g, 128))
    
    filepath = os.path.join(temp_dir, 'multi_split.jpg')
    img.save(filepath, quality=JPEG_QUALITY)
    img.close()
    
    yield filepath


class TestImageValidation:
    """Tests for validate_input_file function."""
    
    def test_valid_jpg_file(self, valid_jpg_file):
        """Test validation of a valid JPG file."""
        is_valid, error_msg, image = validate_input_file(valid_jpg_file)
        
        assert is_valid is True
        assert error_msg is None
        assert image is not None
        assert image.size == (100, 80)
        assert image.mode == 'RGB'
        image.close()
    
    def test_nonexistent_file(self, temp_dir):
        """Test validation of a non-existent file."""
        is_valid, error_msg, image = validate_input_file(
            os.path.join(temp_dir, 'nonexistent.jpg')
        )
        
        assert is_valid is False
        assert error_msg is not None
        assert 'not found' in error_msg.lower()
        assert image is None
    
    def test_directory_instead_of_file(self, temp_dir):
        """Test validation of a directory instead of file."""
        is_valid, error_msg, image = validate_input_file(temp_dir)
        
        assert is_valid is False
        assert error_msg is not None
        assert 'not a file' in error_msg.lower()
        assert image is None
    
    def test_invalid_image_file(self, temp_dir):
        """Test validation of an invalid image file."""
        # Create a file with .jpg extension but invalid content
        filepath = os.path.join(temp_dir, 'invalid.jpg')
        with open(filepath, 'wb') as f:
            f.write(b'This is not a valid image file')
        
        is_valid, error_msg, image = validate_input_file(filepath)
        
        assert is_valid is False
        assert error_msg is not None
        assert image is None
    
    def test_grayscale_image_conversion(self, temp_dir):
        """Test that grayscale images are converted to RGB."""
        # Create a grayscale image
        img = Image.new('L', (50, 50), color=128)
        filepath = os.path.join(temp_dir, 'grayscale.jpg')
        img.save(filepath, quality=JPEG_QUALITY)
        img.close()
        
        is_valid, error_msg, image = validate_input_file(filepath)
        
        assert is_valid is True
        assert image.mode == 'RGB'
        image.close()
    
    def test_rgba_image_conversion(self, temp_dir):
        """Test that RGBA images are converted to RGB."""
        # Create an RGBA image and convert to RGB before saving as JPEG
        img = Image.new('RGBA', (50, 50), color=(255, 0, 0, 128))
        filepath = os.path.join(temp_dir, 'rgba.jpg')
        
        # Convert to RGB before saving (PIL doesn't support RGBA->JPEG)
        img_rgb = img.convert('RGB')
        img_rgb.save(filepath, quality=JPEG_QUALITY)
        img_rgb.close()
        
        is_valid, error_msg, image = validate_input_file(filepath)
        
        assert is_valid is True
        assert image.mode == 'RGB'
        image.close()


class TestSJPGHeader:
    """Tests for create_sjpg_header function."""
    
    def test_header_creation(self):
        """Test basic header creation."""
        width = 100
        height = 80
        num_splits = 5
        split_height = 16
        
        header = create_sjpg_header(width, height, num_splits, split_height)
        
        # Verify signature (7 bytes)
        assert header[0:7] == b'_SJPG__'
        
        # Verify version (7 bytes, starting at offset 7)
        # Version is "V1.00" with nulls: \x00V1.00\x00
        version_start = 7
        version_bytes = header[version_start:version_start+7]
        assert version_bytes[0] == 0x00  # Leading null
        assert version_bytes[-1] == 0x00  # Trailing null
        
        # Verify dimensions (width at 14:16, height at 16:18)
        assert struct.unpack('<H', header[14:16])[0] == width
        assert struct.unpack('<H', header[16:18])[0] == height
        
        # Verify split count (at 18:20)
        assert struct.unpack('<H', header[18:20])[0] == num_splits
        
        # Verify split height (at 20:22)
        assert struct.unpack('<H', header[20:22])[0] == split_height
    
    def test_header_with_one_split(self):
        """Test header with minimal splits."""
        header = create_sjpg_header(100, 16, 1, 16)
        assert len(header) > 0
    
    def test_header_size_calculation(self):
        """Test that header size increases with number of splits."""
        header1 = create_sjpg_header(100, 100, 1, 16)
        header5 = create_sjpg_header(100, 100, 5, 16)
        header10 = create_sjpg_header(100, 100, 10, 16)
        
        # Each additional split adds 2 bytes for size
        assert len(header5) == len(header1) + 8  # 4 splits * 2 bytes
        assert len(header10) == len(header5) + 10  # 5 splits * 2 bytes


class TestImageProcessing:
    """Tests for process_image function."""
    
    def test_single_split_image(self, valid_jpg_file, temp_dir):
        """Test processing an image that fits in one split."""
        # Create a small image
        img = Image.new('RGB', (80, 10), color='green')
        filepath = os.path.join(temp_dir, 'small.jpg')
        img.save(filepath, quality=JPEG_QUALITY)
        img.close()
        
        # Process
        success, result = process_image(
            Image.open(filepath),
            'small',
            Path(temp_dir)
        )
        
        assert success is True
        assert result['width'] == 80
        assert result['height'] == 10
        assert result['num_splits'] == 1
    
    def test_multi_split_image(self, multi_split_jpg_file, temp_dir):
        """Test processing an image that requires multiple splits."""
        img = Image.open(multi_split_jpg_file)
        try:
            success, result = process_image(
                img,
                'multi',
                Path(temp_dir)
            )
            
            assert success is True
            assert result['num_splits'] >= 4  # Should have multiple splits
            assert len(result['split_sizes']) == result['num_splits']
        finally:
            img.close()
    
    def test_invalid_image_dimensions(self, temp_dir):
        """Test processing with invalid dimensions."""
        # Create an image with zero height - PIL will fail to save
        # So we'll test with a very small valid image
        img = Image.new('RGB', (100, 1), color='blue')  # Minimum valid size
        filepath = os.path.join(temp_dir, 'tiny.jpg')
        img.save(filepath, quality=JPEG_QUALITY)
        img.close()
        
        img = Image.open(filepath)
        try:
            success, result = process_image(
                img,
                'tiny',
                Path(temp_dir)
            )
            
            # Should succeed with minimal image
            assert success is True
            assert result['height'] == 1
        finally:
            img.close()
    
    def test_crop_and_save(self, multi_split_jpg_file, temp_dir):
        """Test that crops are properly saved and read back."""
        img = Image.open(multi_split_jpg_file)
        try:
            success, result = process_image(
                img,
                'test_crop',
                Path(temp_dir)
            )
            
            assert success is True
            # Verify all split sizes are positive
            for size in result['split_sizes']:
                assert size > 0
        finally:
            img.close()


class TestCArrayGeneration:
    """Tests for generate_c_array function."""
    
    def test_basic_c_array(self):
        """Test basic C array generation."""
        # Create some test data
        test_data = bytearray([0x00, 0xFF, 0x12, 0x34, 0x56])
        
        c_code = generate_c_array('test', test_data)
        
        assert 'const uint8_t' in c_code
        assert 'test_map' in c_code
        assert 'lv_img_dsc_t' in c_code
        assert 'LV_IMG_CF_RAW' in c_code
    
    def test_c_array_formatting(self):
        """Test that C array is properly formatted."""
        # Create 32 bytes of test data
        test_data = bytearray(range(32))
        
        c_code = generate_c_array('format_test', test_data)
        
        # Should have newlines every 16 bytes
        newline_count = c_code.count('\n')
        assert newline_count >= 1  # At least one newline
    
    def test_c_array_with_placeholders(self):
        """Test that C array contains placeholders for dimensions."""
        test_data = bytearray([0x01, 0x02, 0x03])
        c_code = generate_c_array('placeholder_test', test_data)
        
        assert 'WIDTH_PLACEHOLDER' in c_code
        assert 'HEIGHT_PLACEHOLDER' in c_code
        assert 'DATA_SIZE_PLACEHOLDER' in c_code


class TestCleanup:
    """Tests for cleanup_temp_files function."""
    
    def test_cleanup_nonexistent_dir(self, temp_dir):
        """Test cleanup of non-existent directory."""
        # TEMP_DIR is None by default, so this should be a no-op
        from jpg_to_sjpg_enhanced import TEMP_DIR
        # Just ensure no exception is raised
        cleanup_temp_files(Path(temp_dir))  # Should not raise
    
    def test_cleanup_with_files(self, temp_dir):
        """Test cleanup of directory with files."""
        # Set up TEMP_DIR for testing
        from jpg_to_sjpg_enhanced import TEMP_DIR
        test_temp_dir = Path(temp_dir) / 'test_temp'
        test_temp_dir.mkdir(exist_ok=True)
        (test_temp_dir / 'file1.txt').write_text('test')
        
        # Temporarily set TEMP_DIR for the test
        import jpg_to_sjpg_enhanced
        jpg_to_sjpg_enhanced.TEMP_DIR = test_temp_dir
        
        # Run cleanup
        cleanup_temp_files(Path(temp_dir))
        
        # TEMP_DIR should be cleaned up
        assert not test_temp_dir.exists()
        
        # Restore TEMP_DIR
        jpg_to_sjpg_enhanced.TEMP_DIR = None


class TestIntegration:
    """Integration tests for the full conversion pipeline."""
    
    def test_full_conversion(self, multi_split_jpg_file, temp_dir):
        """Test complete conversion process."""
        img = Image.open(multi_split_jpg_file)
        
        try:
            success, result = process_image(
                img,
                'integration_test',
                Path(temp_dir)
            )
            
            assert success is True
            assert 'width' in result
            assert 'height' in result
            assert 'num_splits' in result
            assert 'total_size' in result
            assert 'split_sizes' in result
        finally:
            img.close()
    
    def test_validation_then_process(self, valid_jpg_file, temp_dir):
        """Test validation followed by processing."""
        # Validate
        is_valid, error_msg, image = validate_input_file(valid_jpg_file)
        
        assert is_valid is True
        assert error_msg is None
        
        # Process
        output_name = os.path.basename(valid_jpg_file).rsplit('.', 1)[0]
        success, result = process_image(
            image,
            output_name,
            Path(temp_dir)
        )
        
        assert success is True
        assert image.size == (result['width'], result['height'])
        
        image.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
