from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
import asyncio
import socketio
from socketio import AsyncServer
from .audio_processor import AudioProcessor
from .plugin_manager import PluginManager
from .report import generate_html_report
import logging

app = FastAPI(title="Audio Testing Application")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Socket.IO
sio = AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

plugin_manager = PluginManager()
audio_processor = AudioProcessor(plugin_manager)

logger = logging.getLogger(__name__)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class AnalysisConfig(BaseModel):
    audio_resource: str
    plugins: List[Dict[str, Any]]
    sample_rate: int = 44100
    chunk_size: int = 1024
    frequency: int = 1

class TaskID(BaseModel):
    task_id: str

@app.get("/")
async def root():
    with open("templates/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@sio.on('connect')
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")

@sio.on('disconnect')
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

async def update_clients(data):
    await sio.emit('update', data)

@app.post("/start_analysis")
async def start_analysis(config: AnalysisConfig):
    try:
        logger.info(f"Received analysis config: {config.dict()}")
        task_id = str(uuid.uuid4())
        asyncio.create_task(audio_processor.process_audio(config.dict(), task_id, update_clients))
        return {"task_id": task_id}
    except Exception as e:
        logger.error(f"Error starting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting analysis: {str(e)}")

@app.post("/stop_analysis")
async def stop_analysis(task: TaskID):
    success = audio_processor.stop_task(task.task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task.task_id, "status": "stopped"}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    status = audio_processor.get_task_status(task_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task_id, "status": status}

@app.get("/report/{task_id}")
async def get_report(task_id: str):
    results = audio_processor.get_report(task_id)
    if results is None:
        raise HTTPException(status_code=404, detail="Report not found")
    report_path = generate_html_report(task_id, results)
    return {"task_id": task_id, "report_path": report_path}

@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    # TODO: Implement audio file processing
    return {"filename": file.filename, "message": "Audio file uploaded successfully"}

@app.get("/plugins")
async def get_plugins():
    return {"plugins": list(plugin_manager.plugins.keys())}

# Use the Socket.IO ASGI app as the main app
app = socket_app