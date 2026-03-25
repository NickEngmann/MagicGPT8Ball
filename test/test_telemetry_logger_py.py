"""
Test suite for TelemetryLogger module - Python simulation tests
Tests the telemetry logging simulation logic for the Magic 8 Ball.
This simulates the behavior of the C++ TelemetryLogger class.
"""

import pytest
import json
from datetime import datetime
from typing import Optional, List, Dict, Any


class SimulatedTelemetryData:
    """Simulates TelemetryData structure"""
    
    def __init__(self, timestamp: int, event_type: str, category: str,
                 details: str, duration_ms: int, success: bool):
        self.timestamp = timestamp
        self.event_type = event_type
        self.category = category
        self.details = details
        self.duration_ms = duration_ms
        self.success = success
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'event_type': self.event_type,
            'category': self.category,
            'details': self.details,
            'duration_ms': self.duration_ms,
            'success': self.success
        }


class SimulatedTelemetryLogger:
    """Python simulation of C++ TelemetryLogger class"""
    
    def __init__(self, max_events: int = 100):
        self.max_events = max_events
        self.events: List[SimulatedTelemetryData] = []
        self.event_counts: Dict[str, int] = {}
        self.category_counts: Dict[str, int] = {}
        self._current_timestamp = 0
        
    def increment_time(self, ms: int = 100):
        """Simulate time passing"""
        self._current_timestamp += ms
        
    def log_event(self, event_type: str, category: str, details: str = "",
                  duration_ms: int = 0, success: bool = True):
        """Log an event"""
        data = SimulatedTelemetryData(
            timestamp=self._current_timestamp,
            event_type=event_type,
            category=category,
            details=details,
            duration_ms=duration_ms,
            success=success
        )
        self.events.append(data)
        self._update_statistics()
        self._trim_events()
        
    def log_shake(self):
        """Simulate shake event"""
        self.log_event('SHAKE_DETECTED', 'USER_ACTION', '', 0, True)
        self.increment_time(10)
        
    def log_recording_start(self):
        """Simulate recording start"""
        self.log_event('RECORDING_STARTED', 'AUDIO', '', 0, True)
        self.increment_time(100)
        
    def log_recording_complete(self, success: bool, duration_ms: int):
        """Simulate recording completion"""
        details = f"{duration_ms}ms" if success else f"Failed after {duration_ms}ms"
        self.log_event('RECORDING_COMPLETED', 'AUDIO', details, 
                      duration_ms, success)
        self.increment_time(100)
        
    def log_response_shown(self, response: str, duration_ms: int):
        """Simulate response shown"""
        # Truncate long responses
        if len(response) > 20:
            response = response[:20] + "..."
        self.log_event('RESPONSE_SHOWN', 'DISPLAY', response, 
                      duration_ms, True)
        self.increment_time(duration_ms)
        
    def log_api_request(self, success: bool, duration_ms: int):
        """Simulate API request"""
        details = "API call successful" if success else "API call failed"
        self.log_event('API_REQUEST', 'NETWORK', details, 
                      duration_ms, success)
        self.increment_time(duration_ms)
        
    def log_error(self, error_message: str):
        """Simulate error event"""
        self.log_event('ERROR', 'ERROR_EVENT', error_message, 0, False)
        self.increment_time(10)
        
    def log_wifi_error(self):
        """Simulate WiFi error"""
        self.log_event('WIFI_ERROR', 'NETWORK', 'WiFi connection error', 
                      0, False)
        self.increment_time(100)
        
    def log_startup(self):
        """Simulate startup"""
        self.log_event('SYSTEM_STARTUP', 'SYSTEM', 'System startup', 
                      0, True)
        self.increment_time(1000)
        
    def get_event_count(self) -> int:
        """Get total event count"""
        return len(self.events)
        
    def get_event_count_by_type(self, event_type: str) -> int:
        """Get count of events by type"""
        return self.event_counts.get(event_type, 0)
        
    def get_event_count_by_category(self, category: str) -> int:
        """Get count of events by category"""
        return self.category_counts.get(category, 0)
        
    def get_latest_event(self) -> Optional[SimulatedTelemetryData]:
        """Get the latest event"""
        return self.events[-1] if self.events else None
        
    def get_event_by_index(self, index: int) -> Optional[SimulatedTelemetryData]:
        """Get event by index"""
        if 0 <= index < len(self.events):
            return self.events[index]
        return None
        
    def get_events(self) -> List[SimulatedTelemetryData]:
        """Get all events"""
        return self.events.copy()
        
    def get_total_events(self) -> int:
        """Get total events"""
        return len(self.events)
        
    def get_unique_event_types(self) -> int:
        """Get unique event type count"""
        return len(self.event_counts)
        
    def get_success_rate(self) -> float:
        """Calculate success rate"""
        if not self.events:
            return 0.0
        success_count = sum(1 for e in self.events if e.success)
        return (success_count / len(self.events)) * 100.0
        
    def get_average_response_time(self) -> int:
        """Calculate average response time"""
        relevant_events = [e for e in self.events 
                          if e.event_type in ('RESPONSE_SHOWN', 'API_REQUEST', 
                                             'RECORDING_COMPLETED')]
        if not relevant_events:
            return 0
        total_time = sum(e.duration_ms for e in relevant_events)
        return total_time // len(relevant_events)
        
    def get_summary(self) -> str:
        """Get summary string"""
        lines = [
            "=== Telemetry Summary ===",
            f"Total Events: {len(self.events)}",
            f"Unique Event Types: {len(self.event_counts)}",
            "\nEvent Categories:",
        ]
        for cat, count in self.category_counts.items():
            lines.append(f"  - {cat}: {count}")
        lines.append("\nEvent Types:")
        for event_type, count in self.event_counts.items():
            lines.append(f"  - {event_type}: {count}")
        lines.append("=== End Summary ===")
        return "\n".join(lines)
        
    def get_json_summary(self) -> str:
        """Get JSON summary"""
        summary = {
            'total_events': len(self.events),
            'unique_event_types': len(self.event_counts),
            'categories': dict(self.category_counts),
            'event_types': dict(self.event_counts)
        }
        return json.dumps(summary, indent=2)
        
    def clear(self):
        """Clear all events"""
        self.events.clear()
        self.event_counts.clear()
        self.category_counts.clear()
        self._current_timestamp = 0
        
    def _update_statistics(self):
        """Update event statistics"""
        self.event_counts.clear()
        self.category_counts.clear()
        for event in self.events:
            self.event_counts[event.event_type] = \
                self.event_counts.get(event.event_type, 0) + 1
            self.category_counts[event.category] = \
                self.category_counts.get(event.category, 0) + 1
                
    def _trim_events(self):
        """Trim events if limit exceeded"""
        while len(self.events) > self.max_events:
            self.events.pop(0)
        self._update_statistics()


