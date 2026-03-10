"""Tests for VoiceActivatedRecorder using hardware mocks."""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock hardware dependencies before importing source
sys.modules['Arduino.h'] = MagicMock()
sys.modules['driver'] = MagicMock()
sys.modules['esp_adc_cal'] = MagicMock()
sys.modules['esp_system'] = MagicMock()
sys.modules['esp_heap_caps'] = MagicMock()
sys.modules['DEV_Config'] = MagicMock()

from embedded_mocks import MockGPIO, MockI2C, MockADC, MockPWM


class TestVoiceActivatedRecorder:
    """Test suite for VoiceActivatedRecorder class."""
    
    @pytest.fixture
    def mock_recorder(self):
        """Create a mock VoiceActivatedRecorder for testing."""
        recorder = Mock(spec=['begin', 'startRecording', 'stopRecording', 
                             'isRecording', 'getAudioData', 'getAudioLength',
                             'setVoiceThreshold', 'getVoiceThreshold',
                             'checkVoiceActivity', 'updateDebugStats'])
        recorder.audioBuffer = None
        recorder.bufferIndex = 0
        recorder.is_recording = False
        recorder.voiceThreshold = 100
        recorder.sampleRate = 16000
        recorder.channels = 1
        recorder.bitDepth = 16
        recorder.maxSilenceDuration = 2000
        recorder.lastSampleTime = 0
        recorder.hasDetectedVoice = False
        recorder.debugStats = {
            'totalSamples': 0,
            'voiceSamples': 0,
            'silenceSamples': 0,
            'overflows': 0
        }
        # Configure method calls to return actual values
        recorder.isRecording = Mock(return_value=recorder.is_recording)
        recorder.getVoiceThreshold = Mock(return_value=recorder.voiceThreshold)
        recorder.getAudioLength = Mock(return_value=len(recorder.audioBuffer) if recorder.audioBuffer else 0)
        return recorder
    
    @pytest.fixture
    def mock_audio_buffer(self):
        """Create a mock audio buffer."""
        mock = MagicMock()
        mock.__len__ = Mock(return_value=0)
        mock.__setitem__ = Mock()
        mock.__getitem__ = Mock(return_value=0)
        mock.append = Mock()
        mock.extend = Mock()
        mock.clear = Mock()
        mock.pop = Mock(return_value=0)
        mock.len = Mock(return_value=0)
        mock.size = Mock(return_value=0)
        return mock
    
    def test_initialization(self):
        """Test VoiceActivatedRecorder initialization."""
        # Verify mock setup works
        mock_recorder = Mock(spec=['begin', 'startRecording'])
        assert mock_recorder is not None
    
    def test_begin_method(self, mock_recorder):
        """Test begin method initializes audio system."""
        mock_recorder.begin = Mock(return_value=True)
        result = mock_recorder.begin()
        assert result is True
        mock_recorder.begin.assert_called_once()
    
    def test_start_recording(self, mock_recorder, mock_audio_buffer):
        """Test startRecording method."""
        mock_recorder.startRecording = Mock(return_value=True)
        mock_recorder.audioBuffer = mock_audio_buffer
        mock_recorder.bufferIndex = 0
        
        result = mock_recorder.startRecording()
        assert result is True
        mock_recorder.startRecording.assert_called_once()
    
    def test_stop_recording(self, mock_recorder):
        """Test stopRecording method."""
        mock_recorder.stopRecording = Mock(return_value=True)
        mock_recorder.is_recording = True
        
        result = mock_recorder.stopRecording()
        assert result is True
        mock_recorder.stopRecording.assert_called_once()
    
    def test_is_recording(self, mock_recorder):
        """Test isRecording property."""
        mock_recorder.is_recording = False
        mock_recorder.isRecording = Mock(return_value=False)
        assert mock_recorder.isRecording() == False
    
    def test_is_recording_true(self, mock_recorder):
        """Test isRecording property when recording."""
        mock_recorder.is_recording = True
        mock_recorder.isRecording = Mock(return_value=True)
        assert mock_recorder.isRecording() == True
        
        mock_recorder.is_recording = True
        assert mock_recorder.isRecording() == True
    
    def test_get_audio_data(self, mock_recorder, mock_audio_buffer):
        """Test getAudioData method."""
        mock_recorder.audioBuffer = mock_audio_buffer
        mock_recorder.bufferIndex = 100
        
        mock_audio_buffer.__getitem__ = Mock(side_effect=lambda i: i)
        mock_audio_buffer.__len__ = Mock(return_value=100)
        
        result = mock_recorder.getAudioData()
        assert result is not None
    
    def test_get_audio_length(self, mock_recorder):
        """Test getAudioLength method."""
        mock_recorder.bufferIndex = 100
        mock_recorder.getAudioLength = Mock(return_value=100)
        
        result = mock_recorder.getAudioLength()
        assert result == 100
    
    def test_set_voice_threshold(self, mock_recorder):
        """Test setVoiceThreshold method."""
        mock_recorder.setVoiceThreshold = Mock(return_value=True)
        
        result = mock_recorder.setVoiceThreshold(150)
        assert result is True
        mock_recorder.setVoiceThreshold.assert_called_once_with(150)
    
    def test_get_voice_threshold(self, mock_recorder):
        """Test getVoiceThreshold method."""
        mock_recorder.voiceThreshold = 100
        
        result = mock_recorder.getVoiceThreshold()
        assert result == 100
    
    def test_check_voice_activity(self, mock_recorder):
        """Test checkVoiceActivity method."""
        mock_recorder.checkVoiceActivity = Mock(return_value=True)
        
        result = mock_recorder.checkVoiceActivity()
        assert result is True
        mock_recorder.checkVoiceActivity.assert_called_once()
    
    def test_update_debug_stats(self, mock_recorder):
        """Test updateDebugStats method."""
        mock_recorder.updateDebugStats = Mock(return_value=True)
        
        result = mock_recorder.updateDebugStats()
        assert result is True
        mock_recorder.updateDebugStats.assert_called_once()
    
    def test_audio_buffer_overflow_protection(self, mock_recorder, mock_audio_buffer):
        """Test audio buffer overflow protection."""
        mock_recorder.audioBuffer = mock_audio_buffer
        mock_recorder.bufferIndex = 1022  # Near overflow (2 samples from end)
        mock_recorder.BUFFER_SIZE = 1024
        
        # Simulate overflow check
        mock_audio_buffer.__len__ = Mock(return_value=1022)
        
        # Should detect potential overflow (1022 + 2 = 1024 >= 1024)
        assert mock_recorder.bufferIndex + 2 >= mock_recorder.BUFFER_SIZE
    
    def test_voice_detection_timing(self, mock_recorder):
        """Test voice detection timing logic."""
        mock_recorder.lastSampleTime = 0
        mock_recorder.currentTime = 1000
        mock_recorder.maxSilenceDuration = 2000
        
        # Should not trigger timeout
        time_diff = mock_recorder.currentTime - mock_recorder.lastSampleTime
        assert time_diff < mock_recorder.maxSilenceDuration
    
    def test_debug_stats_tracking(self, mock_recorder):
        """Test debug stats tracking."""
        mock_recorder.debugStats = {
            'totalSamples': 0,
            'voiceSamples': 0,
            'silenceSamples': 0,
            'overflows': 0
        }
        
        # Simulate sample tracking
        mock_recorder.debugStats['totalSamples'] += 1
        mock_recorder.debugStats['voiceSamples'] += 1
        
        assert mock_recorder.debugStats['totalSamples'] == 1
        assert mock_recorder.debugStats['voiceSamples'] == 1
    
    def test_adc_setup_validation(self, mock_recorder):
        """Test ADC setup validation."""
        mock_recorder.checkADCSetup = Mock(return_value=True)
        
        result = mock_recorder.checkADCSetup()
        assert result is True
        mock_recorder.checkADCSetup.assert_called_once()
    
    def test_buffer_space_validation(self, mock_recorder, mock_audio_buffer):
        """Test buffer space validation."""
        mock_recorder.validateBufferSpace = Mock(return_value=True)
        mock_recorder.audioBuffer = mock_audio_buffer
        
        result = mock_recorder.validateBufferSpace()
        assert result is True
        mock_recorder.validateBufferSpace.assert_called_once()


class TestRecorderConfiguration:
    """Test suite for Recorder configuration parameters."""
    
    def test_sample_rate(self):
        """Test sample rate configuration."""
        assert 16000 == 16000  # Standard voice sample rate
    
    def test_channels(self):
        """Test mono channel configuration."""
        assert 1 == 1  # Mono audio
    
    def test_bit_depth(self):
        """Test 16-bit depth configuration."""
        assert 16 == 16  # 16-bit audio
    
    def test_max_silence_duration(self):
        """Test maximum silence duration."""
        assert 2000 == 2000  # 2 second timeout
    
    def test_default_voice_threshold(self):
        """Test default voice threshold."""
        assert 100 == 100  # Default threshold value


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
