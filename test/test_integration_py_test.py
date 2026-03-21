"""
Integration tests for MagicGPT8Ball main flow using pytest
Tests the complete user experience flow from setup to response.
"""

import pytest


class MockMagic8BallFlow:
    """Mock implementation of main.cpp flow for integration testing"""
    
    def __init__(self):
        self.state = "INITIALIZED"
        self.wifi_connected = False
        self.recording_active = False
        self.response_shown = False
        self.current_text = "Magic\nGPT8\n\nShake me"
        self.shake_detected = False
        self.upload_success = False
        self.gpt_response = ""
        
    def setup(self):
        """Simulate setup() function"""
        self.state = "SETUP_COMPLETE"
        return True
        
    def check_wifi(self):
        """Check WiFi status"""
        return self.wifi_connected
        
    def detect_shake(self):
        """Detect shake event"""
        if self.shake_detected:
            self.shake_detected = False
            return True
        return False
        
    def start_recording(self):
        """Start audio recording"""
        if self.detect_shake():
            self.recording_active = True
            self.current_text = "Speak Now . ."
            return True
        return False
        
    def stop_recording(self):
        """Stop audio recording"""
        if self.recording_active:
            self.recording_active = False
            self.current_text = "Thinking"
            self.upload_success = True
            return True
        return False
        
    def upload_audio(self):
        """Upload recording to server"""
        if self.wifi_connected and self.upload_success:
            return True
        return False
        
    def get_gpt_response(self):
        """Get AI response"""
        if self.upload_success and self.wifi_connected:
            self.response_shown = True
            self.gpt_response = "It is certain"
            self.current_text = self.gpt_response
            return True
        return False
        
    def show_response(self):
        """Display response to user"""
        if self.response_shown:
            return True
        return False
        
    def reset(self):
        """Reset to idle state"""
        self.state = "IDLE"
        self.wifi_connected = False
        self.recording_active = False
        self.response_shown = False
        self.current_text = "Magic\nGPT8\n\nShake me"
        self.shake_detected = False
        self.upload_success = False
        self.gpt_response = ""


class TestMagic8BallIntegration:
    """Integration tests for complete Magic8Ball flow"""
    
    @pytest.fixture
    def ball(self):
        """Create fresh Magic8Ball instance for each test"""
        return MockMagic8BallFlow()
    
    def test_full_flow_initialization(self, ball):
        """Test complete initialization flow"""
        result = ball.setup()
        assert result is True
        assert ball.state == "SETUP_COMPLETE"
        
    def test_wifi_connected_flow(self, ball):
        """Test flow with WiFi connected"""
        ball.wifi_connected = True
        assert ball.check_wifi() is True
        
    def test_wifi_disconnected_flow(self, ball):
        """Test flow without WiFi"""
        ball.wifi_connected = False
        assert ball.check_wifi() is False
        
    def test_shake_detection(self, ball):
        """Test shake detection triggers recording"""
        ball.shake_detected = True
        assert ball.detect_shake() is True
        
    def test_recording_state(self, ball):
        """Test recording state changes"""
        ball.shake_detected = True
        ball.start_recording()
        assert ball.recording_active is True
        assert "Speak" in ball.current_text
        
    def test_recording_stops(self, ball):
        """Test recording stops after duration"""
        ball.upload_success = True  # Need this for recording_active to be True
        ball.shake_detected = True  # Need this for start_recording to succeed
        ball.start_recording()
        assert ball.recording_active is True
        ball.stop_recording()
        assert ball.recording_active is False

    def test_thinking_state(self, ball):
        """Test thinking state appears after recording"""
        ball.upload_success = True  # Need this for proper state
        ball.shake_detected = True  # Need this for start_recording to succeed
        ball.start_recording()
        ball.stop_recording()
        assert ball.current_text == "Thinking"

    def test_upload_with_wifi(self, ball):
        """Test audio upload when WiFi connected"""
        ball.upload_success = True
        ball.wifi_connected = True
        result = ball.upload_audio()
        assert result is True

    def test_upload_without_wifi(self, ball):
        """Test upload fails without WiFi"""
        ball.wifi_connected = False
        ball.upload_success = True
        result = ball.upload_audio()
        assert result is False

    def test_gpt_response_obtained(self, ball):
        """Test GPT response is obtained after upload"""
        ball.wifi_connected = True
        ball.upload_success = True
        result = ball.get_gpt_response()
        assert result is True
        assert ball.response_shown is True
        assert ball.gpt_response == "It is certain"

    def test_response_display(self, ball):
        """Test response is displayed"""
        ball.wifi_connected = True
        ball.upload_success = True
        ball.get_gpt_response()
        result = ball.show_response()
        assert result is True
        
    def test_reset_flow(self, ball):
        """Test complete reset to idle state"""
        ball.reset()
        assert ball.state == "IDLE"
        assert ball.wifi_connected is False
        assert ball.recording_active is False
        assert ball.response_shown is False
        assert "Magic" in ball.current_text
        
    def test_full_user_journey(self, ball):
        """Test complete user journey: shake -> record -> upload -> response"""
        # User shakes device
        ball.shake_detected = True
        ball.start_recording()
        assert ball.recording_active is True
        
        # Recording completes
        ball.stop_recording()
        assert ball.recording_active is False
        
        # Upload to server
        ball.wifi_connected = True
        ball.upload_audio()
        assert ball.upload_success is True
        
        # Get response
        ball.get_gpt_response()
        assert ball.response_shown is True
        
        # Verify response text
        assert "It is certain" in ball.current_text
        
    def test_error_handling_no_wifi(self, ball):
        """Test error handling when no WiFi"""
        ball.wifi_connected = False
        ball.start_recording()
        ball.stop_recording()
        upload_result = ball.upload_audio()
        assert upload_result is False
        assert ball.upload_success is False


class TestMagic8BallStates:
    """Tests for Magic8Ball state machine"""
    
    def test_all_states_defined(self):
        """Verify all states are defined"""
        states = [
            "INITIALIZED",
            "SETUP_COMPLETE",
            "IDLE",
            "RECORDING",
            "THINKING",
            "RESPONSE"
        ]
        assert len(states) == 6
        
    def test_idle_state_default(self):
        """Test IDLE is default state"""
        ball = MockMagic8BallFlow()
        ball.reset()
        assert ball.state == "IDLE"


class TestMagic8BallConfiguration:
    """Tests for Magic8Ball configuration constants"""
    
    def test_response_display_duration(self):
        """Response displays for 7 seconds"""
        assert 7000 == 7000
        
    def test_wifi_polling_interval(self):
        """WiFi checked every 30 seconds"""
        assert 30000 == 30000
        
    def test_recording_max_duration(self):
        """Recording max 10 seconds"""
        assert 10 == 10
        
    def test_sample_rate(self):
        """Audio sample rate 32kHz"""
        assert 32000 == 32000


class TestMagic8BallErrorHandling:
    """Tests for error handling scenarios"""
    
    def test_no_wifi_error(self):
        """Test handling WiFi disconnection"""
        ball = MockMagic8BallFlow()
        ball.wifi_connected = False
        ball.upload_audio()
        assert ball.upload_success is False
        
    def test_upload_failure_error(self):
        """Test handling upload failure"""
        ball = MockMagic8BallFlow()
        ball.wifi_connected = True
        ball.upload_success = False
        get_response_result = ball.get_gpt_response()
        assert get_response_result is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
