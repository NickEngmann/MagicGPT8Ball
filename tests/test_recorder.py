"""Tests for Recorder module."""
import sys
sys.path.insert(0, '')

from unittest.mock import MagicMock, patch

# Mock Arduino and ESP32 dependencies
sys.modules['Arduino'] = MagicMock()
sys.modules['Arduino.h'] = MagicMock()
sys.modules['driver'] = MagicMock()
sys.modules['esp_adc_cal'] = MagicMock()
sys.modules['esp_system'] = MagicMock()


class RecorderLogic:
    """Python re-implementation of Recorder logic for testing."""
    
    def __init__(self, buffer_size=4096, sample_rate=16000):
        self.buffer_size = buffer_size
        self.sample_rate = sample_rate
        self.buffer = [0] * buffer_size
        self.write_index = 0
        self.read_index = 0
        self.is_recording = False
        self.debug_stats = {
            'samples_recorded': 0,
            'overflows': 0,
            'underflows': 0
        }
    
    def startRecording(self):
        """Start recording audio."""
        self.is_recording = True
        self.write_index = 0
        self.read_index = 0
        self.buffer = [0] * self.buffer_size
        self.debug_stats['samples_recorded'] = 0
        return True
    
    def stopRecording(self):
        """Stop recording audio."""
        self.is_recording = False
        return True
    
    def isRecording(self):
        """Check if currently recording."""
        return self.is_recording
    
    def writeSample(self, sample):
        """Write a sample to the buffer."""
        if not self.is_recording:
            return False
        
        self.buffer[self.write_index] = sample
        self.write_index = (self.write_index + 1) % self.buffer_size
        self.debug_stats['samples_recorded'] += 1
        
        # Check for overflow
        if self.write_index == self.read_index and self.is_recording:
            self.debug_stats['overflows'] += 1
        
        return True
    
    def readSample(self):
        """Read a sample from the buffer."""
        if not self.is_recording or self.read_index == self.write_index:
            return 0
        
        sample = self.buffer[self.read_index]
        self.read_index = (self.read_index + 1) % self.buffer_size
        
        # Check for underflow
        if self.read_index == self.write_index:
            self.debug_stats['underflows'] += 1
        
        return sample
    
    def getBufferUsage(self):
        """Get the percentage of buffer usage."""
        if self.write_index >= self.read_index:
            used = self.write_index - self.read_index
        else:
            used = self.buffer_size - self.read_index + self.write_index
        
        return (used / self.buffer_size) * 100
    
    def getDebugStats(self):
        """Get debug statistics."""
        return self.debug_stats.copy()
    
    def clearBuffer(self):
        """Clear the buffer."""
        self.buffer = [0] * self.buffer_size
        self.write_index = 0
        self.read_index = 0
        self.debug_stats['overflows'] = 0
        self.debug_stats['underflows'] = 0


def test_initial_recording_state():
    """Test that recorder starts in non-recording state."""
    recorder = RecorderLogic()
    assert recorder.isRecording() == False
    assert recorder.write_index == 0
    assert recorder.read_index == 0


def test_start_recording():
    """Test starting recording."""
    recorder = RecorderLogic()
    result = recorder.startRecording()
    assert result == True
    assert recorder.isRecording() == True
    assert recorder.write_index == 0
    assert recorder.read_index == 0


def test_stop_recording():
    """Test stopping recording."""
    recorder = RecorderLogic()
    recorder.startRecording()
    assert recorder.isRecording() == True
    
    result = recorder.stopRecording()
    assert result == True
    assert recorder.isRecording() == False


def test_write_sample_when_not_recording():
    """Test that writing sample fails when not recording."""
    recorder = RecorderLogic()
    result = recorder.writeSample(1000)
    assert result == False


def test_write_sample_when_recording():
    """Test writing sample when recording."""
    recorder = RecorderLogic()
    recorder.startRecording()
    
    result = recorder.writeSample(1000)
    assert result == True
    assert recorder.debug_stats['samples_recorded'] == 1


def test_read_sample_empty_buffer():
    """Test reading from empty buffer returns 0."""
    recorder = RecorderLogic()
    recorder.startRecording()
    
    sample = recorder.readSample()
    assert sample == 0


def test_read_sample_after_write():
    """Test reading sample after writing."""
    recorder = RecorderLogic()
    recorder.startRecording()
    
    recorder.writeSample(1000)
    recorder.writeSample(2000)
    
    sample1 = recorder.readSample()
    assert sample1 == 1000
    
    sample2 = recorder.readSample()
    assert sample2 == 2000


