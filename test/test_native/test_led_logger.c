#include <unity.h>
#include <vector>
#include <string>
#include <map>

// Test LEDLogger functionality
class TestLEDLogger {
private:
    enum LEDPattern {
        SOLID = 0,
        BLINK,
        FAST_BLINK,
        PULSE,
        OFF
    };
    
    struct LEDState {
        SystemState state;
        LEDPattern pattern;
        bool isActive;
        unsigned long lastChangeTime;
    };
    
    LEDState currentLEDState;
    std::vector<std::string> stateLog;
    
public:
    TestLEDLogger(int pin) : currentLEDState(), isActive(false) {
        currentLEDState.state = SystemState::IDLE;
        currentLEDState.pattern = LEDPattern::OFF;
        currentLEDState.isActive = false;
        currentLEDState.lastChangeTime = 0;
    }
    
    void begin() {
        stateLog.clear();
        currentLEDState.state = SystemState::IDLE;
        currentLEDState.pattern = LEDPattern::OFF;
        currentLEDState.isActive = false;
        currentLEDState.lastChangeTime = 0;
    }
    
    void setState(SystemState state, LEDPattern pattern) {
        currentLEDState.state = state;
        currentLEDState.pattern = pattern;
        currentLEDState.isActive = true;
        currentLEDState.lastChangeTime = millisMock();
        
        std::string logEntry = "state:" + systemStateToString(state) + 
                               ",pattern:" + patternToString(pattern);
        stateLog.push_back(logEntry);
    }
    
    void update() {
        unsigned long now = millisMock();
        
        // Auto-turn off after duration
        if (currentLEDState.isActive && 
            (now - currentLEDState.lastChangeTime > 2000)) {
            currentLEDState.isActive = false;
        }
        
        // Blink pattern timing
        if (currentLEDState.pattern == LEDPattern::BLINK && 
            currentLEDState.isActive) {
            if ((now - currentLEDState.lastChangeTime) % 500 < 250) {
                // LED on
            } else {
                // LED off
            }
        }
        
        // Fast blink pattern
        if (currentLEDState.pattern == LEDPattern::FAST_BLINK && 
            currentLEDState.isActive) {
            if ((now - currentLEDState.lastChangeTime) % 100 < 50) {
                // LED on
            } else {
                // LED off
            }
        }
        
        // Pulse pattern
        if (currentLEDState.pattern == LEDPattern::PULSE && 
            currentLEDState.isActive) {
            unsigned long pulsePhase = (now - currentLEDState.lastChangeTime) % 2000;
            // Simulate pulse brightness
        }
    }
    
    bool isActiveLED() {
        return currentLEDState.isActive;
    }
    
    SystemState getCurrentState() {
        return currentLEDState.state;
    }
    
    LEDPattern getCurrentPattern() {
        return currentLEDState.pattern;
    }
    
    size_t getLogSize() {
        return stateLog.size();
    }
    
    std::string getLogEntry(size_t index) {
        if (index < stateLog.size()) {
            return stateLog[index];
        }
        return "";
    }
    
    void clearLog() {
        stateLog.clear();
    }
    
    static std::string systemStateToString(SystemState state) {
        switch (state) {
            case SystemState::IDLE: return "IDLE";
            case SystemState::NORMAL: return "NORMAL";
            case SystemState::BUSY: return "BUSY";
            case SystemState::ERROR: return "ERROR";
            case SystemState::WARNING: return "WARNING";
            case SystemState::STARTUP: return "STARTUP";
            default: return "UNKNOWN";
        }
    }
    
    static std::string patternToString(LEDPattern pattern) {
        switch (pattern) {
            case LEDPattern::SOLID: return "SOLID";
            case LEDPattern::BLINK: return "BLINK";
            case LEDPattern::FAST_BLINK: return "FAST_BLINK";
            case LEDPattern::PULSE: return "PULSE";
            case LEDPattern::OFF: return "OFF";
            default: return "UNKNOWN";
        }
    }
    
    static unsigned long millisMock() {
        static unsigned long mockTime = 0;
        return mockTime++;
    }
    
    static void setMillisMock(unsigned long time) {
        mockTime = time;
    }
    
    typedef enum {
        IDLE = 0,
        NORMAL,
        BUSY,
        ERROR,
        WARNING,
        STARTUP
    } SystemState;
    
    typedef enum {
        SOLID = 0,
        BLINK,
        FAST_BLINK,
        PULSE,
        OFF
    } LEDPattern;
    
private:
    bool isActive;
};

// LEDLogger mock for testing
TestLEDLogger ledLogger(3);

void setUp(void) {
    ledLogger.begin();
    ledLogger.clearLog();
    TestLEDLogger::setMillisMock(0);
}

void tearDown(void) {}

void test_led_logger_initialization(void) {
    TEST_ASSERT_TRUE(true);
    TEST_ASSERT_EQUAL_UINT(0, ledLogger.getLogSize());
    TEST_ASSERT_FALSE(ledLogger.isActiveLED());
}

