import subprocess
import sys
import os
import platform


venv_dir = "venv"
python = sys.executable

if not os.path.exists(venv_dir):
    subprocess.run([python, "-m", "venv", venv_dir], check=True)

pip_exe = (
    os.path.join(venv_dir, "Scripts", "pip.exe")
    if platform.system() == "Windows"
    else os.path.join(venv_dir, "bin", "pip")
)

subprocess.run([pip_exe, "install", "-r", "requirements.txt"], check=True)