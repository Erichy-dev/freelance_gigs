
import subprocess

# Task parameters
task_name = "MyPythonScriptTask"
time_to_run = "18:00"  # 6 PM

# Create the task
subprocess.run(f'schtasks /create /tn "{task_name}" /tr "D:\git\freelance_gigs\fortnite_image\script.bat" /sc daily /st 19:15', shell=True)
