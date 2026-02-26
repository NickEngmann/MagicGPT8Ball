"""Mock functions for Arduino/PlatformIO environments."""

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
    """Mock UART interface for testing."""
    def __init__(self):
        self.buffer = []
    
    def write(self, data):
        self.buffer.append(data)
    
    def read(self, size=-1):
        if size == -1:
            result = b''.join(self.buffer)
            self.buffer = []
            return result
        result = b''.join(self.buffer[:size])
        self.buffer = self.buffer[size:]
        return result
