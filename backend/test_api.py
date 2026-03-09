import requests

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("Testing API...")
    
    # 1. Register
    print("\n1. Registering User...")
    user_data = {"phone": "13800138000", "password": "password123", "nickname": "TestUser"}
    try:
        r = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"Register Status: {r.status_code}")
        print(r.json())
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # 2. Login
    print("\n2. Logging in...")
    login_data = {"phone": "13800138000", "password": "password123", "nickname": "TestUser"}
    r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login Status: {r.status_code}")
    token = r.json().get("access_token")
    print(f"Token: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Capsule
    print("\n3. Creating Capsule...")
    capsule_data = {
        "title": "My First Memory",
        "description": "This is a test memory",
        "latitude": 39.9042,
        "longitude": 116.4074, # Beijing
        "is_public": True,
        "tags": "Test,Beijing",
        "media_items": []
    }
    r = requests.post(f"{BASE_URL}/capsules/create", json=capsule_data, headers=headers)
    print(f"Create Capsule Status: {r.status_code}")
    print(r.json())

    # 4. Get Nearby
    print("\n4. Get Nearby Capsules...")
    r = requests.get(f"{BASE_URL}/capsules/nearby?lat=39.90&lon=116.40", headers=headers)
    print(f"Nearby Status: {r.status_code}")
    print(f"Found: {len(r.json())} capsules")

if __name__ == "__main__":
    test_api()
