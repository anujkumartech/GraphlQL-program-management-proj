import requests
import time 
base_url = 'http://3.90.142.223:5001/fault/'
seconds = 10 # Can be changed for CPU LOAD ig
url = f"{base_url}{seconds}" 

def bring_down_api(seconds):
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(response.text)
        print(f"API will be down for {seconds} seconds...")
        time.sleep(seconds)
        api_status = check_api_status()
        print("API status after downtime:", api_status)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

def check_api_status():
    graphql_url = 'http://3.90.142.223:3000/'
    try:
        response = requests.get(graphql_url)
        if response.status_code == 200:
            return "API is up and running"
        else:
            return f"API status: {response.status_code}"
    except Exception as err:
        return f"Error checking API status: {err}"

if __name__ == "__main__":
    bring_down_api(seconds)