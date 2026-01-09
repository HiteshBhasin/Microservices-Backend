from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
from google.analytics.data_v1beta import Metric


from google.oauth2 import service_account
import os
from dotenv import load_dotenv
load_dotenv()

property_id = os.getenv("GA4_PROPERTY_ID")

credentials = service_account.Credentials.from_service_account_file(
    "cogent-transit-483116-i8-e43751688229.json"
)

def get_active_users():
    """Get comprehensive Google Analytics data including all key metrics"""
    client = BetaAnalyticsDataClient(credentials=credentials)

    request = {
        "property": f"properties/{property_id}",
        "dimensions": [{"name": "date"}],
        "metrics": [
            {"name": "activeUsers"},
            {"name": "newUsers"},
            {"name": "engagedSessions"},
            {"name": "engagementRate"},
            {"name": "userEngagementDuration"},
            {"name": "averageSessionDuration"},
            {"name": "eventCount"},
            {"name": "conversions"},
            {"name": "totalRevenue"}
        ],
        "date_ranges": [{"start_date": "60daysAgo", "end_date": "today"}],
        "order_bys": [{
            "dimension": {"dimension_name": "date"}, 
            "desc": False
        }],
    }

    response = client.run_report(request)
   
    analytics_data = []

    for row in response.rows:
        date = row.dimension_values[0].value
        data_entry = {
            "date": date,
            "activeUsers": row.metric_values[0].value,
            "newUsers": row.metric_values[1].value,
            "engagedSessions": row.metric_values[2].value,
            "engagementRate": f"{float(row.metric_values[3].value) * 100:.2f}%",
            "userEngagementDuration": row.metric_values[4].value,
            "averageSessionDuration": row.metric_values[5].value,
            "eventCount": row.metric_values[6].value,
            "conversions": row.metric_values[7].value,
            "totalRevenue": f"${row.metric_values[8].value}"
        }
        analytics_data.append(data_entry)

    return analytics_data


def get_analytics_by_country():
    """Get Google Analytics data grouped by country"""
    client = BetaAnalyticsDataClient(credentials=credentials)

    request = {
        "property": f"properties/{property_id}",
        "dimensions": [{"name": "country"}],
        "metrics": [
            {"name": "activeUsers"},
            {"name": "newUsers"},
            {"name": "engagedSessions"},
            {"name": "engagementRate"},
            {"name": "userEngagementDuration"},
            {"name": "averageSessionDuration"},
            {"name": "eventCount"},
            {"name": "conversions"},
            {"name": "totalRevenue"}
        ],
        "date_ranges": [{"start_date": "60daysAgo", "end_date": "today"}],
        "order_bys": [{
            "metric": {"metric_name": "activeUsers"}, 
            "desc": True
        }],
        "limit": 10
    }

    response = client.run_report(request)
   
    country_data = []

    for row in response.rows:
        country = row.dimension_values[0].value
        data_entry = {
            "country": country,
            "activeUsers": row.metric_values[0].value,
            "newUsers": row.metric_values[1].value,
            "engagedSessions": row.metric_values[2].value,
            "engagementRate": f"{float(row.metric_values[3].value) * 100:.2f}%",
            "userEngagementDuration": row.metric_values[4].value,
            "averageSessionDuration": row.metric_values[5].value,
            "eventCount": row.metric_values[6].value,
            "conversions": row.metric_values[7].value,
            "totalRevenue": f"${row.metric_values[8].value}"
        }
        country_data.append(data_entry)

    return country_data
# nest host property id required. 
def get_analytics_by_country_nestHost():
    """Get Google Analytics data grouped by country"""
    client = BetaAnalyticsDataClient(credentials=credentials)

    request = {
        "property": f"properties/#nesthostpropertyid{property_id}",
        "dimensions": [{"name": "country"}],
        "metrics": [
            {"name": "activeUsers"},
            {"name": "newUsers"},
            {"name": "engagedSessions"},
            {"name": "engagementRate"},
            {"name": "userEngagementDuration"},
            {"name": "averageSessionDuration"},
            {"name": "eventCount"},
            {"name": "conversions"},
            {"name": "totalRevenue"}
        ],
        "date_ranges": [{"start_date": "60daysAgo", "end_date": "today"}],
        "order_bys": [{
            "metric": {"metric_name": "activeUsers"}, 
            "desc": True
        }],
        "limit": 10
    }

    response = client.run_report(request)
   
    country_data = []

    for row in response.rows:
        country = row.dimension_values[0].value
        data_entry = {
            "country": country,
            "activeUsers": row.metric_values[0].value,
            "newUsers": row.metric_values[1].value,
            "engagedSessions": row.metric_values[2].value,
            "engagementRate": f"{float(row.metric_values[3].value) * 100:.2f}%",
            "userEngagementDuration": row.metric_values[4].value,
            "averageSessionDuration": row.metric_values[5].value,
            "eventCount": row.metric_values[6].value,
            "conversions": row.metric_values[7].value,
            "totalRevenue": f"${row.metric_values[8].value}"
        }
        country_data.append(data_entry)

    return country_data

