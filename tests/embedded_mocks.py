"""Mock module for Arduino helper functions and hardware mocks."""


def arduino_map(x, in_min, in_max, out_min, out_max):
    """Re-implementation of Arduino's map() function."""
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def arduino_constrain(val, min_val, max_val):
    """Re-implementation of Arduino's constrain() function."""
    if val < min_val:
        return min_val
    elif val > max_val:
        return max_val
    return val


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
