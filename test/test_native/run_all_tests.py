"""
Test suite runner for MagicGPT8Ball native tests
Combines all Python-based unit tests
"""

import sys
import os

# Add test directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all test modules
from test_led_logger_py import (
    test_led_logger_constructor,
    test_led_logger_state_transitions,
    test_led_logger_custom_state,
    test_led_logger_brightness_control,
    test_led_logger_color_mapping,
    test_led_logger_pattern_types,
)

from test_vibration_manager_py import (
    test_vibration_manager_constructor,
    test_vibration_manager_begin,
    test_vibration_manager_start,
    test_vibration_manager_stop,
    test_vibration_manager_auto_stop,
    test_vibration_manager_vibration_patterns,
    test_vibration_manager_double_buzz,
    test_vibration_manager_custom_pins,
    test_vibration_manager_timing,
)

from test_text_state_manager_py import (
    test_text_manager_idle_state,
    test_text_manager_error_state,
    test_text_manager_response_state,
    test_text_manager_recording_period_counting,
    test_text_manager_recording_text_generation,
    test_text_manager_thinking_pattern,
    test_text_manager_state_transitions,
    test_text_manager_recording_to_thinking_transition,
    test_text_manager_period_count_reset,
    test_text_manager_response_timing,
)

from test_environment_py import (
    test_environment_get_valtown_url,
    test_environment_get_device_token,
    test_environment_get_unknown_key,
    test_environment_parse_env_line,
    test_environment_parse_env_line_with_quotes,
    test_environment_parse_empty_line,
    test_environment_parse_comment,
    test_environment_parse_invalid_line,
    test_environment_multiple_vars,
    test_environment_overwrite_values,
)

def run_all_tests():
    """Run all tests and report results"""
    
    all_tests = [
        # LED Logger tests
        ("LED Logger", [
            test_led_logger_constructor,
            test_led_logger_state_transitions,
            test_led_logger_custom_state,
            test_led_logger_brightness_control,
            test_led_logger_color_mapping,
            test_led_logger_pattern_types,
        ]),
        
        # Vibration Manager tests
        ("Vibration Manager", [
            test_vibration_manager_constructor,
            test_vibration_manager_begin,
            test_vibration_manager_start,
            test_vibration_manager_stop,
            test_vibration_manager_auto_stop,
            test_vibration_manager_vibration_patterns,
            test_vibration_manager_double_buzz,
            test_vibration_manager_custom_pins,
            test_vibration_manager_timing,
        ]),
        
        # Text State Manager tests
        ("Text State Manager", [
            test_text_manager_idle_state,
            test_text_manager_error_state,
            test_text_manager_response_state,
            test_text_manager_recording_period_counting,
            test_text_manager_recording_text_generation,
            test_text_manager_thinking_pattern,
            test_text_manager_state_transitions,
            test_text_manager_recording_to_thinking_transition,
            test_text_manager_period_count_reset,
            test_text_manager_response_timing,
        ]),
        
        # Environment tests
        ("Environment", [
            test_environment_get_valtown_url,
            test_environment_get_device_token,
            test_environment_get_unknown_key,
            test_environment_parse_env_line,
            test_environment_parse_env_line_with_quotes,
            test_environment_parse_empty_line,
            test_environment_parse_comment,
            test_environment_parse_invalid_line,
            test_environment_multiple_vars,
            test_environment_overwrite_values,
        ]),
    ]
    
    total_passed = 0
    total_failed = 0
    
    for category, tests in all_tests:
        print(f"\n{'='*60}")
        print(f"Testing: {category}")
        print(f"{'='*60}")
        
        category_passed = 0
        category_failed = 0
        
        for test in tests:
            try:
                test()
                print(f"  ✓ {test.__name__}")
                category_passed += 1
                total_passed += 1
            except AssertionError as e:
                print(f"  ✗ {test.__name__}: {e}")
                category_failed += 1
                total_failed += 1
            except Exception as e:
                print(f"  ✗ {test.__name__}: Exception - {e}")
                category_failed += 1
                total_failed += 1
        
        print(f"\n{category}: {category_passed} passed, {category_failed} failed")
    
    print(f"\n{'='*60}")
    print(f"TOTAL RESULTS")
    print(f"{'='*60}")
    print(f"Overall: {total_passed} passed, {total_failed} failed")
    print(f"{'='*60}")
    
    if total_failed == 0:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total_failed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
