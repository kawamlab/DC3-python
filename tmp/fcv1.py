from dc3client.dc3clikent import SocketClient
import math
import sys
import os
import DigitalCurling3



class SimulatorFCV1():
    def longitudinal(self, y_velocity):
        kGravity = 9.80665
        return -(0.00200985 / (y_velocity + 0.06385782) + 0.00626286) * kGravity
    
    def yaw_rate(self, y_velocity, angular_velocity):
        if angular_velocity <= 0.01:
            return 0
        if angular_velocity > 0.0:
            return 1.0 * 0.00820 * math.pow(y_velocity, -0.8)
        else:
            return -1.0 * 0.00820 * math.pow(y_velocity, -0.8)
        
    def angular_acceleration(self, linearSpeed):
        clampedSpeed = max(linearSpeed, 0.001)
        return -0.025 / clampedSpeed
    

    def simulator(self, x_velocity, y_velocity, angle, linearspeed):
        DigitalCurling3.
