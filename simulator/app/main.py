from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import socketio
import uvicorn
import aiohttp
import asyncio
import json
import random
import time
import math

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simulator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (simulator)
parent_dir = os.path.dirname(current_dir)

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(parent_dir, "static")), name="static")

# Store active WebSocket connections
active_connections = set()

# Sampling rate
SAMPLING_RATE = 250  # Hz

# Generate more realistic EEG data with frequencies
def generate_eeg_data():
    t = time.time()
    
    # Generate signals with different frequency components for each channel
    # Alpha (8-13 Hz), Beta (13-30 Hz), Theta (4-8 Hz), Delta (0.5-4 Hz)
    alpha = 5 * math.sin(2 * math.pi * 10 * t)  # 10 Hz alpha
    beta = 2 * math.sin(2 * math.pi * 20 * t)   # 20 Hz beta
    theta = 4 * math.sin(2 * math.pi * 6 * t)   # 6 Hz theta
    delta = 3 * math.sin(2 * math.pi * 2 * t)   # 2 Hz delta
    
    # Add some random noise
    noise = random.uniform(-1, 1)
    
    return {
        'timestamp': t,
        'data': {
            'O1': alpha + theta + noise,
            'O2': alpha + beta + noise,
            'T3': theta + delta + noise,
            'T4': beta + delta + noise
        }
    }

@app.websocket("/ws/eeg_data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info(f"WebSocket connection established: {websocket}")
    active_connections.add(websocket)
    
    try:
        # Send data at 250Hz
        while True:
            data = generate_eeg_data()
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(1/SAMPLING_RATE)  # 250Hz
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected")
        active_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        active_connections.discard(websocket)

@app.get("/")
async def read_root():
    """Serve the main HTML file"""
    logger.info("Serving main HTML file")
    return FileResponse(os.path.join(parent_dir, "test.html"))

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify server is running"""
    return {"status": "ok", "message": "Server is running"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ws_ping_interval=5,
        ws_ping_timeout=5,
        log_level="debug"
    ) 