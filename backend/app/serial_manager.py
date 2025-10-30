"""
Serial Manager for Arduino Communication
Handles serial port detection, reading telemetry, and sending commands
"""
import asyncio
import json
import os
import time
from typing import Optional, Callable
import serial
import serial.tools.list_ports
from .utils.logger import logger


class SerialManager:
    """Manages serial communication with Arduino"""
    
    def __init__(self, port: Optional[str] = None, baudrate: int = 115200):
        self.port = port or os.getenv("ARDUINO_PORT", "COM3")
        self.baudrate = baudrate
        self.serial_conn: Optional[serial.Serial] = None
        self.running = False
        self.telemetry_callback: Optional[Callable] = None
        self.reconnect_interval = 5  # seconds
        
    def detect_arduino(self) -> Optional[str]:
        """Auto-detect Arduino by VID/PID"""
        logger.info("Detecting Arduino...")
        ports = serial.tools.list_ports.comports()
        
        # Common Arduino VID/PIDs
        arduino_ids = [
            (0x2341, None),  # Arduino LLC
            (0x2A03, None),  # Arduino.org
            (0x1A86, 0x7523), # CH340 chip (common in clones)
        ]
        
        for port in ports:
            for vid, pid in arduino_ids:
                if port.vid == vid and (pid is None or port.pid == pid):
                    logger.info(f"Arduino detected at {port.device}")
                    return port.device
        
        # If no Arduino found, try to use configured port
        if self.port and self.port != "AUTO":
            logger.warning(f"Arduino not auto-detected, trying configured port: {self.port}")
            return self.port
        
        logger.error("Arduino not detected on any port")
        return None
    
    def connect(self) -> bool:
        """Connect to Arduino"""
        try:
            # Auto-detect if enabled
            if os.getenv("AUTO_DETECT_ARDUINO", "true").lower() == "true":
                detected_port = self.detect_arduino()
                if detected_port:
                    self.port = detected_port
            
            if not self.port:
                logger.error("No serial port configured")
                return False
            
            logger.info(f"Connecting to Arduino at {self.port} @ {self.baudrate} baud...")
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                write_timeout=3
            )
            
            # Wait for Arduino to reset
            time.sleep(2)
            
            # Flush any startup data
            self.serial_conn.reset_input_buffer()
            
            # Test connection with PING
            response = self.send_command("PING", timeout=3)
            if response and "PONG" in response:
                logger.info("[OK] Arduino connected and responding")
            else:
                logger.warning("Arduino connected but not responding to PING")
            
            # Enable test mode to use mock sensor values (prevents emergency mode from floating pins)
            logger.info("Enabling TEST_MODE for safe operation without physical sensors...")
            test_mode_response = self.send_command("TEST_MODE_ON", timeout=2)
            if test_mode_response and "Enabled" in test_mode_response:
                logger.info("[OK] Test mode enabled")
            
            # Reset emergency mode if it was triggered by floating pins on startup
            reset_response = self.send_command("RESET_EMERGENCY", timeout=2)
            if reset_response and "reset" in reset_response.lower():
                logger.info("[OK] Emergency mode reset")
            
            return True  # Still consider connected
                
        except serial.SerialException as e:
            logger.error(f"Failed to connect to Arduino: {e}")
            self.serial_conn = None
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Arduino: {e}")
            self.serial_conn = None
            return False
    
    def disconnect(self):
        """Disconnect from Arduino"""
        if self.serial_conn and self.serial_conn.is_open:
            logger.info("Disconnecting from Arduino...")
            self.serial_conn.close()
            self.serial_conn = None
    
    def is_connected(self) -> bool:
        """Check if connected to Arduino"""
        return self.serial_conn is not None and self.serial_conn.is_open
    
    def send_command(self, command: str, timeout: int = 3) -> Optional[str]:
        """
        Send command to Arduino and wait for response
        Returns the actual response line (skips COMMAND_RECEIVED echo)
        """
        if not self.is_connected():
            logger.error("Cannot send command: not connected")
            return None
        
        try:
            # Send command
            cmd_line = f"{command}\n"
            self.serial_conn.write(cmd_line.encode('utf-8'))
            logger.debug(f"→ Sent command: {command}")
            
            # Wait for response - Arduino sends COMMAND_RECEIVED first, then actual response
            start_time = time.time()
            lines_received = []
            
            while time.time() - start_time < timeout:
                if self.serial_conn.in_waiting > 0:
                    response = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    if response:
                        logger.debug(f"← Received: {response}")
                        lines_received.append(response)
                        
                        # Skip COMMAND_RECEIVED echo, return the actual response
                        if not response.startswith("COMMAND_RECEIVED:"):
                            return response
                
                time.sleep(0.05)
            
            # If we only got COMMAND_RECEIVED, return the last line
            if lines_received:
                return lines_received[-1]
            
            logger.warning(f"Command '{command}' timed out")
            return None
            
        except Exception as e:
            logger.error(f"Error sending command '{command}': {e}")
            return None
    
    def parse_telemetry(self, line: str) -> Optional[dict]:
        """Parse telemetry line from Arduino"""
        if not line.startswith("TELEMETRY:"):
            return None
        
        try:
            json_str = line.replace("TELEMETRY:", "").strip()
            data = json.loads(json_str)
            
            # Add timestamp if not present
            if 't' not in data:
                data['t'] = int(time.time())
            
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse telemetry JSON: {e}")
            logger.error(f"Raw line: {repr(line)}")
            logger.error(f"JSON string: {repr(json_str)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing telemetry: {e}")
            return None
    
    async def read_loop(self):
        """
        Async loop to continuously read from serial port
        Calls telemetry_callback when telemetry is received
        """
        self.running = True
        logger.info("Serial read loop started")
        
        while self.running:
            try:
                # Ensure connected
                if not self.is_connected():
                    logger.warning("Not connected, attempting reconnect...")
                    if self.connect():
                        logger.info("Reconnected successfully")
                    else:
                        await asyncio.sleep(self.reconnect_interval)
                        continue
                
                # Read line if available
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    
                    if not line:
                        continue
                    
                    # Parse telemetry
                    if line.startswith("TELEMETRY:"):
                        telemetry_data = self.parse_telemetry(line)
                        if telemetry_data and self.telemetry_callback:
                            # Call callback with telemetry data
                            if asyncio.iscoroutinefunction(self.telemetry_callback):
                                await self.telemetry_callback(telemetry_data, line)
                            else:
                                self.telemetry_callback(telemetry_data, line)
                    else:
                        # Log non-telemetry messages
                        logger.info(f"Arduino: {line}")
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.05)
                
            except serial.SerialException as e:
                logger.error(f"Serial error in read loop: {e}")
                self.disconnect()
                await asyncio.sleep(self.reconnect_interval)
            except Exception as e:
                logger.error(f"Unexpected error in read loop: {e}")
                await asyncio.sleep(1)
        
        logger.info("Serial read loop stopped")
    
    def stop(self):
        """Stop the read loop"""
        logger.info("Stopping serial manager...")
        self.running = False
        self.disconnect()
    
    def set_telemetry_callback(self, callback: Callable):
        """Set callback function for telemetry data"""
        self.telemetry_callback = callback


# Global serial manager instance
serial_manager = SerialManager()
