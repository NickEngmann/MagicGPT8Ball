// Environment.h
#ifndef ENVIRONMENT_H
#define ENVIRONMENT_H

#include <Arduino.h>
#include <LittleFS.h>
#include <FS.h>

class Environment
{
public:
  static bool begin()
  {
    if (!LittleFS.begin(true))
    {
      Serial.println("Failed to mount LittleFS");
      return false;
    }
    return loadEnv();
  }

  static bool loadEnv()
  {
    fs::File file = LittleFS.open("/.env", "r");
    if (!file)
    {
      file = LittleFS.open("/littlefs/.env", "r");
    }
    if (!file)
    {
      Serial.println("No .env file found");
      return false;
    }

    _valtownUrl = "";
    _deviceToken = "";

    while (file.available())
    {
      String line = file.readStringUntil('\n');
      line.trim();

      // Skip empty lines and comments
      if (line.length() == 0 || line.startsWith("#"))
      {
        continue;
      }

      int separatorPos = line.indexOf('=');
      if (separatorPos > 0)
      {
        String key = line.substring(0, separatorPos);
        String value = line.substring(separatorPos + 1);
        key.trim();
        value.trim();

        // Remove quotes if present
        if (value.startsWith("\"") && value.endsWith("\"") && value.length() >= 2)
        {
          value = value.substring(1, value.length() - 1);
        }

        setEnv(key, value);
      }
    }

    file.close();

    // Validate required environment variables
    if (_valtownUrl.isEmpty() || _deviceToken.isEmpty())
    {
      Serial.println("Warning: Incomplete .env configuration");
      if (_valtownUrl.isEmpty())
      {
        Serial.println("Missing: VALTOWN_URL");
      }
      if (_deviceToken.isEmpty())
      {
        Serial.println("Missing: DEVICE_TOKEN");
      }
      return false;
    }

    return true;
  }

  static String getEnv(const String &key)
  {
    if (key == "VALTOWN_URL")
      return _valtownUrl;
    if (key == "DEVICE_TOKEN")
      return _deviceToken;
    return "";
  }

  // Validate that all required environment variables are set
  static bool isValid()
  {
    return !_valtownUrl.isEmpty() && !_deviceToken.isEmpty();
  }

  // Get available environment variables as a list
  static void getAvailableKeys(StringArray &keys)
  {
    keys.add("VALTOWN_URL");
    keys.add("DEVICE_TOKEN");
  }

private:
  static void setEnv(const String &key, const String &value)
  {
    if (key == "VALTOWN_URL")
      _valtownUrl = value;
    if (key == "DEVICE_TOKEN")
      _deviceToken = value;
  }

  static String _valtownUrl;
  static String _deviceToken;
};

// Initialize static members
String Environment::_valtownUrl;
String Environment::_deviceToken;

#endif // ENVIRONMENT_H
