"""embedded_mocks.py — Mocks for PlatformIO/Arduino testing.

Provides Python implementations of common Arduino functions for testing.
"""


def arduino_map(value, from_low, from_high, to_low, to_high):
    """Map a value from one range to another (Arduino map function)."""
    return int((value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low)


def arduino_constrain(value, low, high):
    """Constrain a value to be within a range (Arduino constrain function)."""
    if value < low:
        return low
    if value > high:
        return high
    return value


class MockUART:
    """Mock UART class for testing serial communication."""
    
    def __init__(self):
        self.buffer = []
        self.baud_rate = None
        
    def begin(self, baud_rate):
        """Initialize UART with baud rate."""
        self.baud_rate = baud_rate
        self.buffer = []
        
    def print(self, data):
        """Print data to UART buffer."""
        self.buffer.append(str(data))
        
    def println(self, data=""):
        """Print data with newline to UART buffer."""
        self.buffer.append(str(data))
        
    def available(self):
        """Check if data is available in buffer."""
        return len(self.buffer) > 0
        
    def read(self):
        """Read data from buffer."""
        if self.buffer:
            return self.buffer.pop(0)
        return -1
        
    def flush(self):
        """Clear the buffer."""
        self.buffer = []
