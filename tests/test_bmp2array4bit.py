import os
import sys
import tempfile
import struct
import pytest

# Extract core logic from bmp2array4bit.py (binary parsing functions)
def parse_bmp_header(contents):
    """
    Extracted from bmp2array4bit.py: parse BMP file header
    Returns: dict with file size, offset, width, height, etc.
    """
    upto = 2  # Skip "BM" signature
    
    # Get file size (4 bytes)
    data = struct.pack("BBBB", contents[upto], contents[upto+1], contents[upto+2], contents[upto+3])
    file_size = struct.unpack("I", bytearray(data))[0]
    upto += 4
    
    # Skip 4 reserved bytes
    upto += 4
    
    # Get header offset (4 bytes)
    data = struct.pack("BBBB", contents[upto], contents[upto+1], contents[upto+2], contents[upto+3])
    offset = struct.unpack("I", bytearray(data))[0]
    upto += 4
    
    # Get header size (4 bytes)
    data = struct.pack("BBBB", contents[upto], contents[upto+1], contents[upto+2], contents[upto+3])
    header_size = struct.unpack("I", bytearray(data))[0]
    start_of_definitions = header_size + upto
    upto += 4
    
    # Get width (4 bytes)
    data = struct.pack("BBBB", contents[upto], contents[upto+1], contents[upto+2], contents[upto+3])
    width = struct.unpack("I", bytearray(data))[0]
    upto += 4
    
    # Get height (4 bytes)
    data = struct.pack("BBBB", contents[upto], contents[upto+1], contents[upto+2], contents[upto+3])
    height = struct.unpack("I", bytearray(data))[0]
    upto += 4
    
    return {
        'file_size': file_size,
        'offset': offset,
        'header_size': header_size,
        'start_of_definitions': start_of_definitions,
        'width': width,
        'height': height
    }

def validate_bmp_signature(contents):
    """Extracted: validate BMP signature is 'BM'"""
    if len(contents) < 2:
        return False
    return contents[0:2] == b'BM'

def calculate_row_padding(width, bits_per_pixel=4):
    """Extracted: calculate row padding for 4-bit BMP"""
    # Each row must be padded to 4-byte boundary
    bytes_per_row = (width * bits_per_pixel) // 8  # floor division
    return (4 - (bytes_per_row % 4)) % 4