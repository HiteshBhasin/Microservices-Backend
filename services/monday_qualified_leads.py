"""
Monday.com Qualified Leads Service
Provides access to the Qualified Leads board with categorized groups
"""

import os
from dotenv import load_dotenv
from services.monday_api_client import get_information

load_dotenv()

# Board ID for Qualified Leads
QUALIFIED_LEADS_BOARD_ID = "3496733949"

# Group IDs within the Qualified Leads board
GROUPS = {
    "top_mobility": "topics",
    "ibam_contacts": "new_group21337",
    "first_priority": "new_group50588",
    "prospects": "new_group",
    "for_review": "group_title"
}


def get_board_items_by_group(group_id: str, limit: int = 100):
    """
    Get items from the Qualified Leads board filtered by group.
    
    Args:
        group_id: The group ID to filter by
        limit: Maximum number of items to return (1-500)
    
    Returns:
        dict: Response containing items from the specified group
    """
    query_str = f"""
    query {{
        boards(ids: {QUALIFIED_LEADS_BOARD_ID}) {{
            name
            groups(ids: ["{group_id}"]) {{
                id
                title
                items_page(limit: {limit}) {{
                    cursor
                    items {{
                        id
                        name
                        group {{
                            id
                            title
                        }}
                        column_values {{
                            id
                            text
                            value
                        }}
                    }}
                }}
            }}
        }}
    }}
    """
    
    return get_information(query_str, variables={})


def get_top_mobility_leads(limit: int = 100):
    """Get leads from Top Mobility group"""
    return get_board_items_by_group(GROUPS["top_mobility"], limit)


def get_ibam_contacts_leads(limit: int = 100):
    """Get leads from IBAM Contacts group"""
    return get_board_items_by_group(GROUPS["ibam_contacts"], limit)


def get_first_priority_leads(limit: int = 100):
    """Get leads from First Priority group"""
    return get_board_items_by_group(GROUPS["first_priority"], limit)


def get_prospects_leads(limit: int = 100):
    """Get leads from Prospects group"""
    return get_board_items_by_group(GROUPS["prospects"], limit)


def get_for_review_leads(limit: int = 100):
    """Get leads from For Review group"""
    return get_board_items_by_group(GROUPS["for_review"], limit)


def get_all_qualified_leads(limit: int = 100):
    """
    Get all items from the Qualified Leads board across all groups.
    
    Args:
        limit: Maximum number of items to return per group
    
    Returns:
        dict: Combined results from all groups
    """
    query_str = f"""
    query {{
        boards(ids: {QUALIFIED_LEADS_BOARD_ID}) {{
            name
            items_page(limit: {limit}) {{
                cursor
                items {{
                    id
                    name
                    group {{
                        id
                        title
                    }}
                    column_values {{
                        id
                        text
                        value
                    }}
                }}
            }}
        }}
    }}
    """
    
    return get_information(query_str, variables={})


def get_qualified_leads_summary():
    """
    Get summary statistics for each group in the Qualified Leads board.
    
    Returns:
        dict: Summary with item counts per group
    """
    query_str = f"""
    query {{
        boards(ids: {QUALIFIED_LEADS_BOARD_ID}) {{
            name
            groups {{
                id
                title
                items_count
            }}
        }}
    }}
    """
    
    return get_information(query_str, variables={})


if __name__ == "__main__":
    """Test the functions"""
    print("Testing Monday.com Qualified Leads Service\n")
    
    # Test each category
    categories = [
        ("Top Mobility", get_top_mobility_leads),
        ("IBAM Contacts", get_ibam_contacts_leads),
        ("First Priority", get_first_priority_leads),
        ("Prospects", get_prospects_leads),
        ("For Review", get_for_review_leads)
    ]
    
    for name, func in categories:
        try:
            result = func(limit=10)
            # Extract items count
            if result and "data" in result:
                boards = result["data"].get("boards", [])
                if boards and boards[0].get("groups"):
                    groups = boards[0]["groups"]
                    if groups and groups[0].get("items_page"):
                        items = groups[0]["items_page"].get("items", [])
                        print(f"{name}: {len(items)} items")
                    else:
                        print(f"{name}: 0 items")
                else:
                    print(f"{name}: 0 items")
        except Exception as e:
            print(f"{name}: Error - {e}")
    
    # Test summary
    print("\nGetting summary...")
    summary = get_qualified_leads_summary()
    if summary and "data" in summary:
        boards = summary["data"].get("boards", [])
        if boards:
            print(f"\nBoard: {boards[0].get('name')}")
            for group in boards[0].get("groups", []):
                print(f"  - {group['title']}: {group.get('items_count', 0)} items")
