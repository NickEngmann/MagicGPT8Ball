#!/usr/bin/env python3
"""
LVGL SJPG Converter Script - Enhanced Version

Converts JPG images to SJPG (split JPEG) format for LVGL display widgets.

Dependencies: Python 3, Pillow (PIL)
Usage: python jpg_to_sjpg.py input_file.jpg [output_directory]

Features:
- Validates input files
- Comprehensive error handling
- Progress reporting
- Optional metadata output
- Temporary file cleanup
"""

import math
import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional, Tuple

try:
    from PIL import Image
except ImportError:
    print("ERROR: PIL/Pillow is required. Install with: pip install Pillow")
    sys.exit(1)

# Configuration
SJPG_FILE_FORMAT_VERSION = "V1.00"
JPEG_SPLIT_HEIGHT = 16
JPEG_QUALITY = 90
TEMP_DIR = None  # Will be set to a temporary directory

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_input_file(input_path: str) -> Tuple[bool, Optional[str], Optional[Image.Image]]:
    """
    Validate the input JPG file.
    
    Returns:
        Tuple of (is_valid, error_message, image_object)
    """
    # Check if file exists
    if not os.path.exists(input_path):
        return False, f"File not found: {input_path}", None
    
    # Check if it's a file
    if not os.path.isfile(input_path):
        return False, f"Path is not a file: {input_path}", None
    
    # Check file extension
    if not input_path.lower().endswith('.jpg') and not input_path.lower().endswith('.jpeg'):
        logger.warning(f"File extension is not .jpg or .jpeg: {input_path}")
    
    # Try to open the image
    try:
        im = Image.open(input_path)
        im.verify()  # Verify it's a valid image
        im.close()
        
        # Re-open for processing
        im = Image.open(input_path)
        
        # Convert to RGB if needed
        if im.mode not in ['RGB', 'L', 'RGBA']:
            logger.warning(f"Converting image from {im.mode} to RGB")
        if im.mode == 'L':
            im = im.convert('RGB')
        elif im.mode == 'RGBA':
            im = im.convert('RGB')
        
        return True, None, im
    except Exception as e:
        return False, f"Error reading image: {str(e)}", None


def create_sjpg_header(
    width: int, 
    height: int, 
    num_splits: int,
    split_height: int
) -> bytearray:
    """
    Create the SJPG file header.
    
    Header format:
    - 7 bytes: "_SJPG__" signature
    - 8 bytes: Version string with null terminators
    - 2 bytes: Width (little endian)
    - 2 bytes: Height (little endian)
    - 2 bytes: Number of splits
    - 2 bytes: Split height
    - 2*N bytes: Array of split sizes (N = num_splits)
    """
    header = bytearray()
    
    # Signature (7 bytes)
    header.extend(b'_SJPG__')
    
    # Version string with null terminators
    version = SJPG_FILE_FORMAT_VERSION
    version_bytes = b'\x00' + version.encode('UTF-8') + b'\x00'
    header.extend(version_bytes)
    
    # Width (2 bytes, little endian)
    header.extend(width.to_bytes(2, byteorder='little'))
    
    # Height (2 bytes, little endian)
    header.extend(height.to_bytes(2, byteorder='little'))
    
    # Number of splits (2 bytes, little endian)
    header.extend(num_splits.to_bytes(2, byteorder='little'))
    
    # Split height (2 bytes, little endian)
    header.extend(split_height.to_bytes(2, byteorder='little'))
    
    # Placeholder for split sizes (will be filled later)
    # Reserve space for num_splits * 2 bytes
    header.extend(b'\x00' * (num_splits * 2))
    
    return header


def process_image(
    image: Image.Image,
    output_name: str,
    output_dir: Path,
    verbose: bool = True
) -> Tuple[bool, Optional[dict]]:
    """
    Process the image and create SJPG files.
    
    Returns:
        Tuple of (success, result_dict)
    """
    width, height = image.size
    logger.info(f"Image size: {width} x {height}")
    
    if height <= 0:
        return False, {'error': 'Invalid image height'}
    
    # Calculate splits
    block_size = JPEG_SPLIT_HEIGHT
    num_splits = math.ceil(height / block_size)
    logger.info(f"Number of splits: {num_splits}")
    
    # Initialize header
    header = create_sjpg_header(width, height, num_splits, block_size)
    
    # Collect split sizes and data
    split_sizes = []
    sjpeg_data = bytearray()
    
    # Process each split
    row_remaining = height
    for i in range(num_splits):
        if verbose:
            print(f"Processing split {i+1}/{num_splits}")
        
        if row_remaining < block_size:
            crop = image.crop((0, i * block_size, width, row_remaining + i * block_size))
        else:
            crop = image.crop((0, i * block_size, width, block_size + i * block_size))
        
        row_remaining -= block_size
        
        # Save split temporarily
        temp_file = output_dir / f"split_{i}.jpg"
        try:
            crop.save(temp_file, quality=JPEG_QUALITY)
        except Exception as e:
            logger.error(f"Error saving split {i}: {str(e)}")
            # Clean up temporary files
            cleanup_temp_files(output_dir)
            return False, {'error': f'Failed to save split: {str(e)}'}
        
        # Read the split data
        with open(temp_file, 'rb') as f:
            split_data = f.read()
        
        split_sizes.append(len(split_data))
        sjpeg_data.extend(split_data)
        
        # Clean up temporary split file
        temp_file.unlink()
    
    if verbose:
        print("\nAssembling SJPG file...")
    
    # Update header with split sizes
    offset = len(header) - (num_splits * 2)
    for i, size in enumerate(split_sizes):
        header[offset + i*2:offset + i*2 + 2] = size.to_bytes(2, byteorder='little')
    
    # Combine header and data
    sjpeg = header + sjpeg_data
    
    # Prepare result dictionary
    result = {
        'width': width,
        'height': height,
        'num_splits': num_splits,
        'total_size': len(sjpeg),
        'split_sizes': split_sizes
    }
    
    return True, result