void test_led_logger_set_idle_state(void) {
    ledLogger.setState(TestLEDLogger::SystemState::IDLE, 
                       TestLEDLogger::LEDPattern::OFF);
    
    TEST_ASSERT_EQUAL_UINT(1, ledLogger.getLogSize());
    std::string logEntry = ledLogger.getLogEntry(0);
    TEST_ASSERT_TRUE(logEntry.find("IDLE") != std::string::npos);
}

void test_led_logger_set_normal_state(void) {
    ledLogger.setState(TestLEDLogger::SystemState::NORMAL, 
                       TestLEDLogger::LEDPattern::SOLID);
    
    TEST_ASSERT_TRUE(ledLogger.isActiveLED());
}

void test_led_logger_set_busy_state(void) {
    ledLogger.setState(TestLEDLogger::SystemState::BUSY, 
                       TestLEDLogger::LEDPattern::PULSE);
    
    std::string logEntry = ledLogger.getLogEntry(ledLogger.getLogSize() - 1);
    TEST_ASSERT_TRUE(logEntry.find("BUSY") != std::string::npos);
    TEST_ASSERT_TRUE(logEntry.find("PULSE") != std::string::npos);
}

void test_led_logger_set_error_state(void) {
    ledLogger.setState(TestLEDLogger::SystemState::ERROR, 
                       TestLEDLogger::LEDPattern::FAST_BLINK);
    
    TEST_ASSERT_EQUAL_STRING("ERROR", 
                            TestLEDLogger::systemStateToString(
                                ledLogger.getCurrentState()).c_str());
    TEST_ASSERT_EQUAL_STRING("FAST_BLINK", 
                            TestLEDLogger::patternToString(
                                ledLogger.getCurrentPattern()).c_str());
}

void test_led_logger_set_warning_state(void) {
    ledLogger.setState(TestLEDLogger::SystemState::WARNING, 
                       TestLEDLogger::LEDPattern::BLINK);
    
    TEST_ASSERT_EQUAL_STRING("WARNING", 
                            TestLEDLogger::systemStateToString(
                                ledLogger.getCurrentState()).c_str());
}

void test_led_logger_set_startup_state(void) {
    ledLogger.setState(TestLEDLogger::SystemState::STARTUP, 
                       TestLEDLogger::LEDPattern::PULSE);
    
    TEST_ASSERT_EQUAL_STRING("STARTUP", 
                            TestLEDLogger::systemStateToString(
                                ledLogger.getCurrentState()).c_str());
}

void test_led_logger_multiple_state_changes(void) {
    ledLogger.setState(TestLEDLogger::SystemState::IDLE, 
                       TestLEDLogger::LEDPattern::OFF);
    ledLogger.setState(TestLEDLogger::SystemState::NORMAL, 
                       TestLEDLogger::LEDPattern::SOLID);
    ledLogger.setState(TestLEDLogger::SystemState::BUSY, 
                       TestLEDLogger::LEDPattern::PULSE);
    
    TEST_ASSERT_EQUAL_UINT(3, ledLogger.getLogSize());
}

void test_led_logger_update_when_inactive(void) {
    ledLogger.setState(TestLEDLogger::SystemState::IDLE, 
                       TestLEDLogger::LEDPattern::OFF);
    
    // Advance time
    for (int i = 0; i < 100; i++) {
        ledLogger.update();
    }
    
    TEST_ASSERT_FALSE(ledLogger.isActiveLED());
}

void test_led_logger_update_timeout(void) {
    TestLEDLogger::setMillisMock(0);
    ledLogger.setState(TestLEDLogger::SystemState::NORMAL, 
                       TestLEDLogger::LEDPattern::SOLID);
    
    // Advance time past timeout
    TestLEDLogger::setMillisMock(2500);
    ledLogger.update();
    
    TEST_ASSERT_FALSE(ledLogger.isActiveLED());
}

void test_led_logger_update_blink_pattern(void) {
    TestLEDLogger::setMillisMock(0);
    ledLogger.setState(TestLEDLogger::SystemState::BUSY, 
                       TestLEDLogger::LEDPattern::BLINK);
    
    // Check blink pattern behavior
    TestLEDLogger::setMillisMock(100);
    ledLogger.update();
    TEST_ASSERT_TRUE(ledLogger.isActiveLED());
    
    TestLEDLogger::setMillisMock(600);
    ledLogger.update();
    // Blink should cycle
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_led_logger_initialization);
    RUN_TEST(test_led_logger_set_idle_state);
    RUN_TEST(test_led_logger_set_normal_state);
    RUN_TEST(test_led_logger_set_busy_state);
    RUN_TEST(test_led_logger_set_error_state);
    RUN_TEST(test_led_logger_set_warning_state);
    RUN_TEST(test_led_logger_set_startup_state);
    RUN_TEST(test_led_logger_multiple_state_changes);
    RUN_TEST(test_led_logger_update_when_inactive);
    RUN_TEST(test_led_logger_update_timeout);
    RUN_TEST(test_led_logger_update_blink_pattern);
    
    return UNITY_END();
}