class TestSimulatedTelemetryLogger:
    """Tests for SimulatedTelemetryLogger"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.telemetry = SimulatedTelemetryLogger(max_events=50)
        
    def test_initialization(self):
        """Test telemetry logger initialization"""
        assert self.telemetry.get_event_count() == 0
        assert self.telemetry.get_total_events() == 0
        assert self.telemetry.get_unique_event_types() == 0
        assert self.telemetry.get_success_rate() == 0.0
        
    def test_log_shake_event(self):
        """Test logging a shake event"""
        self.telemetry.log_shake()
        
        assert self.telemetry.get_event_count() == 1
        assert self.telemetry.get_event_count_by_type('SHAKE_DETECTED') == 1
        
        latest = self.telemetry.get_latest_event()
        assert latest is not None
        assert latest.event_type == 'SHAKE_DETECTED'
        assert latest.success is True
        
    def test_log_recording_complete_success(self):
        """Test logging successful recording completion"""
        self.telemetry.log_recording_complete(True, 5000)
        
        latest = self.telemetry.get_latest_event()
        assert latest.event_type == 'RECORDING_COMPLETED'
        assert latest.duration_ms == 5000
        assert latest.success is True
        assert '5000ms' in latest.details
        
    def test_log_recording_complete_failure(self):
        """Test logging failed recording completion"""
        self.telemetry.log_recording_complete(False, 3000)
        
        latest = self.telemetry.get_latest_event()
        assert latest.success is False
        assert latest.duration_ms == 3000
        
    def test_log_response_shown(self):
        """Test logging response shown event"""
        self.telemetry.log_response_shown("It is certain", 7000)
        
        latest = self.telemetry.get_latest_event()
        assert latest.event_type == 'RESPONSE_SHOWN'
        assert latest.duration_ms == 7000
        assert latest.details == "It is certain"
        
    def test_log_response_truncation(self):
        """Test that long responses are truncated"""
        long_response = "A very long response that exceeds the normal length limit for display purposes and should be truncated in the telemetry log"
        self.telemetry.log_response_shown(long_response, 1000)
        
        latest = self.telemetry.get_latest_event()
        # Should be truncated to ~23 chars (20 + "...")
        assert len(latest.details) <= 23
        assert latest.details.endswith('...')
        
    def test_log_api_request(self):
        """Test logging API request"""
        self.telemetry.log_api_request(True, 1500)
        
        latest = self.telemetry.get_latest_event()
        assert latest.event_type == 'API_REQUEST'
        assert latest.success is True
        assert latest.duration_ms == 1500
        
    def test_error_handling(self):
        """Test error logging"""
        self.telemetry.log_error("WiFi connection failed")
        
        latest = self.telemetry.get_latest_event()
        assert latest.event_type == 'ERROR'
        assert latest.success is False
        assert latest.category == 'ERROR_EVENT'
        assert 'WiFi' in latest.details
        
    def test_wifi_error(self):
        """Test WiFi error logging"""
        self.telemetry.log_wifi_error()
        
        latest = self.telemetry.get_latest_event()
        assert latest.event_type == 'WIFI_ERROR'
        assert latest.success is False
        assert latest.category == 'NETWORK'
        
    def test_startup_event(self):
        """Test startup event"""
        self.telemetry.log_startup()
        
        latest = self.telemetry.get_latest_event()
        assert latest.event_type == 'SYSTEM_STARTUP'
        assert latest.success is True
        assert latest.category == 'SYSTEM'
        
    def test_event_categorization(self):
        """Test event categorization"""
        self.telemetry.log_shake()  # USER_ACTION
        self.telemetry.log_recording_start()  # AUDIO
        self.telemetry.log_api_request(True, 1000)  # NETWORK
        self.telemetry.log_error("Test")  # ERROR_EVENT
        
        assert self.telemetry.get_event_count_by_category('USER_ACTION') == 1
        assert self.telemetry.get_event_count_by_category('AUDIO') == 1
        assert self.telemetry.get_event_count_by_category('NETWORK') == 1
        assert self.telemetry.get_event_count_by_category('ERROR_EVENT') == 1
        
    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        self.telemetry.log_api_request(True, 1000)
        self.telemetry.log_api_request(True, 1500)
        self.telemetry.log_api_request(False, 0)
        self.telemetry.log_api_request(True, 2000)
        
        success_rate = self.telemetry.get_success_rate()
        assert success_rate == 75.0
        
    def test_success_rate_empty(self):
        """Test success rate with no events"""
        assert self.telemetry.get_success_rate() == 0.0
        
    def test_average_response_time(self):
        """Test average response time calculation"""
        self.telemetry.log_response_shown("Response 1", 1000)
        self.telemetry.log_response_shown("Response 2", 2000)
        self.telemetry.log_response_shown("Response 3", 3000)
        
        avg_time = self.telemetry.get_average_response_time()
        assert avg_time == 2000
        
    def test_get_latest_event(self):
        """Test getting latest event"""
        self.telemetry.log_shake()
        self.telemetry.log_recording_start()
        self.telemetry.log_recording_complete(True, 5000)
        
        latest = self.telemetry.get_latest_event()
        assert latest is not None
        assert latest.event_type == 'RECORDING_COMPLETED'
        assert latest.duration_ms == 5000
        
    def test_get_event_by_index(self):
        """Test getting event by index"""
        self.telemetry.log_shake()
        self.telemetry.log_recording_start()
        self.telemetry.log_recording_complete(True, 5000)
        
        event0 = self.telemetry.get_event_by_index(0)
        event1 = self.telemetry.get_event_by_index(1)
        event2 = self.telemetry.get_event_by_index(2)
        
        assert event0 is not None
        assert event1 is not None
        assert event2 is not None
        assert event0.event_type == 'SHAKE_DETECTED'
        assert event1.event_type == 'RECORDING_STARTED'
        assert event2.event_type == 'RECORDING_COMPLETED'
        
    def test_get_invalid_event_index(self):
        """Test getting event with invalid index"""
        self.telemetry.log_shake()
        
        invalid_event = self.telemetry.get_event_by_index(100)
        assert invalid_event is None
        
    def test_get_all_events(self):
        """Test getting all events"""
        self.telemetry.log_shake()
        self.telemetry.log_recording_start()
        
        events = self.telemetry.get_events()
        assert len(events) == 2
        
    def test_summary_generation(self):
        """Test summary generation"""
        self.telemetry.log_shake()
        self.telemetry.log_recording_start()
        self.telemetry.log_recording_complete(True, 5000)
        
        summary = self.telemetry.get_summary()
        assert 'Total Events' in summary
        assert 'Unique Event Types' in summary
        assert 'SHAKE_DETECTED' in summary
        assert 'RECORDING_COMPLETED' in summary
        
    def test_json_summary_generation(self):
        """Test JSON summary generation"""
        self.telemetry.log_shake()
        self.telemetry.log_recording_start()
        
        json_summary = self.telemetry.get_json_summary()
        assert json_summary.startswith('{')
        assert 'total_events' in json_summary
        assert 'categories' in json_summary
        
    def test_event_limit_trimming(self):
        """Test event limit trimming"""
        limited = SimulatedTelemetryLogger(max_events=3)
        
        limited.log_shake()
        limited.log_recording_start()
        limited.log_recording_complete(True, 5000)
        
        assert limited.get_event_count() == 3
        
        # Add one more - oldest should be removed
        limited.log_response_shown("Response", 1000)
        
        assert limited.get_event_count() == 3
        
        # First event should NOT be shake (it was trimmed)
        earliest = limited.get_event_by_index(0)
        assert earliest.event_type != 'SHAKE_DETECTED'
        
    def test_clear_events(self):
        """Test clearing all events"""
        self.telemetry.log_shake()
        self.telemetry.log_recording_start()
        
        assert self.telemetry.get_event_count() == 2
        
        self.telemetry.clear()
        
        assert self.telemetry.get_event_count() == 0
        assert self.telemetry.get_unique_event_types() == 0
        
    def test_multiple_event_types(self):
        """Test logging multiple event types"""
        self.telemetry.log_shake()
        self.telemetry.log_recording_start()
        self.telemetry.log_recording_complete(True, 5000)
        self.telemetry.log_response_shown("It is certain", 7000)
        self.telemetry.log_api_request(True, 1500)
        
        assert self.telemetry.get_event_count() == 5
        assert self.telemetry.get_unique_event_types() == 5
        
    def test_timestamp_tracking(self):
        """Test timestamp tracking"""
        self.telemetry.increment_time(1000)  # Advance time first
        self.telemetry.log_shake()
        
        events = self.telemetry.get_events()
        assert len(events) == 1
        assert events[0].timestamp >= 0
        
    def test_complete_usage_cycle(self):
        """Test a complete usage cycle"""
        self.telemetry.log_shake()
        self.telemetry.log_recording_start()
        self.telemetry.log_recording_complete(True, 5000)
        self.telemetry.log_response_shown("It is certain", 7000)
        self.telemetry.log_api_request(True, 1500)
        
        assert self.telemetry.get_event_count() == 5
        assert self.telemetry.get_success_rate() == 100.0
        assert self.telemetry.get_average_response_time() > 0
        
    def test_error_handling_cycle(self):
        """Test cycle with errors"""
        self.telemetry.log_shake()
        self.telemetry.log_recording_start()
        self.telemetry.log_recording_complete(False, 3000)
        self.telemetry.log_error("Recording failed")
        self.telemetry.log_wifi_error()
        
        events = self.telemetry.get_events()
        success_count = sum(1 for e in events if e.success)
        assert success_count < len(events)


class TestTelemetryDataStructure:
    """Tests for telemetry data structure"""
    
    def test_televitry_data_creation(self):
        """Test creating telemetry data"""
        data = SimulatedTelemetryData(
            timestamp=12345,
            event_type='TEST',
            category='TEST',
            details='test details',
            duration_ms=100,
            success=True
        )
        
        assert data.timestamp == 12345
        assert data.event_type == 'TEST'
        assert data.details == 'test details'
        assert data.duration_ms == 100
        assert data.success is True
        
    def test_televitry_data_to_dict(self):
        """Test converting telemetry data to dict"""
        data = SimulatedTelemetryData(
            timestamp=12345,
            event_type='TEST',
            category='TEST',
            details='test',
            duration_ms=100,
            success=True
        )
        
        d = data.to_dict()
        assert d['timestamp'] == 12345
        assert d['event_type'] == 'TEST'
        assert d['success'] is True
