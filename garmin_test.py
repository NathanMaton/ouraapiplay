from garminconnect import Garmin
import json
import os
from datetime import date
from dotenv import load_dotenv

def display_json(data):
    """Helper function to pretty print JSON data"""
    print(json.dumps(data, indent=4))

def main():
    print("Garmin Connect API Test")
    print("----------------------")
    
    # Load environment variables
    load_dotenv()
    
    # Get Garmin Connect credentials from environment variables
    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')
    
    if not email or not password:
        print("Error: Garmin credentials not found in .env file")
        print("Please set GARMIN_EMAIL and GARMIN_PASSWORD in your .env file")
        return
    
    # Initialize API
    try:
        print("\nAttempting to connect to Garmin Connect...")
        client = Garmin(email=email, password=password)
        client.login()
        
        # Get basic user info
        print("\nFetching user info...")
        full_name = client.get_full_name()
        print(f"Full Name: {full_name}")
        
        print("\nFetching user stats...")
        today = date.today().strftime("%Y-%m-%d")
        stats = client.get_stats(today)
        print(f"User Stats for {today}:")
        display_json(stats)
        
        # Get device information
        print("\nFetching connected devices...")
        devices = client.get_devices()
        if devices:
            print("Your Garmin Devices:")
            for device in devices:
                print(f"\nDevice: {device.get('productDisplayName', 'Unknown')}")
                print(f"- Model: {device.get('model', 'N/A')}")
                print(f"- Firmware: {device.get('softwareVersion', 'N/A')}")
                print(f"- Last Sync: {device.get('lastSyncTime', 'N/A')}")
                print(f"- Features: {', '.join(device.get('features', []))}")
        
    except Exception as err:
        print(f"\nError occurred: {err}")
        print("\nTips:")
        print("1. Make sure your email and password are correct")
        print("2. If you use 2FA, you might need to generate an app password")
        print("3. Check your internet connection")
        return
    
    print("\nConnection test completed successfully!")

if __name__ == "__main__":
    main()