def get_analytics_by_country_firstClass():
    """Get Google Analytics data grouped by country"""
    client = BetaAnalyticsDataClient(credentials=credentials)

    request = {
        "property": f"properties/# firstclass propery id required{property_id}",
        "dimensions": [{"name": "country"}],
        "metrics": [
            {"name": "activeUsers"},
            {"name": "newUsers"},
            {"name": "engagedSessions"},
            {"name": "engagementRate"},
            {"name": "userEngagementDuration"},
            {"name": "averageSessionDuration"},
            {"name": "eventCount"},
            {"name": "conversions"},
            {"name": "totalRevenue"}
        ],
        "date_ranges": [{"start_date": "60daysAgo", "end_date": "today"}],
        "order_bys": [{
            "metric": {"metric_name": "activeUsers"}, 
            "desc": True
        }],
        "limit": 10
    }

    response = client.run_report(request)
   
    country_data = []

    for row in response.rows:
        country = row.dimension_values[0].value
        data_entry = {
            "country": country,
            "activeUsers": row.metric_values[0].value,
            "newUsers": row.metric_values[1].value,
            "engagedSessions": row.metric_values[2].value,
            "engagementRate": f"{float(row.metric_values[3].value) * 100:.2f}%",
            "userEngagementDuration": row.metric_values[4].value,
            "averageSessionDuration": row.metric_values[5].value,
            "eventCount": row.metric_values[6].value,
            "conversions": row.metric_values[7].value,
            "totalRevenue": f"${row.metric_values[8].value}"
        }
        country_data.append(data_entry)

    return country_data

def get_total_summary():
    """Get total summary statistics for the time period"""
    client = BetaAnalyticsDataClient(credentials=credentials)

    request = {
        "property": f"properties/{property_id}",
        "metrics": [
            {"name": "activeUsers"},
            {"name": "newUsers"},
            {"name": "engagedSessions"},
            {"name": "engagementRate"},
            {"name": "userEngagementDuration"},
            {"name": "averageSessionDuration"},
            {"name": "eventCount"},
            {"name": "conversions"},
            {"name": "totalRevenue"}
        ],
        "date_ranges": [{"start_date": "60daysAgo", "end_date": "today"}]
    }

    response = client.run_report(request)
   
    if response.rows:
        row = response.rows[0]
        summary = {
            "activeUsers": row.metric_values[0].value,
            "newUsers": row.metric_values[1].value,
            "engagedSessions": row.metric_values[2].value,
            "engagementRate": f"{float(row.metric_values[3].value) * 100:.2f}%",
            "userEngagementDuration": f"{int(float(row.metric_values[4].value))}s",
            "averageSessionDuration": f"{int(float(row.metric_values[5].value))}s",
            "eventCount": row.metric_values[6].value,
            "conversions": row.metric_values[7].value,
            "totalRevenue": f"${row.metric_values[8].value}"
        }
        return summary
    return None

def user_engagement_by_month():
    """Get Monthly Engaged Sessions data"""
    client = BetaAnalyticsDataClient(credentials=credentials)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            {"name": "yearMonth"}
        ],
        metrics=[
            {"name": "engagedSessions"},
            {"name": "engagementRate"},
            {"name": "newUsers"}
        ],
        date_ranges=[
            {"start_date": "2024-01-01", "end_date": "today"}
        ],
        order_bys=[
            {
                "dimension": {
                    "dimension_name": "yearMonth"
                }
            }
        ]
    )
    response = client.run_report(request=request)
    
    monthly_data = []
    for row in response.rows:
        year_month = row.dimension_values[0].value
        engaged_sessions = row.metric_values[0].value
        engagement_rate = row.metric_values[1].value
        new_users = row.metric_values[2].value
        data = {
            "yearMonth": year_month,
            "engagedSessions": engaged_sessions,
            "engagementRate": f"{float(engagement_rate) * 100:.2f}%",
            "newUsers": new_users
        }
        monthly_data.append(data)
    
    return monthly_data

    
