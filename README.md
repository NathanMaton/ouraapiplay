# Oura Ring Data Monitor

This repository contains scripts to monitor various health metrics from your Oura ring using the Oura API v2, with a primary focus on real-time heart rate monitoring and alerts.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables in `.env`:
```
OURA_API_KEY=your_api_key_here
EMAIL_ADDRESS=your_gmail_address
EMAIL_APP_PASSWORD=your_app_specific_password
```

3. For email notifications:
   - Enable 2-factor authentication in your Google Account
   - Generate an App Password for the script

## Primary Script: Heart Rate Monitor

### Running the Heart Rate Monitor
```bash
python oura_heart_rate.py
```

### Features
- Real-time heart rate monitoring every 5 minutes
- Email alerts for significant changes (≥10 BPM within 5 minutes)
- Statistical analysis including:
  - Current heart rate and status
  - Average, maximum, and minimum heart rates
  - Detailed alerts for rapid changes

## Other Available Scripts

### 1. Old HRV Monitor (`old_oura_hrv.py`)

This script monitors your daily readiness score and its components.

#### Metrics Explained:
- **Readiness Score**: Overall daily score (0-100)
  - Higher scores indicate better recovery and readiness for activity
- **HRV Balance**: Heart Rate Variability score (0-100)
  - Measures the variation in time between heartbeats
  - Higher scores indicate better recovery and lower stress
- **Previous Night**: Sleep quality score (0-100)
  - Based on your previous night's sleep metrics
- **Activity Balance**: Activity level score (0-100)
  - Based on your recent activity levels and recovery needs
- **Temperature Deviation**: Body temperature variation from baseline
  - Measured in degrees Celsius
  - Large deviations might indicate stress or illness

### 2. Stress Monitor (`stress_monitor.py`)

This script provides a more comprehensive stress analysis using multiple metrics from Oura Ring.

#### Stress Level Calculation:

The script calculates stress levels based on four key indicators:

1. **Readiness Score**
   - Threshold: < 70 indicates stress
   - Weight: 1 stress point

2. **HRV Balance**
   - Threshold: < 70 indicates stress
   - Weight: 1 stress point
   - Lower HRV often correlates with higher stress

3. **Recovery Index**
   - Threshold: < 70 indicates stress
   - Weight: 1 stress point
   - Measures how well your body has recovered

4. **Temperature Deviation**
   - Threshold: > 0.5°C (absolute value) indicates stress
   - Weight: 1 stress point
   - Significant deviations can indicate stress or illness

#### Stress Level Categories:
- **HIGH**: 3+ stress indicators
- **MODERATE**: 2 stress indicators
- **MILD**: 1 stress indicator
- **LOW**: 0 stress indicators

#### Update Frequency:
- Checks metrics every 5 minutes
- Provides actionable suggestions for MODERATE and HIGH stress levels

## API Endpoints Used

- `/v2/usercollection/daily_readiness`: Daily readiness and recovery metrics
- `/v2/usercollection/personal_info`: User's personal information

## Notes

- The Oura API v2 doesn't provide real-time heart rate or stress data
- Metrics are updated once per day, typically after waking up
- Temperature deviations are relative to your personal baseline
- All scores (0-100) follow the principle that higher numbers are better

## Error Handling

Both scripts include error handling for:
- API connection issues
- Missing or incomplete data
- Invalid API responses

If you encounter persistent errors, verify your:
- Internet connection
- API token validity
- Oura ring sync status
