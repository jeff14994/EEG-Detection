from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import time
import random
import json
import logging
import os
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simulator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (simulator)
parent_dir = os.path.dirname(current_dir)

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(parent_dir, "static")), name="static")

def generate_eeg_data():
    """Generate simulated EEG data in the specified format"""
    data = {}
    for i in range(1, 20):
        # Generate random values similar to the example data
        value = random.uniform(-20, 20)
        data[f"c{i}"] = round(value, 4)
    logger.debug(f"Generated EEG data: {data}")
    return data

@app.websocket("/ws/eeg_data")
async def eeg_data(websocket: WebSocket):
    logger.info("New WebSocket connection request received")
    try:
        await websocket.accept()
        logger.info("WebSocket connection established")
        
        # Create a task for sending data
        async def send_data():
            while True:
                try:
                    # Generate simulated EEG data
                    eeg_data = generate_eeg_data()
                    
                    # Prepare response
                    response = {
                        "data": eeg_data,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    logger.debug(f"Sending data: {response}")
                    
                    # Send data to frontend
                    await websocket.send_json(response)
                    
                    # Update every second
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error in data generation/sending: {str(e)}", exc_info=True)
                    break
        
        # Create a task for receiving data (ping/pong)
        async def receive_data():
            while True:
                try:
                    # Wait for any message (ping)
                    await websocket.receive_text()
                except WebSocketDisconnect:
                    logger.info("Client disconnected")
                    break
                except Exception as e:
                    logger.error(f"Error in receive: {str(e)}", exc_info=True)
                    break
        
        # Run both tasks concurrently
        send_task = asyncio.create_task(send_data())
        receive_task = asyncio.create_task(receive_data())
        
        # Wait for either task to complete
        done, pending = await asyncio.wait(
            [send_task, receive_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel any pending tasks
        for task in pending:
            task.cancel()
            
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}", exc_info=True)
    finally:
        try:
            await websocket.close()
            logger.info("WebSocket connection closed")
        except:
            pass

@app.get("/")
async def read_root():
    """Serve the main HTML file"""
    logger.info("Serving main HTML file")
    return FileResponse(os.path.join(parent_dir, "test.html"))

@app.get("/api/status")
async def get_status():
    """API endpoint to check server status"""
    return {"status": "running", "timestamp": datetime.utcnow().isoformat()} 