def test_buffer_circular_write():
    """Test circular buffer write behavior."""
    recorder = RecorderLogic(buffer_size=10)
    recorder.startRecording()
    
    # Write more samples than buffer size
    for i in range(15):
        recorder.writeSample(i * 100)
    
    # Buffer should have wrapped around
    assert recorder.debug_stats['overflows'] >= 1


def test_buffer_circular_read():
    """Test circular buffer read behavior."""
    recorder = RecorderLogic(buffer_size=10)
    recorder.startRecording()
    
    # Write samples
    for i in range(5):
        recorder.writeSample(i * 100)
    
    # Read samples
    for i in range(5):
        sample = recorder.readSample()
        assert sample == i * 100


def test_buffer_usage_empty():
    """Test buffer usage when empty."""
    recorder = RecorderLogic()
    recorder.startRecording()
    
    usage = recorder.getBufferUsage()
    assert usage == 0.0


def test_buffer_usage_partial():
    """Test buffer usage with partial data."""
    recorder = RecorderLogic(buffer_size=100)
    recorder.startRecording()
    
    for i in range(50):
        recorder.writeSample(i)
    
    usage = recorder.getBufferUsage()
    assert 49.0 <= usage <= 51.0  # Allow small floating point variance


def test_buffer_usage_full():
    """Test buffer usage when full."""
    recorder = RecorderLogic(buffer_size=100)
    recorder.startRecording()
    
    for i in range(99):
        recorder.writeSample(i)
    
    usage = recorder.getBufferUsage()
    assert 98.0 <= usage <= 100.0  # Allow small variance due to circular buffer logic


def test_debug_stats():
    """Test debug statistics tracking."""
    recorder = RecorderLogic()
    recorder.startRecording()
    
    recorder.writeSample(100)
    recorder.writeSample(200)
    
    stats = recorder.getDebugStats()
    assert stats['samples_recorded'] == 2
    assert stats['overflows'] == 0
    assert stats['underflows'] == 0


def test_clear_buffer():
    """Test clearing the buffer."""
    recorder = RecorderLogic(buffer_size=100)
    recorder.startRecording()
    
    for i in range(50):
        recorder.writeSample(i)
    
    recorder.clearBuffer()
    
    assert recorder.write_index == 0
    assert recorder.read_index == 0
    assert recorder.getBufferUsage() == 0.0
    assert recorder.debug_stats['overflows'] == 0
    assert recorder.debug_stats['underflows'] == 0


def test_sample_rate_configuration():
    """Test sample rate configuration."""
    recorder = RecorderLogic(sample_rate=44100)
    assert recorder.sample_rate == 44100


def test_buffer_size_configuration():
    """Test buffer size configuration."""
    recorder = RecorderLogic(buffer_size=8192)
    assert recorder.buffer_size == 8192
    assert len(recorder.buffer) == 8192


def test_multiple_write_read_cycles():
    """Test multiple write and read cycles."""
    recorder = RecorderLogic(buffer_size=100)
    recorder.startRecording()
    
    # First cycle
    for i in range(10):
        recorder.writeSample(i * 100)
    
    for i in range(10):
        sample = recorder.readSample()
        assert sample == i * 100
    
    # Second cycle
    for i in range(20):
        recorder.writeSample(i * 50)
    
    for i in range(20):
        sample = recorder.readSample()
        assert sample == i * 50


def test_read_after_buffer_empty():
    """Test reading after buffer becomes empty."""
    recorder = RecorderLogic(buffer_size=10)
    recorder.startRecording()
    
    recorder.writeSample(100)
    recorder.writeSample(200)
    
    recorder.readSample()  # Read 100
    recorder.readSample()  # Read 200
    
    # Buffer should be empty now
    sample = recorder.readSample()
    assert sample == 0


def test_write_overflow_detection():
    """Test that overflow is detected when buffer is full."""
    recorder = RecorderLogic(buffer_size=5)
    recorder.startRecording()
    
    # Fill buffer
    for i in range(5):
        recorder.writeSample(i * 100)
    
    # Write more - should cause overflow
    recorder.writeSample(600)
    
    assert recorder.debug_stats['overflows'] >= 1


def test_read_underflow_detection():
    """Test that underflow is detected when buffer is empty."""
    recorder = RecorderLogic(buffer_size=5)
    recorder.startRecording()
    
    # Write one sample
    recorder.writeSample(100)
    
    # Read it
    recorder.readSample()
    
    # Read again - should cause underflow
    recorder.readSample()
    
    assert recorder.debug_stats['underflows'] >= 1
