import subprocess
import time

# A simple function to run a Python script and wait for it to finish
def run_script(script_name):
    print(f"Running {script_name}...")
    result = subprocess.run(['python', script_name], capture_output=True, text=True)
    print(result.stdout)  # Optionally, print the output of the script
    print(result.stderr)  # Optionally, print errors if any

def main():
    # List of scripts in the order they need to be executed
    scripts = [
        "main.py",  # First game (UI game)
        "2.describeempty.py",  # Next step (describe empty)
        "3.empty.py",  # Empty game stage
        "4.describeobstacles.py",  # Next step (describe obstacles)
        "5.obstacles.py",  # Obstacles game stage
    ]

    # Sequentially run each script
    for script in scripts:
        run_script(script)
        time.sleep(1)  # Optional: Add a short delay between scripts

if __name__ == "__main__":
    main()
