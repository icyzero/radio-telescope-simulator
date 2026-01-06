# src/controller/telescope.py
import math

EPSILON = 0.1 #Degrees

class Telescope:
    def __init__(self, slew_rate=2.0):
        """slew_rate : degrees per second"""

        self.alt = 0.0
        self.az = 0.0

        self.alt_step = 0.6 #01.06
        self.az_step  = 2.4 #01.06

        self.target_alt = None
        self.target_az = None

        self.alt_error = 0.0 #01.06 고도 오류 제어
        self.az_error = 0.0 #01.06 방위각 오류 제어

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

        #01.06 지금 위치가 목표에서 얼마나 벗어나 있는지
        self.alt_error = self.target_alt - self.alt #목표 고도 - 현재 고도
        self.az_error = self.target_az - self.az #목표 방위각 - 현재 방위각
        


    #01.06
    def is_target_reached(self):
        return(
            abs(self.alt_error) < EPSILON and
            abs(self.az_error) < EPSILON
        )