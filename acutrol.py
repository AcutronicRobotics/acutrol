import socket
from threading import Lock
import time
import json
import os
import inspect
MODULE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

MODE_NONE     = 0
MODE_POSITION = 1
MODE_RATE     = 2

class AcutrolDevice:
    def __init__(self, IP='192.168.1.53', PORT=9888, command_dict=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((IP, PORT))
        self.mode = MODE_NONE
        self.L = Lock()

        if command_dict <> None: 
            self.command_dict = command_dict
        else:                    
            self.command_dict = json.load(open(os.path.join(MODULE_PATH, 'ac117.json'), 'r'))
       
        self.startup()

    def startup(self):
        result = self.send_command_list(self.command_dict['startup'])
        time.sleep(.5)
        return result

    def shutdown(self):
        result = self.send_command_list(self.command_dict['shutdown'])
        time.sleep(.5)
        return result

    def send_command_list(self, command_list):
        success = True
        for command in command_list:
            success = (success and 
                       (self.send_command(command[0]) == command[1]))
            time.sleep(.25)
        return success

    def send_command(self, command):
        with self.L: 
            self.sock.send(str(command) + '\r\n')
            return self.sock.recv(1024)[8:]

    def status(self):
        return {'velocity' : float(self.send_command(':read:rate 1')) * 0.0174532925, 
                'position' : float(self.send_command(':read:position 1')) * 0.0174532925}
        
    def command_position(self, position_rad):
        position_str_deg = format(((57.2957795 * float(position_rad)) % 360), '06.3f')
        if self.mode == MODE_POSITION:
            self.send_command(':demand:position 1, ' + position_str_deg)
        else:
            if self.mode == MODE_RATE: 
                self.command_rate(0)
                time.sleep(.5)
            self.send_command(':mode:position 1')
            time.sleep(.5)
            self.send_command(':demand:position 1, ' + position_str_deg)
            self.mode = MODE_POSITION

    def command_rate(self, rate_rad):
        rate_str_deg = format((57.2957795 * float(rate_rad)), '06.3f')
        if self.mode == MODE_RATE:
            self.send_command(':demand:rate 1, ' + rate_str_deg)
        else:
            self.send_command(':mode:rate 1')
            time.sleep(.5)
            self.send_command(':demand:rate 1, ' + rate_str_deg)
            self.mode = MODE_RATE

if __name__ == '__main__':
    ac = AcutrolDevice()
