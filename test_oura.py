import requests

API_KEY = "GCB6HLCP5FTDPDK3HGFKDAUNUHAKPD4V"
BASE_URL = "https://api.ouraring.com/v2/usercollection/personal_info"

def get_personal_info():
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.get(BASE_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def main():
    print("Testing Oura API connection...")
    data = get_personal_info()
    if data:
        print("\nAPI Response:")
        print(data)

if __name__ == "__main__":
    main()
