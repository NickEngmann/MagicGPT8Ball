"""Mock implementations for embedded C++ functions and classes."""


def arduino_map(x, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def arduino_constrain(x, a, b):
    """Constrain a value to be within a range."""
    if x < a:
        return a
    elif x > b:
        return b
    return x


class MockUART:
    """Mock UART class for testing."""
    
    def __init__(self, port=None, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.buffer = b''
        self.open = True
    
    def write(self, data):
        """Write data to the buffer."""
        if isinstance(data, str):
            data = data.encode()
        self.buffer += data
        return len(data)
    
    def read(self, size=1):
        """Read data from the buffer."""
        result = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return result
    
    def readinto(self, buf):
        """Read data into a buffer."""
        size = min(len(buf), len(self.buffer))
        buf[:size] = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return size
    
    def readline(self):
        """Read a line from the buffer."""
        if b'\n' in self.buffer:
            idx = self.buffer.index(b'\n') + 1
            result = self.buffer[:idx]
            self.buffer = self.buffer[idx:]
            return result
        return b''
    
    def available(self):
        """Return number of bytes available."""
        return len(self.buffer)
    
    def flush(self):
        """Flush the buffer."""
        self.buffer = b''
    
    def close(self):
        """Close the mock UART."""
        self.open = False
