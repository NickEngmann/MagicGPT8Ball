"""embedded_mocks.py — Mock implementations for embedded C functions."""


def arduino_map(x, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def arduino_constrain(x, a, b):
    """Constrain a value to be within a range."""
    if x < a:
        return a
    if x > b:
        return b
    return x


class MockUART:
    """Mock UART interface for testing."""
    
    def __init__(self, port=None, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self._buffer = b""
        self._connected = False
    
    def open(self):
        self._connected = True
    
    def close(self):
        self._connected = False
    
    def is_open(self):
        return self._connected
    
    def write(self, data):
        if not self._connected:
            raise RuntimeError("Port not open")
        return len(data)
    
    def read(self, size=1):
        if not self._connected:
            raise RuntimeError("Port not open")
        result = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return result
    
    def read_until(self, terminator=b"\n"):
        if not self._connected:
            raise RuntimeError("Port not open")
        idx = self._buffer.find(terminator)
        if idx == -1:
            result = self._buffer
            self._buffer = b""
        else:
            result = self._buffer[:idx+1]
            self._buffer = self._buffer[idx+1:]
        return result
    
    def available(self):
        return len(self._buffer)
    
    def flush(self):
        self._buffer = b""
    
    def push_data(self, data):
        """Simulate incoming data (for testing)."""
        self._buffer += data
