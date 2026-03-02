"""Mock modules for embedded system testing."""

def arduino_map(value, from_low, from_high, to_low, to_high):
    """Map a value from one range to another."""
    return int((value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low)

def arduino_constrain(value, min_val, max_val):
    """Constrain a value between min and max."""
    return max(min_val, min(value, max_val))

class MockUART:
    """Mock UART class for testing."""
    def __init__(self):
        self.buffer = []
    
    def write(self, data):
        self.buffer.append(data)
        return len(data) if isinstance(data, bytes) else 1
    
    def read(self):
        return self.buffer.pop(0) if self.buffer else None
    
    def available(self):
        return len(self.buffer)
    
    def flush(self):
        self.buffer.clear()
