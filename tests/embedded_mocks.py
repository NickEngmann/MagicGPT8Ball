"""embedded_mocks.py — Mock implementations for PlatformIO/Arduino testing.

Provides Python equivalents of common Arduino functions and hardware mocks
to test embedded C/C++ logic without actual hardware.
"""
import sys
from unittest.mock import MagicMock


def arduino_map(value, from_low, from_high, to_low, to_high):
    """Map a value from one range to another (Arduino map function)."""
    if from_low == from_high:
        return to_low
    return int((value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low)


def arduino_constrain(value, low, high):
    """Constrain a value between low and high (Arduino constrain function)."""
    if value < low:
        return low
    if value > high:
        return high
    return value


class MockUART:
    """Mock UART class for serial communication testing."""
    
    def __init__(self):
        self.data = []
        self.buffer_size = 0
    
    def begin(self, baud_rate):
        """Initialize UART with baud rate."""
        self.baud_rate = baud_rate
        self.data = []
    
    def print(self, data):
        """Print data to UART buffer."""
        self.data.append(str(data))
    
    def println(self, data=""):
        """Print data with newline to UART buffer."""
        self.data.append(str(data) + "\n")
    
    def available(self):
        """Check if data is available to read."""
        return len(self.data) > 0
    
    def read(self):
        """Read data from UART buffer."""
        if self.data:
            return self.data.pop(0)
        return None
    
    def flush(self):
        """Clear UART buffer."""
        self.data = []


class MockSPI:
    """Mock SPI class for SPI communication testing."""
    
    def __init__(self):
        self.data = []
    
    def begin(self):
        """Initialize SPI."""
        pass
    
    def setClockDivider(self, divider):
        """Set SPI clock divider."""
        pass
    
    def setBitOrder(self, order):
        """Set SPI bit order."""
        pass
    
    def setDataMode(self, mode):
        """Set SPI data mode."""
        pass
    
    def beginTransaction(self, settings):
        """Begin SPI transaction."""
        pass
    
    def endTransaction(self):
        """End SPI transaction."""
        pass
    
    def transfer(self, data):
        """Transfer data over SPI."""
        return data
    
    def write(self, data):
        """Write data to SPI."""
        self.data.append(data)
    
    def read(self):
        """Read data from SPI."""
        return 0


class MockI2C:
    """Mock I2C class for I2C communication testing."""
    
    def __init__(self):
        self.data = {}
    
    def begin(self):
        """Initialize I2C."""
        pass
    
    def setClock(self, clock_speed):
        """Set I2C clock speed."""
        pass
    
    def beginTransmission(self, address):
        """Begin I2C transmission."""
        pass
    
    def endTransmission(self):
        """End I2C transmission."""
        return 0
    
    def requestFrom(self, address, quantity):
        """Request data from I2C device."""
        return 0
    
    def read(self):
        """Read data from I2C."""
        return 0
    
    def write(self, data):
        """Write data to I2C."""
        pass


class MockGPIO:
    """Mock GPIO class for pin control testing."""
    
    def __init__(self):
        self.pin_states = {}
    
    def pinMode(self, pin, mode):
        """Set pin mode."""
        self.pin_states[pin] = mode
    
    def digitalWrite(self, pin, value):
        """Set digital pin value."""
        self.pin_states[pin] = value
    
    def digitalRead(self, pin):
        """Read digital pin value."""
        return self.pin_states.get(pin, 0)
    
    def analogWrite(self, pin, value):
        """Write analog value to pin."""
        self.pin_states[pin] = value
    
    def analogRead(self, pin):
        """Read analog value from pin."""
        return self.pin_states.get(pin, 0)


# Create singleton instances for convenience
mock_uart = MockUART()
mock_spi = MockSPI()
mock_i2c = MockI2C()
mock_gpio = MockGPIO()
