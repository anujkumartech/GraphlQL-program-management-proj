import requests
import time

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
            return "API is up and running"
        elif response.status_code == 503:
            return "API is down (503 Service Unavailable)"
        else:
            return f"API status: {response.status_code}"
    except Exception as err:
        return f"Error checking API status: {err}"

def main():
    duration = 30  # Total duration to run the check (in seconds)
    interval = 1   # Time interval between each check (in seconds)

    start_time = time.time()
    while time.time() - start_time < duration:
        status = check_api_status()
        print(f"API status: {status}")
        time.sleep(interval)

if __name__ == "__main__":
    main()
