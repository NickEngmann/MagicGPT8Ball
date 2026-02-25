"""Mock implementations for embedded C++ functions."""

class millis_mock:
    """Mock for Arduino millis() function."""
    current_time = 0
    
    @staticmethod
    def get():
        return millis_mock.current_time


class ArduinoMock:
    """Mock Arduino environment."""
    
    @staticmethod
    def map(value, fromLow, fromHigh, toLow, toHigh):
        """Reimplementation of Arduino's map() function."""
        return (value - fromLow) * (toHigh - toLow) // (fromHigh - fromLow) + toLow
    
    @staticmethod
    def constrain(val, min_val, max_val):
        """Reimplementation of Arduino's constrain() function."""
        return min(max(val, min_val), max_val)


# Aliases for compatibility
arduino_map = ArduinoMock.map
arduino_constrain = ArduinoMock.constrain


class MockUART:
    """Mock UART serial communication."""
    def __init__(self):
        self.buffer = []
        self.baud_rate = 115200
    
    def begin(self, baud_rate):
        self.baud_rate = baud_rate
    
    def print(self, text):
        self.buffer.append(str(text))
    
    def println(self, text):
        self.buffer.append(str(text) + "\n")
    
    def printf(self, format_str, *args):
        self.buffer.append(format_str % args)
    
    def flush(self):
        pass
    
    def get_output(self):
        return "".join(self.buffer)
    
    def clear(self):
        self.buffer = []
