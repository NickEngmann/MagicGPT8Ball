"""Mock implementations of Arduino functions for testing."""


def arduino_map(x, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def arduino_constrain(x, a, b):
    """Constrain a value between two bounds."""
    if x < a:
        return a
    elif x > b:
        return b
    return x


class MockUART:
    """Mock UART interface for testing."""
    def __init__(self, tx=1, rx=3, baudrate=9600):
        self.tx = tx
        self.rx = rx
        self.baudrate = baudrate
        self._buffer = b""
        self._enabled = True

    def write(self, data):
        """Write data to the mock UART."""
        if isinstance(data, str):
            data = data.encode()
        self._buffer += data
        return len(data)

    def read(self, size=-1):
        """Read data from the mock UART."""
        if size == -1:
            result = self._buffer
            self._buffer = b""
            return result
        result = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return result

    def readinto(self, buf):
        """Read data into a buffer."""
        size = len(buf)
        data = self.read(size)
        for i, b in enumerate(data):
            buf[i] = b
        return len(data)

    def readline(self):
        """Read a line from the mock UART."""
        if b"\n" in self._buffer:
            idx = self._buffer.index(b"\n") + 1
            result = self._buffer[:idx]
            self._buffer = self._buffer[idx:]
            return result
        result = self._buffer
        self._buffer = b""
        return result

    def any(self):
        """Check if there's any data available."""
        return len(self._buffer) > 0

    def flush(self):
        """Flush the UART buffer."""
        self._buffer = b""
