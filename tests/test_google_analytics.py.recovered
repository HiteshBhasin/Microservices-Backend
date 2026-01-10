"""
Quick test script for Google Analytics integration
"""
import sys
sys.path.insert(0, '.')

print("=" * 80)
print("GOOGLE ANALYTICS INTEGRATION TEST")
print("=" * 80)

# Test 1: Import routes
print("\n1. Testing route imports...")
try:
    from routes.google import router
    print("   ✓ Google routes imported successfully")
    print(f"   ✓ Found {len(router.routes)} endpoints:")
    for route in router.routes:
        print(f"      - {route.methods} {route.path}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Import MCP server
print("\n2. Testing MCP server...")
try:
    from mcp_server.google_analytics_mcp_server import server
    print(f"   ✓ MCP server '{server.name}' initialized successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Check main app registration
print("\n3. Testing main app integration...")
try:
    from app.main import app
    google_routes = [r for r in app.routes if hasattr(r, 'path') and '/google' in r.path]
    print(f"   ✓ Main app has {len(google_routes)} Google Analytics routes registered")
    for route in google_routes[:3]:  # Show first 3
        print(f"      - {route.path}")
    if len(google_routes) > 3:
        print(f"      ... and {len(google_routes) - 3} more")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Test service functions
print("\n4. Testing service functions...")
try:
    from services.google_analytics import get_total_summary
    summary = get_total_summary()
    if summary:
        print("   ✓ get_total_summary() works")
        print(f"      - Active Users: {summary.get('activeUsers')}")
        print(f"      - Engagement Rate: {summary.get('engagementRate')}")
    else:
        print("   ⚠ Function returned no data (check GA4 configuration)")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
