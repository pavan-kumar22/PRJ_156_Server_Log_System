import requests
from datetime import datetime


SERVICES = {
    "Classifier": "http://localhost:8000/health",
    "Notification": "http://localhost:8001/health",
    "OpenSearch": "http://localhost:9200",
}


def check_service(name, url):
    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            return True, response.text

        return False, f"HTTP {response.status_code}"

    except requests.RequestException as error:
        return False, str(error)


def main():
    print("=" * 70)
    print("AICTE SERVER LOG MONITORING PLATFORM")
    print("DAY 27 - SYSTEM HEALTH CHECK")
    print("=" * 70)

    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    healthy = 0

    for name, url in SERVICES.items():
        status, details = check_service(name, url)

        if status:
            print(f"[PASS] {name}")
            healthy += 1
        else:
            print(f"[FAIL] {name}")
            print(f"       {details}")

    print()
    print("-" * 70)
    print(f"Healthy Services: {healthy}/{len(SERVICES)}")

    if healthy == len(SERVICES):
        print("OVERALL STATUS: HEALTHY")
        print("-" * 70)
        return 0

    print("OVERALL STATUS: DEGRADED")
    print("-" * 70)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())