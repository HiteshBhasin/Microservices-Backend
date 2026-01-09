import sys
sys.path.append('C:/Users/bhasi/OneDrive/Desktop/Microservices-Backend')

from services.monday_api_client import get_information, query
import json

# Categories we're looking for
target_categories = [
    "Top Mobility",
    "IBAM Contracts", 
    "First Priority (For Discover)",
    "Prospects",
    "For Review"
]

print("=" * 80)
print("ANALYZING MONDAY.COM DATA FOR BOARD CATEGORIES")
print("=" * 80)

result = get_information(query=query)

if result and "data" in result:
    boards = result.get("data", {}).get("boards", [])
    
    for board in boards:
        items = board.get("items_page", {}).get("items", [])
        print(f"\n📊 Board has {len(items)} items\n")
        
        # Check first few items structure
        if items:
            print("Sample item structure:")
            sample = items[0]
            print(f"  - ID: {sample.get('id')}")
            print(f"  - Name: {sample.get('name')}")
            print(f"  - Column count: {len(sample.get('column_values', []))}")
            
            # Check all column IDs and first few values
            print("\n📋 Available columns:")
            for col in sample.get('column_values', [])[:10]:
                print(f"  - {col.get('id')}: {col.get('value')[:50] if col.get('value') else 'None'}...")
        
        # Search for category matches
        print("\n" + "=" * 80)
        print("🔍 SEARCHING FOR TARGET CATEGORIES IN DATA:")
        print("=" * 80)
        
        for category in target_categories:
            found_count = 0
            found_in = []
            
            for item in items:
                # Check in name
                if category.lower() in item.get('name', '').lower():
                    found_count += 1
                    found_in.append(f"Item name: {item.get('name')}")
                
                # Check in all column values
                for col in item.get('column_values', []):
                    if col.get('value') and category.lower() in str(col.get('value')).lower():
                        found_count += 1
                        found_in.append(f"Column {col.get('id')}: {item.get('name')}")
            
            if found_count > 0:
                print(f"\n✅ '{category}' - FOUND {found_count} times:")
                for match in found_in[:5]:  # Show first 5 matches
                    print(f"    {match}")
            else:
                print(f"\n❌ '{category}' - NOT FOUND")
        
        # Also check what unique values exist in status/category type columns
        print("\n" + "=" * 80)
        print("📊 CHECKING STATUS/CATEGORY COLUMNS:")
        print("=" * 80)
        
        status_columns = {}
        for item in items:
            for col in item.get('column_values', []):
                col_id = col.get('id')
                if 'status' in col_id.lower() or 'color' in col_id.lower():
                    if col_id not in status_columns:
                        status_columns[col_id] = set()
                    if col.get('value'):
                        status_columns[col_id].add(str(col.get('value'))[:100])
        
        for col_id, values in status_columns.items():
            print(f"\nColumn '{col_id}' unique values ({len(values)} total):")
            for val in list(values)[:10]:  # Show first 10
                print(f"  - {val}")

else:
    print("❌ No data returned from Monday.com API")