def user_by_month():
    """Get Monthly Active Users (MAU) data"""
    client = BetaAnalyticsDataClient(credentials=credentials)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            {"name": "yearMonth"}  # ← monthly bucket
        ],
        metrics=[
            {"name": "activeUsers"}  # ← MAU
        ],
        date_ranges=[
            {"start_date": "2024-01-01", "end_date": "today"}
        ],
        order_bys=[
            {
                "dimension": {
                    "dimension_name": "yearMonth"
                }
            }
        ]
    )
    response = client.run_report(request=request)
    
    monthly_data = []
    for row in response.rows:
        year_month = row.dimension_values[0].value
        active_users = row.metric_values[0].value
        monthly_data.append({
            "yearMonth": year_month,
            "activeUsers": active_users
        })
    
    return monthly_data
def user_engagement_by_month_sessions():
    """Get monthly engaged sessions (monthly engagement only)"""
    client = BetaAnalyticsDataClient(credentials=credentials)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            {"name": "yearMonth"}  # ← monthly bucket
        ],
        metrics=[
            {"name": "engagedSessions"}  
        ],
        date_ranges=[
            {"start_date": "2024-01-01", "end_date": "today"}
        ],
        order_bys=[
            {
                "dimension": {
                    "dimension_name": "yearMonth"
                }
            }
        ]
    )
    response = client.run_report(request=request)
    
    monthly_data = []
    for row in response.rows:
        year_month = row.dimension_values[0].value
        engaged_sessions = row.metric_values[0].value
        monthly_data.append({
            "yearMonth": year_month,
            "engagedSessions": engaged_sessions
        })
    
    return monthly_data
    
    
if __name__ == "__main__":
    print("=" * 80)
    print("GOOGLE ANALYTICS SUMMARY (Last 60 Days)")
    print("=" * 80)
    
    # Get total summary
    summary = get_total_summary()
    if summary:
        print("\n📊 TOTAL METRICS:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("TOP 10 COUNTRIES")
    print("=" * 80)
    
    # Get data by country
    country_data = get_analytics_by_country()
    for i, entry in enumerate(country_data, 1):
        print(f"\n{i}. {entry['country']}")
        print(f"   Active Users: {entry['activeUsers']}")
        print(f"   New Users: {entry['newUsers']}")
        print(f"   Engaged Sessions: {entry['engagedSessions']}")
        print(f"   Engagement Rate: {entry['engagementRate']}")
        print(f"   Event Count: {entry['eventCount']}")
    
    print("\n" + "=" * 80)
    print("DAILY TRENDS (Last 10 Days)")
    print("=" * 80)
    
    # Get daily data
    daily_data = get_active_users()
    for entry in daily_data[-10:]:  # Show last 10 days
        print(f"\n📅 {entry['date']}")
        print(f"   Active Users: {entry['activeUsers']}, New Users: {entry['newUsers']}")
        print(f"   Engaged Sessions: {entry['engagedSessions']}, Engagement Rate: {entry['engagementRate']}")
        print(f"   Event Count: {entry['eventCount']}")
    
    print("\n" + "=" * 80)
    print("MONTHLY ACTIVE USERS (MAU)")
    print("=" * 80)
    
    # Get monthly data
    monthly_data = user_by_month()
    for entry in monthly_data:
        print(f"   {entry['yearMonth']}: {entry['activeUsers']} MAU")
    
    print("\n" + "=" * 80)
    print("MONTHLY ENGAGEMENT DATA")
    print("=" * 80)
    
    Enga_monthly_data = user_engagement_by_month()
    if Enga_monthly_data:
        for entry in Enga_monthly_data:
            print(f"   {entry['yearMonth']}: {entry['engagedSessions']} Engaged Sessions | {entry['engagementRate']} Engagement Rate | {entry['newUsers']} New Users")
    else:
        print("   No monthly engagement data available")