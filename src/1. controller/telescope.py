# src/controller/telescope.py

class Telescope:
    def __init__(self):
        self.alt = 0.0
        self.az = 0.0
        self.state = "IDLE"

    def move_to(self, alt, az):
        self.alt = alt
        self.az = az
        self.state = "MOVING"

    def stop(self):
        self.state = "STOPPED"
