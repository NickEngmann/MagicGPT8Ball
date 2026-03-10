#include <unity.h>
#include "TextStateManager.h"
#include <string>

// Mock millis() for testing
static unsigned long mockMillis = 0;

void setUp(void) {
    mockMillis = 0;
}

void tearDown(void) {
}

// Test constructor and initial state
void test_constructor_initial_state(void) {
    TextStateManager manager;
    // Just verify it compiles and constructs
    TEST_ASSERT_NOT_NULL(&manager);
}

// Test state transitions
void test_state_transitions(void) {
    TextStateManager manager;
    
    // Initial state should be IDLE
    manager.setState(TextStateManager::DisplayState::IDLE);
    TEST_ASSERT_EQUAL(TextStateManager::DisplayState::IDLE, manager.getState());
    
    // Transition to RECORDING
    manager.setState(TextStateManager::DisplayState::RECORDING);
    TEST_ASSERT_EQUAL(TextStateManager::DisplayState::RECORDING, manager.getState());
    
    // Transition to THINKING
    manager.setState(TextStateManager::DisplayState::THINKING);
    TEST_ASSERT_EQUAL(TextStateManager::DisplayState::THINKING, manager.getState());
    
    // Transition to RESPONSE
    manager.setState(TextStateManager::DisplayState::RESPONSE);
    TEST_ASSERT_EQUAL(TextStateManager::DisplayState::RESPONSE, manager.getState());
    
    // Transition back to IDLE
    manager.setState(TextStateManager::DisplayState::IDLE);
    TEST_ASSERT_EQUAL(TextStateManager::DisplayState::IDLE, manager.getState());
}

// Test text setting and getting
void test_text_management(void) {
    TextStateManager manager;
    
    const char* testText = "The answer is yes";
    manager.setResponseText(testText);
    
    std::string currentText = manager.getCurrentText();
    TEST_ASSERT_EQUAL_STRING(testText, currentText.c_str());
    
    // Test with different text
    const char* newText = "Reply later";
    manager.setResponseText(newText);
    currentText = manager.getCurrentText();
    TEST_ASSERT_EQUAL_STRING(newText, currentText.c_str());
}

// Test state change with timestamp
void test_state_change_with_timestamp(void) {
    TextStateManager manager;
    
    manager.setState(TextStateManager::DisplayState::RESPONSE);
    manager.setResponseText("Test response");
    
    unsigned long startTime = manager.getResponseStartTime();
    TEST_ASSERT_NOT_EQUAL(0, startTime);
    
    unsigned long duration = manager.getResponseDisplayDuration();
    TEST_ASSERT_EQUAL(3000, duration); // Default is 3 seconds
}

// Test auto-transition from RESPONSE to IDLE
void test_auto_transition_response_to_idle(void) {
    TextStateManager manager;
    
    manager.setState(TextStateManager::DisplayState::RESPONSE);
    manager.setResponseText("Test response");
    
    // Initially should be RESPONSE
    TEST_ASSERT_EQUAL(TextStateManager::DisplayState::RESPONSE, manager.getState());
    
    // Simulate time passing (3 seconds = response display duration)
    mockMillis = 3001;
    manager.autoTransitionResponseText(mockMillis);
    
    // Should have transitioned to IDLE
    TEST_ASSERT_EQUAL(TextStateManager::DisplayState::IDLE, manager.getState());
}

// Test that auto-transition doesn't change state if time hasn't passed
void test_no_auto_transition_before_duration(void) {
    TextStateManager manager;
    
    manager.setState(TextStateManager::DisplayState::RESPONSE);
    manager.setResponseText("Test response");
    
    // Simulate time passing (1 second, less than 3 second duration)
    mockMillis = 1000;
    manager.autoTransitionResponseText(mockMillis);
    
    // Should still be RESPONSE
    TEST_ASSERT_EQUAL(TextStateManager::DisplayState::RESPONSE, manager.getState());
}

// Test state management methods
void test_state_management_methods(void) {
    TextStateManager manager;
    
    // Test isIdle()
    manager.setState(TextStateManager::DisplayState::IDLE);
    TEST_ASSERT_TRUE(manager.isIdle());
    
    manager.setState(TextStateManager::DisplayState::RESPONSE);
    TEST_ASSERT_FALSE(manager.isIdle());
    
    // Test isRecording()
    manager.setState(TextStateManager::DisplayState::RECORDING);
    TEST_ASSERT_TRUE(manager.isRecording());
    
    manager.setState(TextStateManager::DisplayState::IDLE);
    TEST_ASSERT_FALSE(manager.isRecording());
    
    // Test isThinking()
    manager.setState(TextStateManager::DisplayState::THINKING);
    TEST_ASSERT_TRUE(manager.isThinking());
    
    // Test isResponse()
    manager.setState(TextStateManager::DisplayState::RESPONSE);
    TEST_ASSERT_TRUE(manager.isResponse());
}

// Test response text duration configuration
void test_response_duration_configuration(void) {
    TextStateManager manager;
    
    const unsigned long customDuration = 5000; // 5 seconds
    manager.setResponseDisplayDuration(customDuration);
    
    TEST_ASSERT_EQUAL(customDuration, manager.getResponseDisplayDuration());
    
    // Reset to default
    manager.setResponseDisplayDuration(3000);
    TEST_ASSERT_EQUAL(3000, manager.getResponseDisplayDuration());
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_constructor_initial_state);
    RUN_TEST(test_state_transitions);
    RUN_TEST(test_text_management);
    RUN_TEST(test_state_change_with_timestamp);
    RUN_TEST(test_auto_transition_response_to_idle);
    RUN_TEST(test_no_auto_transition_before_duration);
    RUN_TEST(test_state_management_methods);
    RUN_TEST(test_response_duration_configuration);
    
    return UNITY_END();
}
