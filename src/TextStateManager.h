// TextStateManager.h
#ifndef TEXT_STATE_MANAGER_H
#define TEXT_STATE_MANAGER_H

#ifdef NATIVE_BUILD


#else
#include <Arduino.h>
#endif

class TextStateManager
{
public:
  enum class DisplayState
  {
    IDLE,
    RECORDING,
    THINKING,
    RESPONSE,
    ERROR
  };

  TextStateManager() : currentState(DisplayState::IDLE),
                       lastUpdateTime(0),
                       periodCount(0),
                       maxPeriods(10),
                       responseStartTime(0),
                       responseDisplayDuration(5000) // 5 seconds
  {
  }

  void update(unsigned long currentTime)
  {
    switch (currentState)
    {
    case DisplayState::RECORDING:
      updateRecordingText(currentTime);
      break;
    case DisplayState::THINKING:
      updateThinkingText(currentTime);
      break;
    case DisplayState::RESPONSE:
      updateResponseText(currentTime);
      break;
    default:
      break;
    }
  }

#ifdef NATIVE_BUILD
  void setState(DisplayState newState, const std::string &response = "")
#else
  void setState(DisplayState newState, const String &response = "")
#endif
  {
    currentState = newState;
#ifdef NATIVE_BUILD
    lastUpdateTime = currentTime;
#else
    lastUpdateTime = millis();
#endif
    periodCount = (newState == DisplayState::RECORDING) ? maxPeriods : 0;

    if (newState == DisplayState::RESPONSE)
    {
      responseText = response;
#ifdef NATIVE_BUILD
      responseStartTime = currentTime;
#else
      responseStartTime = millis();
#endif
    }
  }

  DisplayState getState() const
  {
    return currentState;
  }

#ifdef NATIVE_BUILD
  std::string getCurrentText()
#else
  String getCurrentText()
#endif
  {
    switch (currentState)
    {
    case DisplayState::IDLE:
#ifdef NATIVE_BUILD
      return "Magic\nGPT8\n\nShake me";
#else
      return String("Magic\nGPT8\n\nShake me");
#endif
    case DisplayState::ERROR:
#ifdef NATIVE_BUILD
      return "Wifi: X";
#else
      return String("Wifi: X");
#endif
    case DisplayState::RESPONSE:
      return responseText;
    default:
      return lastGeneratedText;
    }
  }

private:
  DisplayState currentState;
  unsigned long lastUpdateTime;
  int periodCount;
  const int maxPeriods;
#ifdef NATIVE_BUILD
  std::string lastGeneratedText;
  std::string responseText;
  unsigned long responseStartTime;
  const unsigned long responseDisplayDuration = 5000;
#else
  String lastGeneratedText;
  String responseText;
  unsigned long responseStartTime;
  const unsigned long responseDisplayDuration;
#endif

  void updateRecordingText(unsigned long currentTime)
  {
    if (currentTime - lastUpdateTime >= 1000)
    { // Update every second
      lastUpdateTime = currentTime;
      periodCount = max(0, periodCount - 1);

      if (periodCount <= 2)
      {
#ifdef NATIVE_BUILD
        lastGeneratedText = "Thinking";
#else
        lastGeneratedText = "Thinking";
#endif
      }
      else
      {
#ifdef NATIVE_BUILD
        std::string text = "Speak Now";
#else
        String text = "Speak Now";
#endif
        for (int i = 0; i < periodCount; i++)
        {
          text += " .";
        }
        lastGeneratedText = text;
      }
    }
  }

  void updateThinkingText(unsigned long currentTime)
  {
    if (currentTime - lastUpdateTime >= 500)
    { // Update every half second
      lastUpdateTime = currentTime;
      periodCount = (periodCount + 1) % 4; // 0 to 3 periods

#ifdef NATIVE_BUILD
      std::string text = "Thinking";
#else
      String text = "Thinking";
#endif
      for (int i = 0; i < periodCount; i++)
      {
        text += ".";
      }
      lastGeneratedText = text;
    }
  }

  void updateResponseText(unsigned long currentTime)
  {
    if (currentTime - responseStartTime >= responseDisplayDuration)
    {
      setState(DisplayState::IDLE);
    }
  }
};

#endif // TEXT_STATE_MANAGER_H