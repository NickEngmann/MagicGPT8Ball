"""embedded_mocks.py — Mock implementations for Arduino-like functions."""


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
        self.buffer = b""
        self.open = True
    
    def write(self, data):
        """Write data to the mock UART."""
        if not self.open:
            raise RuntimeError("UART is closed")
        self.buffer += data if isinstance(data, bytes) else data.encode()
        return len(data)
    
    def read(self, size=1):
        """Read data from the mock UART."""
        if not self.open:
            raise RuntimeError("UART is closed")
        result = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return result
    
    def readinto(self, buf):
        """Read data into a buffer."""
        if not self.open:
            raise RuntimeError("UART is closed")
        size = min(len(buf), len(self.buffer))
        buf[:size] = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return size
    
    def readline(self):
        """Read a line from the mock UART."""
        if not self.open:
            raise RuntimeError("UART is closed")
        if b"\n" in self.buffer:
            idx = self.buffer.index(b"\n") + 1
            result = self.buffer[:idx]
            self.buffer = self.buffer[idx:]
            return result
        return b""
    
    def close(self):
        """Close the mock UART."""
        self.open = False
    
    def flush(self):
        """Flush the buffer."""
        self.buffer = b""
