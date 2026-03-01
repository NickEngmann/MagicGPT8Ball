"""embedded_mocks.py — Mock implementations of Arduino functions for testing."""


def arduino_map(x, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def arduino_constrain(val, low, high):
    """Constrain a value to be within a range."""
    if val < low:
        return low
    elif val > high:
        return high
    return val


class MockUART:
    """Mock UART for testing embedded code."""
    
    def __init__(self, port=None, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.buffer = b''
        self.open = True
    
    def write(self, data):
        """Write data to the mock UART."""
        if isinstance(data, str):
            data = data.encode()
        self.buffer += data
        return len(data)
    
    def read(self, size=1):
        """Read data from the mock UART."""
        result = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return result
    
    def readinto(self, buf):
        """Read data into a buffer."""
        size = min(len(buf), len(self.buffer))
        for i in range(size):
            buf[i] = self.buffer[i]
        self.buffer = self.buffer[size:]
        return size
    
    def readline(self):
        """Read a line from the mock UART."""
        if b'\n' in self.buffer:
            idx = self.buffer.index(b'\n') + 1
            result = self.buffer[:idx]
            self.buffer = self.buffer[idx:]
            return result
        result = self.buffer
        self.buffer = b''
        return result
    
    def any(self):
        """Check if there's any data to read."""
        return len(self.buffer) > 0
    
    def close(self):
        """Close the mock UART."""
        self.open = False
