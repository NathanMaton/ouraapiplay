from garminconnect import Garmin
import json
import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
import time

def display_json(data):
    """Helper function to pretty print JSON data"""
    print(json.dumps(data, indent=4))

def get_hrv_data(client, date_str):
    """Get HRV data for a specific date"""
    try:
        # Get heart rate variability data
        hrv_data = client.get_hrv_data(date_str)
        if not hrv_data:
            print(f"No HRV data available for {date_str}")
            return None
        
        # Extract the HRV values and timestamps
        measurements = []
        for item in hrv_data.get('hrvSummaries', []):
            timestamp = item.get('startTimeLocal', '')
            hrv_value = item.get('avgHrv', 0)
            measurements.append({
                'timestamp': timestamp,
                'hrv': hrv_value
            })
        
        return measurements
    except Exception as e:
        print(f"Error fetching HRV data: {e}")
        return None

def monitor_hrv(interval_minutes=5):
    """Monitor HRV data continuously with specified interval"""
    print("Starting Garmin HRV Monitor")
    print("---------------------------")
    
    # Load environment variables
    load_dotenv()
    
    # Get Garmin Connect credentials
    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')
    
    if not email or not password:
        print("Error: Garmin credentials not found in .env file")
        print("Please set GARMIN_EMAIL and GARMIN_PASSWORD in your .env file")
        return
    
    try:
        # Initialize Garmin client
        client = Garmin(email=email, password=password)
        client.login()
        print("Successfully connected to Garmin Connect")
        
        while True:
            today = date.today().strftime("%Y-%m-%d")
            yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            print("Fetching recent HRV data...")
            
            # Get today's and yesterday's data to ensure we have a complete picture
            today_data = get_hrv_data(client, today)
            yesterday_data = get_hrv_data(client, yesterday)
            
            if today_data:
                print("\nToday's HRV measurements:")
                for measurement in today_data:
                    print(f"Time: {measurement['timestamp']}, HRV: {measurement['hrv']}")
            
            if yesterday_data:
                print("\nYesterday's HRV measurements:")
                for measurement in yesterday_data:
                    print(f"Time: {measurement['timestamp']}, HRV: {measurement['hrv']}")
            
            # Calculate statistics if we have data
            if today_data:
                hrv_values = [m['hrv'] for m in today_data]
                avg_hrv = sum(hrv_values) / len(hrv_values)
                max_hrv = max(hrv_values)
                min_hrv = min(hrv_values)
                
                print(f"\nToday's HRV Statistics:")
                print(f"Average HRV: {avg_hrv:.1f}")
                print(f"Maximum HRV: {max_hrv:.1f}")
                print(f"Minimum HRV: {min_hrv:.1f}")
            
            print(f"\nWaiting {interval_minutes} minutes before next update...")
            time.sleep(interval_minutes * 60)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as err:
        print(f"\nError occurred: {err}")
        print("\nTips:")
        print("1. Make sure your email and password are correct")
        print("2. If you use 2FA, you might need to generate an app password")
        print("3. Check your internet connection")

if __name__ == "__main__":
    monitor_hrv()
