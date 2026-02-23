#ifndef CONFIG_H
#define CONFIG_H

// WiFi Configuration
// TODO: Replace with your actual WiFi credentials
// For security, consider using environment variables or a secure storage mechanism
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// API Configuration
// TODO: Replace with your actual API key
#define OPENAI_API_KEY "YOUR_OPENAI_API_KEY"

// Display Configuration
#define DISPLAY_WIDTH 240
#define DISPLAY_HEIGHT 320

// Shake Detection Configuration
#define SHAKE_THRESHOLD 20.0  // Threshold for shake detection in G units
#define SHAKE_DEBOUNCE_MS 500  // Debounce time for shake detection

#endif // CONFIG_H
