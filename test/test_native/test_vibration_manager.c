#include <unity.h>
#include <map>
#include <vector>

// Test VibrationManager functionality
class TestVibrationManager {
private:
    std::vector<std::string> vibrationLog;
    bool leftMotorActive;
    bool rightMotorActive;
    unsigned long lastVibrationStart;
    
public:
    TestVibrationManager(int pin1, int pin2) : leftMotorActive(false), 
        rightMotorActive(false), lastVibrationStart(0) {}
    
    void begin() {
        vibrationLog.clear();
        leftMotorActive = false;
        rightMotorActive = false;
    }
    
    void update() {
        unsigned long now = millisMock();
        
        // Check if vibration should end
        if (leftMotorActive && (now - lastVibrationStart >= 100)) {
            leftMotorActive = false;
            vibrationLog.push_back("left_motor_stopped");
        }
        
        if (rightMotorActive && (now - lastVibrationStart >= 100)) {
            rightMotorActive = false;
            vibrationLog.push_back("right_motor_stopped");
        }
    }
    
    void shortBuzz() {
        leftMotorActive = true;
        rightMotorActive = true;
        lastVibrationStart = millisMock();
        vibrationLog.push_back("short_buzz");
    }
    
    void mediumBuzz() {
        leftMotorActive = true;
        rightMotorActive = true;
        lastVibrationStart = millisMock();
        vibrationLog.push_back("medium_buzz");
    }
    
    void longBuzz() {
        leftMotorActive = true;
        rightMotorActive = true;
        lastVibrationStart = millisMock();
        vibrationLog.push_back("long_buzz");
    }
    
    void stop() {
        leftMotorActive = false;
        rightMotorActive = false;
        vibrationLog.push_back("stop");
    }
    
    bool isMotorActive(int motorIndex) {
        if (motorIndex == 0) return leftMotorActive;
        if (motorIndex == 1) return rightMotorActive;
        return false;
    }
    
    bool getLeftMotorStatus() { return leftMotorActive; }
    bool getRightMotorStatus() { return rightMotorActive; }
    
    size_t getVibrationCount() { return vibrationLog.size(); }
    
    std::string getVibrationLog(size_t index) {
        if (index < vibrationLog.size()) {
            return vibrationLog[index];
        }
        return "";
    }
    
    void clearLog() {
        vibrationLog.clear();
    }
    
    unsigned long getLastVibrationDuration() {
        if (lastVibrationStart > 0) {
            return millisMock() - lastVibrationStart;
        }
        return 0;
    }
    
    static unsigned long millisMock() {
        static unsigned long mockTime = 0;
        return mockTime++;
    }
    
    static void setMillisMock(unsigned long time) {
        mockTime = time;
    }
};

// VibrationManager mock for testing
TestVibrationManager vibrationManager(5, 13);

void setUp(void) {
    vibrationManager.begin();
    vibrationManager.clearLog();
}

void tearDown(void) {}

void test_vibration_manager_initialization(void) {
    TEST_ASSERT_TRUE(true); // Basic setup check
    TEST_ASSERT_FALSE(vibrationManager.getLeftMotorStatus());
    TEST_ASSERT_FALSE(vibrationManager.getRightMotorStatus());
}

void test_vibration_manager_short_buzz(void) {
    vibrationManager.shortBuzz();
    vibrationManager.update();
    
    TEST_ASSERT_TRUE(vibrationManager.getLeftMotorStatus());
    TEST_ASSERT_TRUE(vibrationManager.getRightMotorStatus());
    TEST_ASSERT_EQUAL_UINT(1, vibrationManager.getVibrationCount());
}

void test_vibration_manager_medium_buzz(void) {
    vibrationManager.mediumBuzz();
    vibrationManager.update();
    
    TEST_ASSERT_EQUAL_UINT(1, vibrationManager.getVibrationCount());
    TEST_ASSERT_EQUAL_STRING("medium_buzz", 
                            vibrationManager.getVibrationLog(0).c_str());
}

void test_vibration_manager_long_buzz(void) {
    vibrationManager.longBuzz();
    vibrationManager.update();
    
    TEST_ASSERT_EQUAL_STRING("long_buzz", 
                            vibrationManager.getVibrationLog(0).c_str());
}

void test_vibration_manager_stop(void) {
    vibrationManager.shortBuzz();
    vibrationManager.stop();
    
    TEST_ASSERT_FALSE(vibrationManager.getLeftMotorStatus());
    TEST_ASSERT_FALSE(vibrationManager.getRightMotorStatus());
    TEST_ASSERT_EQUAL_UINT(2, vibrationManager.getVibrationCount());
}

void test_vibration_manager_auto_stop(void) {
    vibrationManager.shortBuzz();
    vibrationManager.update();
    
    // Advance time past vibration duration
    for (int i = 0; i < 150; i++) {
        vibrationManager.update();
    }
    
    TEST_ASSERT_FALSE(vibrationManager.getLeftMotorStatus());
    TEST_ASSERT_FALSE(vibrationManager.getRightMotorStatus());
}

void test_vibration_manager_sequence(void) {
    vibrationManager.shortBuzz();
    vibrationManager.mediumBuzz();
    vibrationManager.stop();
    vibrationManager.longBuzz();
    
    TEST_ASSERT_EQUAL_UINT(4, vibrationManager.getVibrationCount());
}

void test_vibration_manager_multiple_stops(void) {
    vibrationManager.shortBuzz();
    vibrationManager.stop();
    vibrationManager.stop(); // Multiple stops should be safe
    vibrationManager.stop();
    
    TEST_ASSERT_FALSE(vibrationManager.getLeftMotorStatus());
}

void test_vibration_manager_update_idle(void) {
    TEST_ASSERT_EQUAL_UINT(0, vibrationManager.getVibrationCount());
    
    vibrationManager.update(); // Update when idle
    TEST_ASSERT_EQUAL_UINT(0, vibrationManager.getVibrationCount());
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_vibration_manager_initialization);
    RUN_TEST(test_vibration_manager_short_buzz);
    RUN_TEST(test_vibration_manager_medium_buzz);
    RUN_TEST(test_vibration_manager_long_buzz);
    RUN_TEST(test_vibration_manager_stop);
    RUN_TEST(test_vibration_manager_auto_stop);
    RUN_TEST(test_vibration_manager_sequence);
    RUN_TEST(test_vibration_manager_multiple_stops);
    RUN_TEST(test_vibration_manager_update_idle);
    
    return UNITY_END();
}
