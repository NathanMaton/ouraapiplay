import requests
import time
from datetime import datetime, timedelta

API_KEY = "GCB6HLCP5FTDPDK3HGFKDAUNUHAKPD4V"
READINESS_URL = "https://api.ouraring.com/v2/usercollection/daily_readiness"

def get_readiness_metrics():
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # Get today's data
    today = datetime.now().date()
    params = {
        "start_date": today.isoformat(),
        "end_date": today.isoformat()
    }
    
    try:
        response = requests.get(READINESS_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def analyze_wellness(data):
    if not data or "data" not in data or not data["data"]:
        return None

    # Get today's metrics
    metrics = data["data"][0]
    contributors = metrics.get("contributors", {})
    
    return {
        "readiness_score": metrics.get("score"),
        "hrv_balance": contributors.get("hrv_balance"),
        "recovery_index": contributors.get("recovery_index"),
        "resting_hr": contributors.get("resting_heart_rate"),
        "temperature": metrics.get("temperature_deviation")
    }

def assess_stress_level(metrics):
    if not metrics:
        return "UNKNOWN"
    
    stress_indicators = 0
    reasons = []
    
    if metrics["readiness_score"] and metrics["readiness_score"] < 70:
        stress_indicators += 1
        reasons.append("Low readiness score")
    
    if metrics["hrv_balance"] and metrics["hrv_balance"] < 70:
        stress_indicators += 1
        reasons.append("Low HRV balance")
    
    if metrics["recovery_index"] and metrics["recovery_index"] < 70:
        stress_indicators += 1
        reasons.append("Low recovery index")
    
    if metrics["temperature"] and abs(metrics["temperature"]) > 0.5:
        stress_indicators += 1
        reasons.append("Temperature deviation")
    
    if stress_indicators >= 3:
        return "HIGH", reasons
    elif stress_indicators >= 2:
        return "MODERATE", reasons
    elif stress_indicators >= 1:
        return "MILD", reasons
    else:
        return "LOW", ["All metrics look good"]

def display_metrics(metrics):
    if not metrics:
        print("No data available for today")
        return

    print("\n=== Current Wellness Metrics ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Readiness Score: {metrics['readiness_score']}")
    print(f"HRV Balance: {metrics['hrv_balance']}")
    print(f"Recovery Index: {metrics['recovery_index']}")
    print(f"Resting Heart Rate Score: {metrics['resting_hr']}")
    print(f"Temperature Deviation: {metrics['temperature']}°C")
    
    stress_level, reasons = assess_stress_level(metrics)
    print(f"\nStress Level: {stress_level}")
    print("Reasons:")
    for reason in reasons:
        print(f"- {reason}")
    
    if stress_level in ["MODERATE", "HIGH"]:
        print("\n⚠️ Suggested actions:")
        print("- Take deep breaths")
        print("- Go for a walk")
        print("- Take a break from work")
        print("- Consider meditation")
        print("- Ensure you're staying hydrated")

def main():
    print("Starting Oura wellness monitoring...")
    print("Checking metrics every 5 minutes...")
    
    while True:
        data = get_readiness_metrics()
        metrics = analyze_wellness(data)
        display_metrics(metrics)
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    main()
