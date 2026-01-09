import os
from fastapi import APIRouter, HTTPException, Query
from dotenv import load_dotenv
from services.monday_api_client import get_information, query
from services.monday_qualified_leads import (
    get_top_mobility_leads,
    get_ibam_contacts_leads,
    get_first_priority_leads,
    get_prospects_leads,
    get_for_review_leads,
    get_all_qualified_leads
)

load_dotenv()

router = APIRouter(prefix="/monday", tags=["Monday.com"])


@router.get("/qualified-leads")
async def get_qualified_leads_all(limit: int = Query(default=500, ge=1, le=1000)):
    """
    Fetch all items from the Qualified Leads board (all groups)
    Board ID: 3496733949
    """
    try:
        result = get_all_qualified_leads(limit=limit)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch data from Monday.com API"
            )
        
        if "errors" in result:
            raise HTTPException(
                status_code=400,
                detail=f"Monday.com API error: {result['errors']}"
            )
        
        boards = result.get("boards", [])
        if not boards:
            raise HTTPException(status_code=404, detail="Board not found")
        
        board = boards[0]
        items = board.get("items_page", {}).get("items", [])
        
        return {
            "success": True,
            "board_id": board.get("id"),
            "board_name": board.get("name"),
            "total_items": len(items),
            "groups": board.get("groups", []),
            "items": items
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/qualified-leads/top-mobility")
async def get_top_mobility(limit: int = Query(default=100, ge=1, le=500)):
    """
    Fetch leads from the "Top Mobility" group
    Group ID: 1684948804_apollo_contacts_exp
    """
    try:
        result = get_top_mobility_leads(limit=limit)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch Top Mobility leads"
            )
        
        return {
            "success": True,
            "category": "Top Mobility",
            **result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/qualified-leads/ibam-contacts")
async def get_ibam_contacts(limit: int = Query(default=100, ge=1, le=500)):
    """
    Fetch leads from the "IBAM Contacts" group
    Group ID: new_group21337
    """
    try:
        result = get_ibam_contacts_leads(limit=limit)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch IBAM Contacts leads"
            )
        
        return {
            "success": True,
            "category": "IBAM Contacts",
            **result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/qualified-leads/first-priority")
async def get_first_priority(limit: int = Query(default=100, ge=1, le=500)):
    """
    Fetch leads from the "First Priority (For Discover)" group
    Group ID: new_group7744
    """
    try:
        result = get_first_priority_leads(limit=limit)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch First Priority leads"
            )
        
        return {
            "success": True,
            "category": "First Priority (For Discover)",
            **result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/qualified-leads/prospects")
async def get_prospects(limit: int = Query(default=100, ge=1, le=500)):
    """
    Fetch leads from the "Prospects" group
    Group ID: 1667950578_book3
    """
    try:
        result = get_prospects_leads(limit=limit)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch Prospects leads"
            )
        
        return {
            "success": True,
            "category": "Prospects",
            **result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/qualified-leads/for-review")
async def get_for_review(limit: int = Query(default=100, ge=1, le=500)):
    """
    Fetch leads from the "For Review" group
    Group ID: 1668584639_lead_import_nov_16
    """
    try:
        result = get_for_review_leads(limit=limit)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch For Review leads"
            )
        
        return {
            "success": True,
            "category": "For Review",
            **result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/qualified-leads/summary")
async def get_qualified_leads_summary():
    """
    Get a summary of all groups in the Qualified Leads board
    """
    try:
        result = get_all_qualified_leads(limit=500)
        
        if not result or "boards" not in result:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch qualified leads summary"
            )
        
        boards = result.get("boards", [])
        if not boards:
            raise HTTPException(status_code=404, detail="Board not found")
        
        board = boards[0]
        items = board.get("items_page", {}).get("items", [])
        
        # Group items by category
        groups_summary = {}
        for item in items:
            group = item.get("group", {})
            group_id = group.get("id")
            group_title = group.get("title")
            
            if group_id not in groups_summary:
                groups_summary[group_id] = {
                    "group_id": group_id,
                    "group_title": group_title,
                    "count": 0,
                    "sample_items": []
                }
            
            groups_summary[group_id]["count"] += 1
            if len(groups_summary[group_id]["sample_items"]) < 3:
                groups_summary[group_id]["sample_items"].append({
                    "id": item.get("id"),
                    "name": item.get("name")
                })
        
        return {
            "success": True,
            "board_id": board.get("id"),
            "board_name": board.get("name"),
            "total_items": len(items),
            "groups": list(groups_summary.values())
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

