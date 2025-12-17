import os
import sys
import json
import asyncio
import logging
import platform

logger = logging.getLogger(__name__)

class IPCManager:
    """
    Manages the 'Fast Lane' communication (Inter-Process Communication).
    Uses Named Pipes on Windows and Unix Domain Sockets on macOS/Linux.
    Designed for sub-10ms latency for emergency commands.
    """
    
    IS_WINDOWS = platform.system() == "Windows"
    
    # Path configuration
    if IS_WINDOWS:
        PIPE_NAME = r'\\.\pipe\axiom_fast_lane'
    else:
        SOCKET_PATH = "/tmp/axiom_fast_lane.sock"

    def __init__(self, is_server=False):
        self.is_server = is_server
        self.server_task = None
        self.command_queue = asyncio.Queue()
        self.running = False

    async def start_server(self, on_command_callback):
        """
        Starts the IPC server (Brain Side).
        """
        self.running = True
        logger.info(f"🚀 IPC Server starting on {'Named Pipe' if self.IS_WINDOWS else 'Unix Socket'}")
        
        if self.IS_WINDOWS:
            await self._start_windows_server(on_command_callback)
        else:
            await self._start_unix_server(on_command_callback)

    async def send_command(self, command: dict):
        """
        Sends a command to the IPC server (Voice Agent Side).
        """
        logger.info(f"📤 Sending command: {command.get('action')}")
        
        if self.IS_WINDOWS:
            await self._send_windows_command(command)
        else:
            await self._send_unix_command(command)

    # ==========================================
    # UNIX IMPLEMENTATION (MacOS/Linux)
    # ==========================================
    async def _start_unix_server(self, callback):
        if os.path.exists(self.SOCKET_PATH):
            os.remove(self.SOCKET_PATH)
            
        async def handle_client(reader, writer):
            data = await reader.read(1024)
            message = data.decode()
            if message:
                try:
                    cmd = json.loads(message)
                    logger.info(f"📥 Received: {cmd}")
                    await callback(cmd)
                except json.JSONDecodeError:
                    logger.error("❌ Invalid JSON received")
            writer.close()

        server = await asyncio.start_unix_server(handle_client, self.SOCKET_PATH)
        logger.info(f"✅ Unix Socket listening at {self.SOCKET_PATH}")
        async with server:
            await server.serve_forever()

    async def _send_unix_command(self, command: dict):
        try:
            reader, writer = await asyncio.open_unix_connection(self.SOCKET_PATH)
            writer.write(json.dumps(command).encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except FileNotFoundError:
            logger.error("❌ Server not running (Socket not found)")
        except Exception as e:
            logger.error(f"❌ Send error: {e}")

    # ==========================================
    # WINDOWS IMPLEMENTATION (Named Pipes)
    # ==========================================
    async def _start_windows_server(self, callback):
        # On Windows, we need to use win32file/win32pipe which are blocking.
        # For simplicity in this async context, we'll simulate or use a thread.
        # NOTE: Full async Named Pipe server in Python is complex without third-party libs like 'aiofiles' or 'pywin32'.
        # We will use a simplified robust approach suitable for the 'brain_runner'.
        import win32pipe, win32file, pywintypes
        
        logger.info(f"✅ Named Pipe Server created: {self.PIPE_NAME}")
        
        while self.running:
            try:
                # Run blocking pipe operations in a thread executor to keep event loop alive
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._windows_pipe_loop_step, callback)
                
            except Exception as e:
                logger.error(f"❌ Pipe Server Error: {e}")
                await asyncio.sleep(1)

    def _windows_pipe_loop_step(self, callback):
        import win32pipe, win32file
        
        pipe = win32pipe.CreateNamedPipe(
            self.PIPE_NAME,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
            1, 65536, 65536,
            0,
            None
        )
        
        try:
            win32pipe.ConnectNamedPipe(pipe, None)
            
            # Read message
            resp = win32file.ReadFile(pipe, 64*1024)
            if resp[0] == 0: # Success
                msg = resp[1].decode()
                cmd = json.loads(msg)
                # We can't await here because we differ to async loop, 
                # but for 'brain_runner' we might need to queue it.
                # For now, we'll assume the callback handles thread-safety or we queue it.
                asyncio.run_coroutine_threadsafe(callback(cmd), asyncio.get_event_loop())
                
        except Exception as e:
            # logger.error(f"Pipe error: {e}")
            pass
        finally:
            win32file.CloseHandle(pipe)

    async def _send_windows_command(self, command: dict):
        import win32file
        
        try:
            f = win32file.CreateFile(
                self.PIPE_NAME,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0, None,
                win32file.OPEN_EXISTING,
                0, None
            )
            
            data = json.dumps(command).encode()
            win32file.WriteFile(f, data)
            win32file.CloseHandle(f)
            
        except Exception as e:
            logger.error(f"❌ Failed to reach pipe: {e}")
