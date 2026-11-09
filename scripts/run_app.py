import subprocess, sys
subprocess.run([sys.executable, "-m", "streamlit", "run", "app/main.py"], check=True)
