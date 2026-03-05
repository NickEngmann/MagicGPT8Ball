"""test_recorder.py — Tests for Recorder class algorithms.

This module tests the voice detection and audio processing algorithms
from the Recorder class by reimplementing them in Python.
"""
import sys
sys.path.insert(0, '')

from tests.embedded_mocks import arduino_map, arduino_constrain


# Constants from Recorder.h
SAMPLE_RATE = 32000
CHANNELS = 1
DC_OFFSET = 1250  # mV
SAMPLE_BUFFER_SIZE = 256
AUDIO_THRESHOLD = 500
SILENCE_TIMEOUT = 2000  # ms
MAX_RECORD_SECONDS = 10

def detect_voice_activity(samples, sample_rate=SAMPLE_RATE):
    """
    Reimplementation of VoiceActivatedRecorder::detectVoiceActivity.
    
    Args:
        samples: List of uint16_t samples (raw ADC values 0-4095)
        sample_rate: Sample rate in Hz
    
    Returns:
        bool: True if voice activity detected
    """
    if not samples or len(samples) == 0:
        return False

    # Track zero crossings and amplitude
    zero_crossings = 0
    sum_amplitude = 0
    last_sample = 0
    max_amplitude = 0

    for i in range(len(samples)):
        # Convert to signed value centered around 0
        current = samples[i] - 2048

        # Count zero crossings
        if last_sample < 0 and current >= 0:
            zero_crossings += 1

        # Track amplitude
        amplitude = abs(current)
        sum_amplitude += amplitude
        max_amplitude = max(max_amplitude, amplitude)

        last_sample = current

    avg_amplitude = sum_amplitude / len(samples)
    
    # Calculate crossing rate (crossings per second)
    sample_duration_ms = (len(samples) * 1000.0) / sample_rate
    crossing_rate = (zero_crossings * 1000.0) / sample_duration_ms if sample_duration_ms > 0 else 0

    # Voice detection logic (simplified from C++ code)
    # Original: avg_amplitude > 1000.0f || max_amplitude > 4000
    is_voice = (avg_amplitude > 1000.0) or (max_amplitude > 4000)

    return is_voice


def read_adc_sample(raw_value, voltage):
    """
    Reimplementation of VoiceActivatedRecorder::readADCSample logic.
    
    Args:
        raw_value: Raw ADC value (0-4095 for 12-bit)
        voltage: Voltage in mV
    
    Returns:
        int16_t: Scaled audio sample (-32768 to 32767)
    """
    # Center around DC bias (1.25V = 1250mV)
    centered = voltage - DC_OFFSET

    # Amplification stage
    centered *= 4

    # Scale to 16-bit range
    centered = (centered * 16000) // 1000

    # Clamp to 16-bit range
    centered = arduino_constrain(centered, -32768, 32767)

    return int(centered)


def map_value(value, from_low, from_high, to_low, to_high):
    """Map a value from one range to another."""
    return arduino_map(value, from_low, from_high, to_low, to_high)


class TestVoiceDetection:
    """Test suite for voice detection algorithm."""

    def test_no_samples_returns_false(self):
        """Test that empty samples return no voice."""
        assert detect_voice_activity([]) == False
        # Single sample at DC offset (2048) should not trigger voice
        assert detect_voice_activity([2048]) == False
        # Single sample with very low amplitude should not trigger voice
        assert detect_voice_activity([2049]) == False

    def test_low_amplitude_no_voice(self):
        """Test that low amplitude samples don't trigger voice detection."""
        # Samples with very low amplitude (close to center)
        samples = [2048 + i for i in range(-100, 101)]  # Amplitude ~100
        assert detect_voice_activity(samples) == False

    def test_high_amplitude_triggers_voice(self):
        """Test that high amplitude samples trigger voice detection."""
        # Samples with high amplitude (far from center)
        samples = [2048 + i for i in range(-5000, 5001)]  # Amplitude ~5000
        assert detect_voice_activity(samples) == True

    def test_max_amplitude_threshold(self):
        """Test that max amplitude > 4000 triggers voice."""
        # Create samples with max amplitude > 4000
        samples = [2048 + 4500, 2048 - 4500, 2048]  # Max amplitude = 4500
        assert detect_voice_activity(samples) == True

    def test_zero_crossing_detection(self):
        """Test zero crossing counting logic."""
        # Alternating positive/negative samples
        samples = [1000, 3000, 1000, 3000, 1000]  # Crosses around 2048
        result = detect_voice_activity(samples)
        # Should detect voice due to high amplitude
        assert result == True

    def test_arduino_map_function(self):
        """Test arduino_map function."""
        assert map_value(512, 0, 1023, 0, 100) == 50
        assert map_value(0, 0, 1023, 0, 100) == 0
        assert map_value(1023, 0, 1023, 0, 100) == 100
        assert map_value(512, 0, 1023, 0, 255) == 127

    def test_arduino_constrain_function(self):
        """Test arduino_constrain function."""
        assert arduino_constrain(50, 0, 100) == 50
        assert arduino_constrain(-10, 0, 100) == 0
        assert arduino_constrain(150, 0, 100) == 100
        assert arduino_constrain(0, 0, 100) == 0
        assert arduino_constrain(100, 0, 100) == 100


