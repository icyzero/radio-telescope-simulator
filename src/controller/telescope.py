# src/controller/telescope.py

import math

class Telescope:
    def __init__(self, slew_rate=2.0):
        """slew_rate : degrees per second"""

        self.alt = 0.0
        self.az = 0.0

        self.target_alt = None
        self.target_az = None

        self.slew_rate = slew_rate
        self.state = "IDLE"

    def move_to(self, alt, az):
        self.target_alt = alt
        self.target_az = az
        self.state = "MOVING"
        print(f"[COMMAN] Move to Alt={alt}, Az={az}")

    def stop(self):
        self.state = "STOPPED"
        self.target_alt = None
        self.target_az = None
        print("[COMMAND] Stop")

    def update(self, dt):
        """dt : time step in seconds"""

        if self.state != "MOVING":
            return
        
        d_alt = self.target_alt - self.alt
        d_az = self.target_az - self.az

        distance = math.sqrt(d_alt**2 + d_az**2)

        if distance < 0.01:
            self.alt = self.target_alt
            self.az = self.target_az
            self.state = "IDLE"
            print("[STATE] Target reached")
            return
        
        step = self.slew_rate * dt

        ratio = min(step / distance, 1.0)
            
        self.alt += d_alt * ratio
        self.az += d_az * ratio

        print(f"[UPDATE] Alt={self.alt:.2f},Az={self.az:.2f}")