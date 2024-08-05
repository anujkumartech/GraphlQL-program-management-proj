import requests
import time
import sys
from collections import deque

def check_api_status():
    graphql_url = 'http://3.90.142.223:5001/graphql'
    query = """
    {
      __typename
    }
    """
    try:
        response = requests.post(
            graphql_url,
            json={'query': query},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            return True, "API is up and running"
        elif response.status_code == 503:
            return False, "API is down (503 Service Unavailable)"
        else:
            return False, f"API status: {response.status_code}"
    except Exception as err:
        return False, f"Error checking API status: {err}"

def record_retry_info(trace_id, retries, duration, type_of_retry):
    retry_info_url = 'http://localhost:5001/save-retry-info'
    payload = {
        "traceId": trace_id,
        "retries": retries,
        "duration": duration,
        "typeOfRetry": type_of_retry
    }
    try:
        response = requests.post(
            retry_info_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 201:
            print("Retry information saved successfully.")
        else:
            print(f"Failed to save retry information. Status code: {response.status_code}")
    except Exception as err:
        print(f"Error saving retry information: {err}")

def main(trace_id):
    max_attempts = 60  # Total number of API calls
    interval = 1       # Time interval between each call (in seconds)
    max_retries = 60   # Maximum number of retry attempts
    initial_retry_delay = 1  # Initial delay between retry attempts (in seconds)
    success_threshold = 0.8  # Desired success rate threshold
    success_window = 10  # Number of recent attempts to consider for success rate

    recent_attempts = deque(maxlen=success_window)
    retry_delay = initial_retry_delay

    total_attempts = 0
    total_successes = 0

    print("Starting the script...")

    for attempt in range(max_attempts):
        is_successful, status = check_api_status()
        total_attempts += 1
        if is_successful:
            total_successes += 1
        print(f"Attempt {attempt + 1}: {status}")

        # Update recent attempts deque and calculate success rate
        recent_attempts.append(is_successful)
        success_rate = sum(recent_attempts) / len(recent_attempts) if recent_attempts else 0

        if not is_successful:
            # Track retries and duration of fault
            retry_count = 0
            fault_start_time = time.time()

            for retry in range(max_retries):
                retry_count += 1
                time.sleep(retry_delay)
                print(f"Retry {retry + 1} for fault detected with delay {retry_delay} seconds.")
                
                # Check the API status again
                is_successful, status = check_api_status()
                total_attempts += 1
                if is_successful:
                    total_successes += 1

                # Update recent attempts and success rate after each retry
                recent_attempts.append(is_successful)
                success_rate = sum(recent_attempts) / len(recent_attempts) if recent_attempts else 0

                if is_successful:
                    fault_duration = int((time.time() - fault_start_time) * 1000)  # Duration in milliseconds
                    print("API is back up.")
                    # Record successful retry information
                    record_retry_info(trace_id, retry_count, fault_duration, "SUCCESS_RATE_BASED")
                    break

                # Adjust retry delay based on success rate
                if success_rate < success_threshold:
                    retry_delay = min(retry_delay * 2, 60)  # Exponential backoff with cap
                    print(f"Decreasing success rate detected. Increasing retry delay to {retry_delay} seconds.")
                else:
                    retry_delay = max(retry_delay / 2, 1)  # Decrease delay if success rate is high
                    print(f"Increasing success rate detected. Decreasing retry delay to {retry_delay} seconds.")

        time.sleep(interval)

    # Calculate and print the overall success rate at the end of the script
    overall_success_rate = total_successes / total_attempts if total_attempts > 0 else 0
    print(f"Script completed. Overall success rate: {overall_success_rate:.2%}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        trace_id = sys.argv[1]  # Get trace_id from command-line argument
    else:
        raise ValueError("Error: A trace_id must be provided as a command-line argument")

    main(trace_id)