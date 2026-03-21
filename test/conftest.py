"""
Pytest configuration for MagicGPT8Ball tests
"""

import pytest

# Increase test timeout if needed
pytest.register_assert_rewrite('test_integration_py')


def pytest_configure(config):
    """Configure pytest options"""
    # Add markers for test categories
    config.addinivalue_line(
        "markers", "led: LEDLogger tests"
    )
    config.addinivalue_line(
        "markers", "vibration: VibrationManager tests"
    )
    config.addinivalue_line(
        "markers", "text: TextStateManager tests"
    )
    config.addinivalue_line(
        "markers", "env: Environment tests"
    )
    config.addinivalue_line(
        "markers", "animation: AnimationManager tests"
    )
    config.addinivalue_line(
        "markers", "recorder: Recorder tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
