"""Embedded system mocks for PlatformIO testing.

This module provides Python implementations of Arduino functions
and mock classes for testing embedded C/C++ code.
"""


def arduino_map(x, in_min, in_max, out_min, out_max):
    """Map a value from one range to another.
    
    This is the Python equivalent of Arduino's map() function.
    """
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def arduino_constrain(x, a, b):
    """Constrain a value to be within a range.
    
    This is the Python equivalent of Arduino's constrain() function.
    If b < a, they are swapped to ensure proper constraint.
    """
    if a > b:
        a, b = b, a
    if x < a:
        return a
    elif x > b:
        return b
    else:
        return x


class MockUART:
    """Mock UART interface for testing serial communication.
    
    Provides a mock implementation of UART/Serial functionality
    that can be used to test code that depends on serial communication.
    """
    
    def __init__(self):
        self.buffer = ""
        self.received_data = []
        self.baud_rate = 9600
        self.enabled = True
    
    def begin(self, baud_rate):
        """Initialize UART with specified baud rate."""
        self.baud_rate = baud_rate
        self.buffer = ""
        return True
    
    def end(self):
        """End UART communication."""
        self.enabled = False
        self.buffer = ""
    
    def available(self):
        """Return number of bytes available for reading."""
        return len(self.buffer)
    
    def read(self, size=None):
        """Read data from the buffer."""
        if not self.buffer:
            return -1
        if size is None or size >= len(self.buffer):
            result = self.buffer
            self.buffer = ""
        else:
            result = self.buffer[:size]
            self.buffer = self.buffer[size:]
        return result
    
    def readString(self):
        """Read data as string."""
        result = self.buffer
        self.buffer = ""
        return result
    
    def write(self, data):
        """Write data to the buffer (simulating transmission)."""
        if isinstance(data, bytes):
            data = data.decode('utf-8', errors='ignore')
        elif not isinstance(data, str):
            data = str(data)
        self.received_data.append(data)
        return len(data)
    
    def print(self, data):
        """Print data to the buffer."""
        return self.write(data)
    
    def println(self, data=""):
        """Print data with newline to the buffer."""
        if data:
            return self.write(str(data) + "\n")
        else:
            return self.write("\n")
    
    def flush(self):
        """Flush the buffer."""
        self.buffer = ""
    
    def clear_buffer(self):
        """Clear the receive buffer."""
        self.buffer = ""
    
    def add_data(self, data):
        """Add data to the receive buffer for testing."""
        if isinstance(data, bytes):
            data = data.decode('utf-8', errors='ignore')
        elif not isinstance(data, str):
            data = str(data)
        self.buffer += data
