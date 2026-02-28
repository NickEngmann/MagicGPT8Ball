"""Mock implementations for embedded C functions."""


def arduino_map(x, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def arduino_constrain(x, a, b):
    """Constrain a value between two bounds."""
    if x < a:
        return a
    if x > b:
        return b
    return x


class MockUART:
    """Mock UART class for testing."""
    
    def __init__(self):
        self.buffer = ""
    
    def write(self, data):
        """Write data to the buffer."""
        if isinstance(data, bytes):
            data = data.decode('utf-8', errors='ignore')
        self.buffer += data
    
    def read(self):
        """Read and clear the buffer."""
        data = self.buffer
        self.buffer = ""
        return data
    
    def flush(self):
        """Flush the buffer."""
        self.buffer = ""