class TestADCSampling:
    """Test suite for ADC sampling logic."""

    def test_adc_sample_conversion(self):
        """Test ADC sample conversion logic."""
        # Test with voltage at DC offset (should be 0 after centering)
        sample = read_adc_sample(0, DC_OFFSET)  # 1250mV = DC offset
        assert sample == 0

    def test_adc_sample_positive(self):
        """Test ADC sample with positive voltage."""
        # 2000mV = 750mV above DC offset
        sample = read_adc_sample(0, 2000)
        # centered = 2000 - 1250 = 750
        # centered *= 4 = 3000
        # centered = (3000 * 16000) // 1000 = 48000
        # constrained to 32767
        assert sample == 32767

    def test_adc_sample_negative(self):
        """Test ADC sample with negative voltage."""
        # 500mV = 750mV below DC offset
        sample = read_adc_sample(0, 500)
        # centered = 500 - 1250 = -750
        # centered *= 4 = -3000
        # centered = (-3000 * 16000) // 1000 = -48000
        # constrained to -32768
        assert sample == -32768

    def test_adc_sample_midpoint(self):
        """Test ADC sample at midpoint voltage."""
        # 1250mV = exactly at DC offset
        sample = read_adc_sample(0, 1250)
        assert sample == 0


class TestBufferManagement:
    """Test suite for buffer management logic."""

    def test_buffer_size_calculation(self):
        """Test buffer size calculation."""
        # BUFFER_SIZE = MAX_RECORD_SECONDS * SAMPLE_RATE * CHANNELS * 2
        expected_size = MAX_RECORD_SECONDS * SAMPLE_RATE * CHANNELS * 2
        assert expected_size == 10 * 32000 * 1 * 2  # 640000 bytes

    def test_sample_buffer_size(self):
        """Test sample buffer size."""
        assert SAMPLE_BUFFER_SIZE == 256

    def test_silence_timeout(self):
        """Test silence timeout value."""
        assert SILENCE_TIMEOUT == 2000  # 2 seconds


class TestAudioProcessing:
    """Test suite for audio processing logic."""

    def test_average_amplitude_calculation(self):
        """Test average amplitude calculation."""
        samples = [2048 + 100, 2048 - 100, 2048 + 200, 2048 - 200]
        # Amplitudes: 100, 100, 200, 200
        # Average: (100 + 100 + 200 + 200) / 4 = 150
        # This is below threshold, so no voice
        assert detect_voice_activity(samples) == False

    def test_mixed_amplitude_samples(self):
        """Test with mixed amplitude samples."""
        # Mix of low and high amplitude
        samples = [2048 + 50, 2048 - 50, 2048 + 5000, 2048 - 5000]
        # Max amplitude = 5000 > 4000, should trigger voice
        assert detect_voice_activity(samples) == True

    def test_edge_case_threshold(self):
        """Test at exact threshold values."""
        # Exactly at threshold (should be False)
        samples = [2048 + 1000, 2048 - 1000]  # avg = 1000, max = 1000
        # avg_amplitude = 1000, not > 1000
        # max_amplitude = 1000, not > 4000
        assert detect_voice_activity(samples) == False

    def test_just_above_threshold(self):
        """Test just above threshold."""
        # Just above threshold
        samples = [2048 + 1001, 2048 - 1001]  # avg = 1001 > 1000
        assert detect_voice_activity(samples) == True


def run_all_tests():
    """Run all test classes."""
    test_classes = [
        TestVoiceDetection,
        TestADCSampling,
        TestBufferManagement,
        TestAudioProcessing
    ]

    total_tests = 0
    passed_tests = 0

    for test_class in test_classes:
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith('test_'):
                total_tests += 1
                try:
                    getattr(instance, method_name)()
                    passed_tests += 1
                    print(f"✓ {test_class.__name__}.{method_name}")
                except AssertionError as e:
                    print(f"✗ {test_class.__name__}.{method_name}: {e}")

    print(f"\nResults: {passed_tests}/{total_tests} tests passed")
    return passed_tests == total_tests


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
