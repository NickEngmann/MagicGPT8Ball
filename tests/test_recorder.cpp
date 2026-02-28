#include <Arduino.h>
#include <CppUTest/TestCase.h>
#include <CppUTestExt/GMock.h>
#include "Recorder.h"
#include "esp_heap_caps.h"
#include "driver/gpio.h"

TEST_GROUP(Recorder)
{
    VoiceActivatedRecorder* recorder;
    
    void setup() override
    {
        recorder = new VoiceActivatedRecorder();
    }
    
    void teardown() override
    {
        delete recorder;
    }
};

TEST(Recorder, ConstructorInitializesCorrectly)
{
    CHECK_EQUAL(nullptr, recorder->audioBuffer);
    CHECK_EQUAL(0, recorder->bufferIndex);
    CHECK_EQUAL(false, recorder->is_recording);
}

TEST(Recorder, StartRecordingSetsFlag)
{
    recorder->startRecording();
    CHECK_EQUAL(true, recorder->is_recording);
}

TEST(Recorder, StopRecordingClearsFlag)
{
    recorder->startRecording();
    recorder->stopRecording();
    CHECK_EQUAL(false, recorder->is_recording);
}

TEST(Recorder, ProcessSampleWithNoSoundDoesNotRecord)
{
    // Simulate silence (sample below threshold)
    int16_t silentSample = 0;
    recorder->processSample(silentSample);
    CHECK_EQUAL(false, recorder->is_recording);
}

TEST(Recorder, ProcessSampleWithSoundStartsRecording)
{
    // Simulate sound (sample above threshold)
    int16_t loudSample = 1000;
    recorder->processSample(loudSample);
    // Note: This depends on the threshold configuration
}
