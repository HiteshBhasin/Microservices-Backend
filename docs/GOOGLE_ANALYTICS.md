# Google Analytics Integration

This integration provides FastAPI routes and an MCP server for accessing Google Analytics 4 (GA4) data.

## Features

### FastAPI Routes

All routes are prefixed with `/api/google` and provide comprehensive Google Analytics data.

#### Available Endpoints

1. **GET `/api/google/analytics/summary`**
   - Get overall summary of GA4 metrics (last 60 days)
   - Returns: Active users, new users, engaged sessions, engagement rate, event count, conversions, revenue

2. **GET `/api/google/analytics/daily`**
   - Get daily breakdown of all metrics
   - Query params: `limit` (optional, 1-365) - limit number of most recent days
   - Returns: Date-wise data for last 60 days

3. **GET `/api/google/analytics/by-country`**
   - Get top 10 countries by active users
   - Returns: Country-wise metrics

4. **GET `/api/google/analytics/by-country/nest-host`**
   - Get analytics by country with nest/host information
   - Returns: Detailed country metrics with hosting data

5. **GET `/api/google/analytics/by-country/first-class`**
   - Get analytics by country with first-class user metrics
   - Returns: Premium user segment data by country

6. **GET `/api/google/analytics/monthly/active-users`**
   - Get Monthly Active Users (MAU)
   - Returns: Year-month data with active user counts

7. **GET `/api/google/analytics/monthly/engagement`**
   - Get monthly engagement metrics
   - Returns: Engaged sessions, engagement rate, new users by month

8. **GET `/api/google/analytics/monthly/sessions`**
   - Get monthly session data
   - Returns: Session engagement metrics by month

9. **GET `/api/google/analytics/health`**
   - Health check endpoint
   - Returns: Service status

### MCP Server

The Model Context Protocol (MCP) server provides programmatic access to Google Analytics data.

#### Available MCP Tools

1. `get_analytics_summary` - Get overall metrics summary
2. `get_daily_analytics` - Get daily breakdown (with optional limit parameter)
3. `get_analytics_by_country` - Top 10 countries
4. `get_analytics_by_country_nest_host` - Country data with nest/host info
5. `get_analytics_by_country_first_class` - Country data with first-class metrics
6. `get_monthly_active_users` - MAU data
7. `get_monthly_engagement` - Monthly engagement metrics
8. `get_monthly_sessions` - Monthly session data

## Setup

### Prerequisites

1. **Google Analytics 4 Property**
   - GA4 Property ID
   - Service account with Analytics Reporting API access

2. **Service Account Credentials**
   - JSON credentials file from Google Cloud Console
   - Place at: `cogent-transit-483116-i8-e43751688229.json` (root directory)

3. **Environment Variables**
   ```bash
   GA4_PROPERTY_ID=your_property_id
   ```

### Installation

1. Install required packages:
   ```bash
   pip install google-analytics-data google-auth fastapi
   ```

2. Configure credentials:
   - Download service account JSON from Google Cloud Console
   - Place in project root
   - Update `.env` with GA4_PROPERTY_ID

## Usage

### FastAPI Routes

Start the server:
```bash
uvicorn app.main:app --reload
```

Example requests:
```bash
# Get summary
curl http://localhost:8000/api/google/analytics/summary

# Get last 10 days of data
curl http://localhost:8000/api/google/analytics/daily?limit=10

# Get country analytics
curl http://localhost:8000/api/google/analytics/by-country

# Get monthly active users
curl http://localhost:8000/api/google/analytics/monthly/active-users
```

### MCP Server

Run the MCP server:
```bash
python mcp_server/google_analytics_mcp_server.py
```

The server communicates via stdio (standard input/output) using the Model Context Protocol.

## Response Format

All FastAPI endpoints return JSON in this format:
```json
{
  "status": "success",
  "count": 10,
  "data": [...]
}
```

Error responses:
```json
{
  "detail": "Error message"
}
```

## Metrics Explained

- **Active Users**: Users who engaged with your app/site
- **New Users**: First-time users
- **Engaged Sessions**: Sessions lasting 10+ seconds with conversion or 2+ page views
- **Engagement Rate**: Percentage of engaged sessions
- **User Engagement Duration**: Total time users spent engaged
- **Average Session Duration**: Average time per session
- **Event Count**: Total number of events triggered
- **Conversions**: Key events/conversions
- **Total Revenue**: Revenue generated (if e-commerce tracking enabled)

## Testing

Test the service functions directly:
```bash
python services/google_analytics.py
```

This will output:
- Total metrics summary
- Top 10 countries
- Last 10 days of daily trends
- Monthly active users
- Monthly engagement data

## Integration with Main Application

The routes are automatically registered in `app/main.py`:
```python
from routes.google import router as google_router
app.include_router(google_router, prefix="/api/google", tags=["google-analytics"])
```

## Troubleshooting

1. **Authentication Errors**
   - Verify service account JSON file path
   - Check GA4_PROPERTY_ID in .env
   - Ensure service account has Analytics Reporting API access

2. **Invalid Metrics**
   - GA4 uses different metric names than Universal Analytics
   - Check [GA4 API Schema](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema)

3. **No Data Returned**
   - Verify property ID is correct
   - Check date ranges (default is last 60 days)
   - Ensure GA4 property has data

## API Documentation

Once the server is running, view interactive API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
