#!/usr/bin/env python3
"""Unit tests for jpg_to_sjpg.py using standard library unittest."""

import unittest
import os
import sys
import tempfile
import shutil
from PIL import Image

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lib.lvgl.scripts.jpg_to_sjpg import jpg_to_sjpg, calculate_jpg_size, calculate_sjpg_size


class TestJpgToSjpg(unittest.TestCase):
    """Test cases for the JPEG to SJPG conversion."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.input_path = os.path.join(self.temp_dir, 'input.jpg')
        self.output_path = os.path.join(self.temp_dir, 'output.sjpg')
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_calculate_jpg_size(self):
        """Test JPEG size calculation."""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(self.input_path)
        
        # Calculate size
        size = calculate_jpg_size(self.input_path)
        
        # Verify size is reasonable (should be > 0 and < 1MB)
        self.assertGreater(size, 0)
        self.assertLess(size, 1024 * 1024)
    
    def test_calculate_sjpg_size(self):
        """Test SJPG size calculation."""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(self.input_path)
        
        # Convert to sjpg
        jpg_to_sjpg(self.input_path, self.output_path, 100, 100)
        
        # Calculate size
        size = calculate_sjpg_size(self.output_path)
        
        # Verify size is reasonable
        self.assertGreater(size, 0)
        self.assertLess(size, 1024 * 1024)
    
    def test_jpg_to_sjpg_conversion(self):
        """Test full JPEG to SJPG conversion."""
        # Create a test image with gradient
        img = Image.new('RGB', (100, 100))
        for x in range(100):
            for y in range(100):
                img.putpixel((x, y), (x * 2, y * 2, (x + y) * 2))
        img.save(self.input_path)
        
        # Convert to sjpg
        result = jpg_to_sjpg(self.input_path, self.output_path, 100, 100)
        
        # Verify conversion succeeded
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_path))
    
    def test_jpg_to_sjpg_with_different_dimensions(self):
        """Test conversion with different image dimensions."""
        # Create a test image with different dimensions
        img = Image.new('RGB', (200, 150), color='green')
        img.save(self.input_path)
        
        # Convert to sjpg with matching dimensions
        result = jpg_to_sjpg(self.input_path, self.output_path, 200, 150)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_path))
    
    def test_jpg_to_sjpg_preserves_dimensions(self):
        """Test that output dimensions match input dimensions."""
        # Create a test image
        width, height = 320, 240
        img = Image.new('RGB', (width, height), color='yellow')
        img.save(self.input_path)
        
        # Convert to sjpg
        jpg_to_sjpg(self.input_path, self.output_path, width, height)
        
        # Verify output file exists and has correct dimensions
        self.assertTrue(os.path.exists(self.output_path))
        
        # Read the sjpg file to verify dimensions
        with open(self.output_path, 'rb') as f:
            # SJPG format: first 8 bytes are header, next 4 bytes are width, next 4 bytes are height
            f.seek(4)
            import struct
            output_width = struct.unpack('<I', f.read(4))[0]
            output_height = struct.unpack('<I', f.read(4))[0]
            
            self.assertEqual(output_width, width)
            self.assertEqual(output_height, height)
    
    def test_jpg_to_sjpg_with_small_image(self):
        """Test conversion with a very small image."""
        # Create a tiny test image
        img = Image.new('RGB', (10, 10), color='purple')
        img.save(self.input_path)
        
        # Convert to sjpg
        result = jpg_to_sjpg(self.input_path, self.output_path, 10, 10)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_path))
    
    def test_jpg_to_sjpg_with_large_image(self):
        """Test conversion with a larger image."""
        # Create a larger test image
        img = Image.new('RGB', (480, 320), color='orange')
        img.save(self.input_path)
        
        # Convert to sjpg
        result = jpg_to_sjpg(self.input_path, self.output_path, 480, 320)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_path))
    
    def test_sjpg_file_structure(self):
        """Test that the sjpg file has the correct structure."""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='cyan')
        img.save(self.input_path)
        
        # Convert to sjpg
        jpg_to_sjpg(self.input_path, self.output_path, 100, 100)
        
        # Verify file structure
        with open(self.output_path, 'rb') as f:
            # Read header
            header = f.read(8)
            self.assertEqual(len(header), 8)
            
            # Read dimensions
            f.seek(4)
            import struct
            width = struct.unpack('<I', f.read(4))[0]
            height = struct.unpack('<I', f.read(4))[0]
            
            self.assertEqual(width, 100)
            self.assertEqual(height, 100)
            
            # Read number of slices
            num_slices = struct.unpack('<I', f.read(4))[0]
            self.assertGreater(num_slices, 0)


if __name__ == '__main__':
    unittest.main()
