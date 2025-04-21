from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import json
from neurosdk.scanner import Scanner
from em_st_artifacts.utils import lib_settings
from em_st_artifacts.utils import support_classes
from em_st_artifacts import emotional_math
from neurosdk.cmn_types import *
from time import sleep

app = FastAPI()

# Global variable to store active WebSocket connections
active_connections = set()

# Function to initialize the sensor and return a sensor object
def initialize_sensor():
    scanner = Scanner([SensorFamily.LEBrainBit, SensorFamily.LEBrainBitBlack])
    scanner.sensorsChanged = sensor_found
    scanner.start()
    sleep(25)  # Wait for sensors to be discovered
    scanner.stop()

    sensorsInfo = scanner.sensors()
    for current_sensor_info in sensorsInfo:
        sensor = scanner.create_sensor(current_sensor_info)
        sensor.sensorStateChanged = on_sensor_state_changed
        sensor.batteryChanged = on_battery_changed
        sensor.signalDataReceived = on_signal_received
        sensor.resistDataReceived = on_resist_received

        sensor.exec_command(SensorCommand.StartResist)
        sleep(20)
        sensor.exec_command(SensorCommand.StopResist)

        # Initialize Emotion detection library
        math = initialize_emotion_lib()

        return sensor, math

# Initialize emotion processing library
def initialize_emotion_lib():
    mls = lib_settings.MathLibSetting(sampling_rate=250, process_win_freq=25, bipolar_mode=True)
    ads = lib_settings.ArtifactDetectSetting(art_bord=110, allowed_percent_artpoints=70)
    sads = lib_settings.ShortArtifactDetectSetting(ampl_art_detect_win_size=200)
    mss = lib_settings.MentalAndSpectralSetting(n_sec_for_averaging=2, n_sec_for_instant_estimation=4)

    math = emotional_math.EmotionalMath(mls, ads, sads, mss)
    math.set_calibration_length(6)
    math.set_mental_estimation_mode(False)
    return math

# Event handlers for sensor data
def sensor_found(scanner, sensors):
    for index in range(len(sensors)):
        print('Sensor found: %s' % sensors[index])

def on_sensor_state_changed(sensor, state):
    print('Sensor {0} is {1}'.format(sensor.name, state))

def on_battery_changed(sensor, battery):
    print('Battery: {0}'.format(battery))

def on_signal_received(sensor, data):
    raw_channels = []
    for sample in data:
        left_bipolar = sample.T3-sample.O1
        right_bipolar = sample.T4-sample.O2
        raw_channels.append(support_classes.RawChannels(left_bipolar, right_bipolar))

    # Process signal data
    math.push_data(raw_channels)
    math.process_data_arr()

    if not math.calibration_finished():
        print("Calibration percents: {0}".format(math.get_calibration_percents()))
    else:
        mental_data = math.read_mental_data_arr()
        if len(mental_data) > 0:
            print("Mental data: {0}".format(mental_data))

        spectral_data = math.read_spectral_data_percents_arr()
        if len(spectral_data) > 0:
            print("Spectral data: {0}".format(spectral_data))

        # Here, you can yield the data as output via the websocket
        for conn in active_connections:
            try:
                conn.send_text(json.dumps({"mental_data": mental_data, "spectral_data": spectral_data}))
            except:
                active_connections.remove(conn)

def on_resist_received(sensor, data):
    print("O1 resist is normal: {0}. Current O1 resist {1}".format(data.O1 < 2000000, data.O1))

# WebSocket route to stream data
@app.websocket("/ws/eeg_data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    sensor, math = initialize_sensor()

    try:
        while True:
            # Run EEG signal collection
            if sensor.is_supported_command(SensorCommand.StartSignal):
                sensor.exec_command(SensorCommand.StartSignal)
                math.start_calibration()
                sleep(120)  # Wait for calibration to complete
                sensor.exec_command(SensorCommand.StopSignal)

            # Yielding mental data and spectral data via WebSocket
            mental_data = math.read_mental_data_arr()
            spectral_data = math.read_spectral_data_percents_arr()
            await websocket.send_text(json.dumps({"mental_data": mental_data, "spectral_data": spectral_data}))

            await asyncio.sleep(1)  # Delay to allow for continuous data flow

    except WebSocketDisconnect:
        active_connections.remove(websocket)

# Run the FastAPI app with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
