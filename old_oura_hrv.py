import requests
import time
from datetime import datetime, timedelta

API_KEY = "GCB6HLCP5FTDPDK3HGFKDAUNUHAKPD4V"
BASE_URL = "https://api.ouraring.com/v2/usercollection/daily_readiness"

def get_readiness_data():
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # Get data for the last 7 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    
    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching readiness data: {e}")
        return None

def display_readiness_data(data):
    if not data or "data" not in data:
        print("No readiness data available")
        return

    print("\n=== Latest Readiness Data ===")
    for entry in data["data"]:
        print(f"\nDate: {entry.get('day')}")
        print(f"Readiness Score: {entry.get('score')}")
        
        contributors = entry.get('contributors', {})
        print("\nContributors:")
        print(f"HRV Balance: {contributors.get('hrv_balance')}")
        print(f"Resting Heart Rate: {contributors.get('resting_heart_rate')}")
        print(f"Previous Night: {contributors.get('previous_night')}")
        print(f"Sleep Balance: {contributors.get('sleep_balance')}")
        print(f"Activity Balance: {contributors.get('activity_balance')}")
        print("-" * 50)

def main():
    print("Starting Oura readiness monitoring...")
    while True:
        data = get_readiness_data()
        display_readiness_data(data)
        time.sleep(5)

if __name__ == "__main__":
    main()
