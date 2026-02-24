"""
Mock implementations of Arduino functions for testing C code in Python.
"""

def arduino_map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def arduino_constrain(x, a, b):
    return max(a, min(x, b))

class MockUART:
    def __init__(self):
        self.buffer = []
        self.received = []

    def write(self, data):
        self.buffer.append(data)

    def read(self, size=1):
        if self.received:
            return self.received.pop(0).encode()[:size]
        return b""

    def available(self):
        return len(self.received)

    def println(self, msg):
        self.buffer.append(msg + "\n")

    def flush(self):
        pass

# Global instance for testing
uart = MockUART()