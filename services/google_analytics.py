from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
load_dotenv()

property_id = os.getenv("GA4_PROPERTY_ID")

credentials = service_account.Credentials.from_service_account_file(
    "cogent-transit-483116-i8-e43751688229.json"
)

def get_active_users():
    client = BetaAnalyticsDataClient(credentials=credentials)

    request = {
        "property": f"properties/{property_id}",
        "dimensions": [{"name": "date"}],
        "metrics": [{"name": "totalUsers"}],
        "date_ranges": [{"start_date": "60daysAgo", "end_date": "today"}],
    }

    response = client.run_report(request)
    active_users_data = []

    for row in response.rows:
        date = row.dimension_values[0].value
        totalUsers = row.metric_values[0].value
        active_users_data.append({"date": date, "totalUsers": totalUsers})

    return active_users_data
if __name__ == "__main__":
    data = get_active_users()
    for entry in data:
        print(f"Date: {entry['date']}, Active Users: {entry['totalUsers']}")