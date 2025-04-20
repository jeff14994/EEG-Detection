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

# Generate EEG data
def generate_eeg_data():
    return {
        'timestamp': time.time(),
        'data': {
            'O1': random.uniform(-10, 10),
            'O2': random.uniform(-8, 8),
            'T3': random.uniform(-12, 12),
            'T4': random.uniform(-6, 6)
        }
    }

@app.websocket("/ws/eeg_data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info(f"WebSocket connection established: {websocket}")
    active_connections.add(websocket)
    
    try:
        # Send data at 60Hz
        while True:
            data = generate_eeg_data()
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(1/60)  # 60Hz
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