from fastapi import FastAPI, WebSocket
from datetime import datetime
import time
from . import app
from .eeg_data import get_eeg_data_from_device
from .preprocess import preprocess_eeg_data, extract_features
from .classify import model

@app.websocket("/ws/eeg_data")
async def eeg_data(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Get raw EEG data from device
            eeg_data = get_eeg_data_from_device()
            
            # Preprocess the data
            processed_data = preprocess_eeg_data(eeg_data)
            
            # Extract features
            features = extract_features(processed_data)
            
            # Classify data
            prediction = model.predict([features])
            
            # Prepare response
            response = {
                "features": features,
                "emotion": prediction[0],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send data to frontend
            await websocket.send_json(response)
            
            # Update every second
            time.sleep(1)
            
    except Exception as e:
        print(f"Error in WebSocket connection: {e}")
    finally:
        await websocket.close()

@app.get("/")
async def root():
    return {"message": "EEG Analysis API is running"} 