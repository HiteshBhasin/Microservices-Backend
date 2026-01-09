from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import sys
import os

# Add the parent directory to the path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.google_analytics import (
    get_active_users,
    get_analytics_by_country,
    get_analytics_by_country_nestHost,
    get_analytics_by_country_firstClass,
    get_total_summary,
    user_engagement_by_month,
    user_by_month,
    user_engagement_by_month_sessions
)

router = APIRouter(prefix="/google", tags=["Google Analytics"])


@router.get("/analytics/summary")
async def get_summary():
    """
    Get overall summary of Google Analytics metrics for the last 60 days.
    
    Returns:
        dict: Summary including active users, new users, engaged sessions, 
              engagement rate, event count, conversions, and total revenue
    """
    try:
        summary = get_total_summary()
        if not summary:
            raise HTTPException(status_code=404, detail="No summary data available")
        return {
            "status": "success",
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/daily")
async def get_daily_analytics(limit: Optional[int] = Query(None, ge=1, le=365, description="Limit number of days returned")):
    """
    Get daily Google Analytics data for the last 60 days.
    
    Args:
        limit: Optional limit on number of days to return (most recent)
    
    Returns:
        list: Daily metrics including active users, new users, engaged sessions,
              engagement rate, event count, conversions, and revenue
    """
    try:
        data = get_active_users()
        if limit:
            data = data[-limit:]
        return {
            "status": "success",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/by-country")
async def get_country_analytics():
    """
    Get Google Analytics data grouped by country (top 10).
    
    Returns:
        list: Top 10 countries with metrics including active users, new users,
              engaged sessions, engagement rate, and event count
    """
    try:
        data = get_analytics_by_country()
        return {
            "status": "success",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/by-country/nest-host")
async def get_country_nest_host_analytics():
    """
    Get Google Analytics data grouped by country with nest/host information.
    
    Returns:
        list: Countries with detailed nest/host metrics
    """
    try:
        data = get_analytics_by_country_nestHost()
        return {
            "status": "success",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/by-country/first-class")
async def get_country_first_class_analytics():
    """
    Get Google Analytics data grouped by country with first-class information.
    
    Returns:
        list: Countries with first-class user metrics
    """
    try:
        data = get_analytics_by_country_firstClass()
        return {
            "status": "success",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/monthly/active-users")
async def get_monthly_active_users():
    """
    Get Monthly Active Users (MAU) data.
    
    Returns:
        list: Monthly data showing year-month and active user counts
    """
    try:
        data = user_by_month()
        return {
            "status": "success",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/monthly/engagement")
async def get_monthly_engagement():
    """
    Get monthly engagement metrics including engaged sessions and engagement rate.
    
    Returns:
        list: Monthly data with engaged sessions, engagement rate, and new users
    """
    try:
        data = user_engagement_by_month()
        return {
            "status": "success",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/monthly/sessions")
async def get_monthly_sessions():
    """
    Get monthly session engagement data.
    
    Returns:
        list: Monthly session metrics
    """
    try:
        data = user_engagement_by_month_sessions()
        return {
            "status": "success",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/health")
async def health_check():
    """
    Health check endpoint for Google Analytics service.
    
    Returns:
        dict: Service status
    """
    return {
        "status": "success",
        "service": "Google Analytics",
        "message": "Service is running"
    }