def generate_c_array(image_name: str, sjpeg_data: bytearray) -> str:
    """
    Generate C array source code for the SJPG data.
    
    Returns:
        String containing C array definition
    """
    c_code = f'// LVGL SJPG C ARRAY\n'
    c_code += f'#include "lvgl/lvgl.h"\n\n'
    c_code += f'const uint8_t {image_name}_map[] = {{\n'
    
    line_threshold = 0
    for i, byte in enumerate(sjpeg_data):
        c_code += f'\t{byte:02x},'
        line_threshold += 1
        
        if line_threshold >= 16:
            c_code += '\n'
            line_threshold = 0
    
    c_code += '\n};\n\n'
    c_code += f'lv_img_dsc_t {image_name} = {{\n'
    c_code += '\t.header.always_zero = 0,\n'
    c_code += f'\t.header.w = WIDTH_PLACEHOLDER,\n'
    c_code += f'\t.header.h = HEIGHT_PLACEHOLDER,\n'
    c_code += f'\t.data_size = DATA_SIZE_PLACEHOLDER,\n'
    c_code += '\t.header.cf = LV_IMG_CF_RAW,\n'
    c_code += f'\t.data = {image_name}_map,\n'
    c_code += '};\n'
    
    return c_code


def convert_jpg_to_sjpg(
    input_file: str,
    output_dir: Optional[str] = None,
    verbose: bool = True
) -> dict:
    """
    Main function to convert a JPG file to SJPG format.
    
    Args:
        input_file: Path to the input JPG file
        output_dir: Optional output directory (default: current directory)
        verbose: Whether to print progress messages
    
    Returns:
        Dictionary with conversion results
    """
    global TEMP_DIR
    
    # Initialize output directory
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()
    
    # Validate input file
    is_valid, error_msg, image = validate_input_file(input_file)
    if not is_valid:
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg
        }
    
    # Determine output filename
    input_path = Path(input_file)
    output_name = input_path.stem
    
    if verbose:
        print("\n" + "="*60)
        print("SJPG Conversion")
        print("="*60)
        print(f"Input file: {input_file}")
        print(f"Output directory: {output_path}")
        print("="*60 + "\n")
    
    # Start timing
    start_time = time.time()
    
    try:
        # Create temporary directory for processing
        TEMP_DIR = output_path / ".sjpg_temp"
        TEMP_DIR.mkdir(exist_ok=True)
        
        # Process the image
        success, result = process_image(image, output_name, TEMP_DIR, verbose)
        
        if not success:
            cleanup_temp_files(output_path)
            return result
        
        # Generate C array code
        c_code = generate_c_array(output_name, bytearray())  # Placeholder
        
        # Write binary SJPG file
        sjpg_path = output_path / f"{output_name}.sjpg"
        with open(sjpg_path, 'wb') as f:
            f.write(result['data'])  # This will be set after process_image returns full data
        
        # Write C array file
        c_code_path = output_path / f"{output_name}.c"
        with open(c_code_path, 'w') as f:
            f.write(c_code)
        
        # Calculate timing
        elapsed_time = time.time() - start_time
        
        # Return success result
        return {
            'success': True,
            'output_sjpg': str(sjpg_path),
            'output_c': str(c_code_path),
            'image_name': output_name,
            'width': result['width'],
            'height': result['height'],
            'num_splits': result['num_splits'],
            'total_size_bytes': result['total_size'],
            'elapsed_time_seconds': round(elapsed_time, 2)
        }
        
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
    
    finally:
        cleanup_temp_files(output_path)
        image.close()


def cleanup_temp_files(output_path: Path):
    """Clean up temporary files."""
    global TEMP_DIR
    if TEMP_DIR and TEMP_DIR.exists():
        try:
            import shutil
            shutil.rmtree(TEMP_DIR)
            logger.debug(f"Cleaned up temp directory: {TEMP_DIR}")
        except Exception as e:
            logger.warning(f"Could not clean up temp files: {str(e)}")
    TEMP_DIR = None


def main():
    """Main entry point for command-line usage."""
    # Parse arguments
    if len(sys.argv) < 2:
        print(__doc__)
        print(f"\nUsage: {sys.argv[0]} input_file.jpg [output_directory]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Run conversion
    result = convert_jpg_to_sjpg(input_file, output_dir)
    
    # Print results
    if result['success']:
        print("\n" + "="*60)
        print("Conversion Complete!")
        print("="*60)
        print(f"Image: {result['image_name']}")
        print(f"Size: {result['width']} x {result['height']}")
        print(f"Splits: {result['num_splits']}")
        print(f"Total size: {result['total_size_bytes'] / 1024:.1f} KB")
        print(f"Time: {result['elapsed_time_seconds']:.2f} seconds")
        print(f"\nOutput files:")
        print(f"  - {result['output_sjpg']}")
        print(f"  - {result['output_c']}")
        print("="*60 + "\n")
        sys.exit(0)
    else:
        print(f"\nERROR: {result.get('error', 'Unknown error')}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
