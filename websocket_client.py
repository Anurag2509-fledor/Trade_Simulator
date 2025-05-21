import asyncio
import json
import logging
import websockets
from PyQt6.QtCore import QObject, pyqtSignal
from utils.config import Config

logger = logging.getLogger(__name__)

class WebSocketClient(QObject):
    data_received = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.ws_url = Config.WEBSOCKET_URL
        self.running = False
        self.websocket = None
        self.reconnect_attempts = 0
        
    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.ws_url)
            logger.info("WebSocket connection established")
            self.running = True
            self.reconnect_attempts = 0
            await self.receive_messages()
        except Exception as e:
            logger.error(f"WebSocket connection error: {str(e)}")
            self.running = False
            await self.handle_reconnect()
            
    async def handle_reconnect(self):
        if self.reconnect_attempts < Config.MAX_RECONNECT_ATTEMPTS:
            self.reconnect_attempts += 1
            logger.info(f"Attempting to reconnect (attempt {self.reconnect_attempts})")
            await asyncio.sleep(Config.RECONNECT_DELAY)
            await self.connect()
        else:
            logger.error("Max reconnection attempts reached")
            
    async def receive_messages(self):
        while self.running:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)
                self.data_received.emit(data)
            except websockets.exceptions.ConnectionClosed:
                logger.error("WebSocket connection closed")
                self.running = False
                await self.handle_reconnect()
                break
            except Exception as e:
                logger.error(f"Error receiving message: {str(e)}")
                
    async def close(self):
        if self.websocket:
            await self.websocket.close()
            self.running = False
            logger.info("WebSocket connection closed")
            
    def start(self):
        asyncio.create_task(self.connect())
        
    def stop(self):
        self.running = False
        if self.websocket:
            asyncio.create_task(self.close()) 