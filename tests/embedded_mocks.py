"""Mock functions for Arduino/PlatformIO testing in Python."""


def arduino_map(x, in_min, in_max, out_min, out_max):
    """Arduino map() function - remaps a number from one range to another."""
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def arduino_constrain(x, a, b):
    """Arduino constrain() function - constrains a value to be within a range."""
    if x < a:
        return a
    elif x > b:
        return b
    return x


class MockUART:
    """Mock UART class for testing serial communication."""
    
    def __init__(self, tx=1, rx=3, baudrate=9600):
        self.tx = tx
        self.rx = rx
        self.baudrate = baudrate
        self.buffer = b""
        self.enabled = True
    
    def write(self, data):
        """Write data to the mock UART."""
        if isinstance(data, str):
            data = data.encode()
        self.buffer += data
        return len(data)
    
    def read(self, size=-1):
        """Read data from the mock UART."""
        if size == -1:
            result = self.buffer
            self.buffer = b""
            return result
        result = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return result
    
    def available(self):
        """Return the number of bytes available to read."""
        return len(self.buffer)
    
    def flush(self):
        """Flush the buffer."""
        self.buffer = b""
