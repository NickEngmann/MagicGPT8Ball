"""Mock implementations for Arduino/C++ functions used in embedded systems testing."""


def arduino_map(x, in_min, in_max, out_min, out_max):
    """Map a value from one range to another (Arduino map function)."""
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def arduino_constrain(val, min_val, max_val):
    """Constrain a value to be within a range (Arduino constrain function)."""
    if val < min_val:
        return min_val
    elif val > max_val:
        return max_val
    return val


class MockUART:
    """Mock UART interface for testing."""
    
    def __init__(self, port=None, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.buffer = []
        self.is_open = True
    
    def write(self, data):
        """Write data to the mock UART."""
        if isinstance(data, str):
            self.buffer.append(data)
        elif isinstance(data, bytes):
            self.buffer.append(data.decode('utf-8', errors='ignore'))
        return len(data)
    
    def read(self, size=1):
        """Read data from the mock UART buffer."""
        if not self.buffer:
            return b''
        data = self.buffer.pop(0)
        return data[:size].encode('utf-8') if isinstance(data, str) else data[:size]
    
    def readline(self):
        """Read a line from the mock UART buffer."""
        if not self.buffer:
            return b''
        data = self.buffer.pop(0)
        return data.encode('utf-8') if isinstance(data, str) else data
    
    def close(self):
        """Close the mock UART."""
        self.is_open = False
    
    def flush(self):
        """Flush the mock UART buffer."""
        self.buffer = []
