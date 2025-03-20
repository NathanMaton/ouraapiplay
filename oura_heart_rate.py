import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from time import sleep
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class OuraHeartRate:
    def __init__(self, api_key, email_address=None, email_password=None):
        self.api_key = api_key
        self.base_url = "https://api.ouraring.com/v2/usercollection"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Email setup
        self.email_address = email_address
        self.email_password = email_password
    
    def send_email(self, subject, message):
        """Send email using Gmail SMTP"""
        if not all([self.email_address, self.email_password]):
            print("Email credentials not configured properly")
            return
        
        print(f"\nAttempting to send email...")
        print(f"From: {self.email_address}")
        print(f"Subject: {subject}")
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = self.email_address
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            print("Connecting to Gmail SMTP server...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            
            print("Attempting login...")
            server.login(self.email_address, self.email_password)
            
            print("Sending email...")
            server.send_message(msg)
            server.quit()
            print("Email sent successfully!")
            
        except Exception as e:
            print(f"Error sending email: {e}")
    
    def check_sync_status(self, data):
        """Check if the Oura ring has synced recently using the provided data"""
        if data and 'data' in data and data['data']:
            latest = max(data['data'], key=lambda x: x['timestamp'])
            latest_time = datetime.fromisoformat(latest['timestamp'].replace('Z', '+00:00'))
            time_since_sync = datetime.now().astimezone() - latest_time
            minutes_since_sync = time_since_sync.total_seconds() / 60
            
            if minutes_since_sync > 30:  # If no data in last 30 minutes
                print(f"\n⚠️ Warning: Last sync was {minutes_since_sync:.1f} minutes ago")
                print("Please sync your Oura ring with the Oura app if this persists.")
                return False
            return True
        return False

    def get_heart_rate(self, start_datetime, end_datetime):
        """Get heart rate data for a specific time range"""
        endpoint = f"{self.base_url}/heartrate"
        
        # Ensure we're not requesting future data
        now = datetime.now().astimezone()
        if end_datetime > now:
            end_datetime = now
            start_datetime = end_datetime - timedelta(hours=1)
        
        # Format times in UTC
        params = {
            "start_datetime": start_datetime.astimezone().isoformat(),
            "end_datetime": end_datetime.astimezone().isoformat()
        }
        
        print(f"\nDebug - API Request:")
        print(f"Endpoint: {endpoint}")
        print(f"Start: {params['start_datetime']}")
        print(f"End: {params['end_datetime']}")
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

def format_timestamp(timestamp):
    """Convert timestamp to local time string"""
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    return dt.astimezone().strftime('%Y-%m-%d %H:%M:%S')

def analyze_heart_rate(data):
    """Analyze heart rate data and return insights"""
    if not data or 'data' not in data:
        return None
    
    readings = data['data']
    if not readings:
        return None
    
    # Calculate statistics
    hr_values = [reading['bpm'] for reading in readings]
    avg_hr = sum(hr_values) / len(hr_values)
    max_hr = max(hr_values)
    min_hr = min(hr_values)
    
    # Look for significant changes
    significant_changes = []
    for i in range(1, len(readings)):
        change = abs(readings[i]['bpm'] - readings[i-1]['bpm'])
        if change >= 10:  # Consider changes of 10+ BPM significant
            significant_changes.append({
                'time': readings[i]['timestamp'],
                'from': readings[i-1]['bpm'],
                'to': readings[i]['bpm'],
                'change': change
            })
    
    return {
        'average': avg_hr,
        'maximum': max_hr,
        'minimum': min_hr,
        'significant_changes': significant_changes
    }

def monitor_heart_rate(interval_minutes=5):
    """Monitor heart rate data continuously"""
    print("Starting Oura Heart Rate Monitor")
    print("-------------------------------")
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OURA_API_KEY')
    email_address = os.getenv('EMAIL_ADDRESS')
    email_password = os.getenv('EMAIL_APP_PASSWORD')
    
    if not api_key:
        print("Error: Oura API key not found in .env file")
        print("Please set OURA_API_KEY in your .env file")
        return
    
    # Initialize Oura client with email credentials
    oura = OuraHeartRate(api_key, email_address, email_password)
    
    try:
        while True:
            now = datetime.now().astimezone()
            
            # Get data for the last hour
            start_time = now - timedelta(hours=1)
            end_time = now
            
            print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}]")
            print("Fetching heart rate data for the last hour...")
            
            data = oura.get_heart_rate(start_time, end_time)
            if data and 'data' in data and data['data']:
                # Check sync status using the actual data
                oura.check_sync_status(data)
                # Display recent readings
                print("\nRecent Heart Rate Readings:")
                recent_readings = sorted(data['data'][-10:], key=lambda x: x['timestamp'], reverse=True)
                
                # Show analysis first
                analysis = analyze_heart_rate(data)
                
                if recent_readings:
                    latest_hr = recent_readings[0]['bpm']
                    print("\nCurrent Status:")
                    print(f"Latest HR: {latest_hr} bpm")
                    
                    # Determine status
                    status = "NORMAL"
                    if latest_hr > 100:
                        status = "ELEVATED"
                    elif latest_hr < 60:
                        status = "LOW"
                    
                    print(f"Status: {status} heart rate range")
                    
                    if analysis:
                        # Check for recent significant changes (last 5 minutes)
                        recent_changes = []
                        now = datetime.now().astimezone()  # Get current time with timezone
                        for change in analysis['significant_changes']:
                            # Convert UTC timestamp to local time with timezone
                            change_time = datetime.fromisoformat(change['time'].replace('Z', '+00:00')).astimezone()
                            if (now - change_time).total_seconds() <= 300:  # 5 minutes = 300 seconds
                                recent_changes.append(change)
                        
                        # Only send email if there are recent significant changes
                        if recent_changes:
                            # Prepare email subject with alert
                            subject = f"⚠️ Rapid HR Change - {status} ({latest_hr} bpm)"
                            
                            # Prepare email message
                            message = f"Alert: Significant heart rate change detected!\n\nCurrent: {latest_hr} bpm\nStatus: {status}\nAvg: {analysis['average']:.1f} bpm\nMax: {analysis['maximum']} bpm\nMin: {analysis['minimum']} bpm"
                            
                            # Add the recent changes
                            message += "\n\n⚠️ RECENT SIGNIFICANT CHANGES (Last 5 min):"
                            for change in recent_changes:
                                time = format_timestamp(change['time'])
                                message += f"\n{time}: {change['from']} → {change['to']} bpm (Δ{change['change']:.1f})"
                            
                            message += f"\n\nTime: {datetime.now().strftime('%H:%M:%S')}"
                            oura.send_email(subject, message)
                            print("\nAlert email sent - Significant HR change detected!")
                
                print("\nLast 10 readings:")
                for reading in recent_readings:
                    timestamp = format_timestamp(reading['timestamp'])
                    print(f"Time: {timestamp}, HR: {reading['bpm']} bpm")
                
                # Show analysis results
                if analysis:
                    print(f"\nHeart Rate Analysis:")
                    print(f"Average HR: {analysis['average']:.1f} bpm")
                    print(f"Maximum HR: {analysis['maximum']} bpm")
                    print(f"Minimum HR: {analysis['minimum']} bpm")
                    
                    if analysis['significant_changes']:
                        print("\nSignificant Changes (10+ bpm):")
                        for change in analysis['significant_changes'][-3:]:  # Show last 3 significant changes
                            time = format_timestamp(change['time'])
                            print(f"Time: {time}, {change['from']} → {change['to']} bpm (Δ{change['change']:.1f})")
            else:
                print("No heart rate data available for this period")
            
            # Calculate time until next update
            next_update = now + timedelta(minutes=interval_minutes)
            print(f"\nNext update at: {next_update.strftime('%H:%M:%S')}")
            
            try:
                sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                return
            except Exception as e:
                print(f"\nError during sleep: {e}")
                print("Falling back to 5-minute interval")
                sleep(300)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as err:
        print(f"\nError occurred: {err}")

if __name__ == "__main__":
    monitor_heart_rate()
