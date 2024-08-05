import subprocess
import time
import requests
from concurrent.futures import ThreadPoolExecutor
import uuid

def run_script(script_name, trace_id):
    try:
        subprocess.run(["python3", script_name, trace_id], check=True)
        print(f"{script_name} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")

def trigger_fault_api():
    fault_url = 'http://3.90.142.223:5001/fault/20'
    time.sleep(5)  # Wait for 5 seconds before calling the API
    try:
        response = requests.get(fault_url)
        if response.status_code == 200:
            print("Fault API triggered successfully.")
        else:
            print(f"Fault API call failed with status code: {response.status_code}")
    except Exception as err:
        print(f"Error triggering fault API: {err}")

def main():
    trace_id = str(uuid.uuid4())  # Generate a single trace ID for all scripts
    # scripts = ["simple_retry.py", "incremental_retry.py", "exponential_retry.py"]
    # scripts = ["success_rate_retry.py"]
    scripts = ["success_rate_simple.py"]

    with ThreadPoolExecutor() as executor:
        # Run all scripts in parallel with the same trace ID
        futures = [executor.submit(run_script, script, trace_id) for script in scripts]

        # Trigger the fault API after 5 seconds
        executor.submit(trigger_fault_api)

        # Wait for all scripts to complete
        for future in futures:
            future.result()

if __name__ == "__main__":
    main()