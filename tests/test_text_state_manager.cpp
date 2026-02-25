#include <unity.h>
#include "../src/TextStateManager.h"

TextStateManager textManager;

void test_IdleStateText(void)
{
    textManager.setState(TextStateManager::DisplayState::IDLE);
    String text = textManager.getCurrentText();
    TEST_ASSERT_EQUAL_STRING("Magic\nGPT8\n\nShake me", text.c_str());
}

void test_ErrorStateText(void)
{
    textManager.setState(TextStateManager::DisplayState::ERROR);
    String text = textManager.getCurrentText();
    TEST_ASSERT_EQUAL_STRING("Wifi: X", text.c_str());
}

void test_RecordingStateText(void)
{
    textManager.setState(TextStateManager::DisplayState::RECORDING);
    String text = textManager.getCurrentText();
    // Should start with "Speak Now" and periods
    TEST_ASSERT_TRUE(text.startsWith("Speak Now"));
    TEST_ASSERT_EQUAL(10, textManager.periodCount);
}

void test_RecordingStatePeriodCountDecrements(void)
{
    textManager.setState(TextStateManager::DisplayState::RECORDING);
    unsigned long currentTime = millis();
    
    // Simulate 8 seconds passing (8 updates)
    for (int i = 0; i < 8; i++) {
        textManager.update(currentTime + (i + 1) * 1000);
    }
    
    String text = textManager.getCurrentText();
    // After 8 updates, periodCount should be 2 (10 - 8 = 2), so text should be "Thinking"
    TEST_ASSERT_EQUAL_STRING("Thinking", text.c_str());
}

void test_ThinkingStateText(void)
{
    textManager.setState(TextStateManager::DisplayState::THINKING);
    String text = textManager.getCurrentText();
    // Should start with "Thinking" and have some periods
    TEST_ASSERT_TRUE(text.startsWith("Thinking"));
}

void test_ThinkingStatePeriodCountCycles(void)
{
    textManager.setState(TextStateManager::DisplayState::THINKING);
    unsigned long currentTime = millis();
    
    // Simulate 4 updates (should cycle back to 0)
    for (int i = 0; i < 4; i++) {
        textManager.update(currentTime + (i + 1) * 500);
    }
    
    String text = textManager.getCurrentText();
    // After cycling, should be back to "Thinking" with 0 periods
    TEST_ASSERT_EQUAL_STRING("Thinking", text.c_str());
}

void test_ResponseStateText(void)
{
    String response = "It is certain";
    textManager.setState(TextStateManager::DisplayState::RESPONSE, response);
    String text = textManager.getCurrentText();
    TEST_ASSERT_EQUAL_STRING(response.c_str(), text.c_str());
}

void test_ResponseStateAutoResets(void)
{
    String response = "Yes, definitely";
    textManager.setState(TextStateManager::DisplayState::RESPONSE, response);
    unsigned long currentTime = millis();
    
    // Simulate 6 seconds passing (more than 5 second duration)
    textManager.update(currentTime + 6000);
    
    TEST_ASSERT_EQUAL(TextStateManager::DisplayState::IDLE, textManager.getState());
}

void test_GetState(void)
{
    textManager.setState(TextStateManager::DisplayState::RECORDING);
    TEST_ASSERT_EQUAL(TextStateManager::DisplayState::RECORDING, textManager.getState());
    
    textManager.setState(TextStateManager::DisplayState::THINKING);
    TEST_ASSERT_EQUAL(TextStateManager::DisplayState::THINKING, textManager.getState());
    
    textManager.setState(TextStateManager::DisplayState::RESPONSE, "test");
    TEST_ASSERT_EQUAL(TextStateManager::DisplayState::RESPONSE, textManager.getState());
}

int main(void)
{
    UNITY_BEGIN();
    
    RUN_TEST(test_IdleStateText);
    RUN_TEST(test_ErrorStateText);
    RUN_TEST(test_RecordingStateText);
    RUN_TEST(test_RecordingStatePeriodCountDecrements);
    RUN_TEST(test_ThinkingStateText);
    RUN_TEST(test_ThinkingStatePeriodCountCycles);
    RUN_TEST(test_ResponseStateText);
    RUN_TEST(test_ResponseStateAutoResets);
    RUN_TEST(test_GetState);
    
    return UNITY_END();
}
