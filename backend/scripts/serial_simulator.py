"""
Arduino Serial Simulator
Simulates Arduino behavior for testing without physical hardware
"""
import random
import time
import json
import sys


class ArduinoSimulator:
    """Simulates Arduino serial communication"""
    
    def __init__(self):
        self.valve_state = "CLOSED"
        self.emergency_mode = False
        self.start_time = time.time()
        self.valve_open_time = 0
        self.total_runtime = 0
        
        # Simulation parameters
        self.base_pressure = 2.5
        self.base_concentration = 150.0
        
    def generate_telemetry(self) -> dict:
        """Generate realistic telemetry data"""
        current_time = int(time.time() - self.start_time)
        
        # Simulate pressure with some variation
        p1 = self.base_pressure + random.uniform(-0.5, 0.5)
        p2 = self.base_pressure + random.uniform(-0.5, 0.5)
        
        # Add pressure surge when valve is open
        if self.valve_state == "OPEN":
            p1 += random.uniform(0.2, 0.8)
            p2 += random.uniform(0.2, 0.8)
        
        # Occasionally spike pressure (for testing emergency)
        if random.random() < 0.001:  # 0.1% chance
            p1 += random.uniform(3.0, 4.0)
        
        # Simulate concentration
        c_src = self.base_concentration + random.uniform(-20, 20)
        c_dst = self.base_concentration * 0.8 + random.uniform(-15, 15)
        
        # Occasionally spike concentration (for testing)
        if random.random() < 0.001:  # 0.1% chance
            c_src += random.uniform(300, 400)
        
        return {
            "t": current_time,
            "valve": self.valve_state,
            "p1": round(p1, 2),
            "p2": round(p2, 2),
            "c_src": round(c_src, 2),
            "c_dst": round(c_dst, 2),
            "em": 1 if self.emergency_mode else 0
        }
    
    def process_command(self, command: str) -> str:
        """Process incoming command and return response"""
        command = command.strip().upper()
        
        if command == "PING":
            return "PONG"
        
        elif command == "INFO":
            return (
                "=======================================\n"
                " Smart Water Valve System — Simulator Mode\n"
                " Baud Rate: 115200\n"
                " Commands: OPEN, CLOSE, STATUS, INFO, PING, FORCE_OPEN, RESET_EMERGENCY\n"
                " Safety: Emergency triggers on overpressure or high concentration\n"
                " Telemetry format: TELEMETRY:{...}\n"
                "======================================="
            )
        
        elif command == "STATUS":
            return (
                f"=== SYSTEM STATUS ===\n"
                f"Valve: {self.valve_state}\n"
                f"Emergency: {'YES' if self.emergency_mode else 'NO'}\n"
                f"Total runtime (s): {self.total_runtime}\n"
                f"====================="
            )
        
        elif command == "OPEN":
            if self.emergency_mode:
                return "ERROR: Cannot OPEN — system in EMERGENCY mode."
            
            # Simulate safety checks
            telemetry = self.generate_telemetry()
            if telemetry["p1"] > 6.0 or telemetry["p2"] > 6.0:
                self.emergency_mode = True
                return "ERROR: Overpressure — aborting OPEN."
            
            if telemetry["c_src"] < 10.0:
                return "ERROR: Source concentration too low."
            
            if telemetry["c_dst"] > 400.0:
                return "ERROR: Destination concentration too high."
            
            self.valve_state = "OPEN"
            self.valve_open_time = time.time()
            return "VALVE_OPENED"
        
        elif command == "CLOSE":
            if self.valve_state == "CLOSED":
                return "VALVE_ALREADY_CLOSED"
            
            self.valve_state = "CLOSED"
            if self.valve_open_time > 0:
                runtime = int(time.time() - self.valve_open_time)
                self.total_runtime += runtime
                self.valve_open_time = 0
            return "VALVE_CLOSED"
        
        elif command == "FORCE_OPEN":
            self.valve_state = "OPEN"
            self.valve_open_time = time.time()
            return "VALVE_OPENED"
        
        elif command == "RESET_EMERGENCY":
            self.emergency_mode = False
            return "EVENT: Emergency mode reset successfully."
        
        else:
            return "ERROR: Unknown command"
    
    def run(self):
        """Run the simulator"""
        print("=======================================", flush=True)
        print(" Arduino Serial Simulator — READY", flush=True)
        print(" Listening for commands on stdin...", flush=True)
        print(" Sending telemetry every 1 second", flush=True)
        print("=======================================", flush=True)
        
        last_telemetry = time.time()
        
        try:
            while True:
                # Check for commands on stdin (non-blocking)
                import select
                if sys.platform == 'win32':
                    # Windows doesn't support select on stdin reliably
                    # For Windows, we'll just send telemetry
                    pass
                else:
                    # Unix-like systems
                    if select.select([sys.stdin], [], [], 0)[0]:
                        command = sys.stdin.readline()
                        if command:
                            response = self.process_command(command)
                            print(f"COMMAND_RECEIVED: {command.strip()}", flush=True)
                            print(response, flush=True)
                
                # Send telemetry every second
                current_time = time.time()
                if current_time - last_telemetry >= 1.0:
                    telemetry = self.generate_telemetry()
                    telemetry_line = f"TELEMETRY:{json.dumps(telemetry)}"
                    print(telemetry_line, flush=True)
                    last_telemetry = current_time
                    
                    # Check for emergency conditions
                    if telemetry["p1"] > 6.0 or telemetry["p2"] > 6.0:
                        if not self.emergency_mode:
                            self.emergency_mode = True
                            if self.valve_state == "OPEN":
                                self.valve_state = "CLOSED"
                                print("EVENT: OVER_PRESSURE — emergency mode triggered.", flush=True)
                    
                    if telemetry["c_src"] > 500.0 or telemetry["c_dst"] > 500.0:
                        if not self.emergency_mode:
                            self.emergency_mode = True
                            if self.valve_state == "OPEN":
                                self.valve_state = "CLOSED"
                                print("EVENT: CRITICAL_CONCENTRATION — emergency mode triggered.", flush=True)
                
                time.sleep(0.1)  # Small delay
                
        except KeyboardInterrupt:
            print("\n=== SIMULATOR STOPPED ===", flush=True)


if __name__ == "__main__":
    simulator = ArduinoSimulator()
    simulator.run()
