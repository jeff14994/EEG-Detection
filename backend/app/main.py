from fastapi import FastAPI, WebSocket
from datetime import datetime
import time
import logging
from app import app
from app.eeg_data import get_eeg_data_from_device
from app.preprocess import preprocess_eeg_data, extract_features
from app.classify import model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eeg_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.websocket("/ws/eeg_data")
async def eeg_data(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    try:
        while True:
            # Get raw EEG data from device
            eeg_data = get_eeg_data_from_device()
            logger.debug(f"Raw EEG data received: {eeg_data}")
            
            # Preprocess the data
            processed_data = preprocess_eeg_data(eeg_data)
            logger.debug(f"Processed EEG data: {processed_data}")
            
            # Extract features
            features = extract_features(processed_data)
            logger.debug(f"Extracted features: {features}")
            
            # Classify data
            prediction = model.predict([features])
            logger.info(f"Emotion prediction: {prediction[0]}")
            
            # Prepare response
            response = {
                "features": features,
                "emotion": prediction[0],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send data to frontend
            await websocket.send_json(response)
            logger.debug("Data sent to frontend")
            
            # Update every second
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}", exc_info=True)
    finally:
        await websocket.close()
        logger.info("WebSocket connection closed")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "EEG Analysis API is running"} 