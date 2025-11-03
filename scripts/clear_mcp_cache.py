#!/usr/bin/env python3
"""
Clear MCP Server Cache Script

This script helps clear various types of MCP server caches:
1. Python module cache for MCP servers
2. FastMCP instance cache
3. MCP stdio connections
4. Environment variable cache
"""

import os
import sys
import importlib
from pathlib import Path

def clear_python_module_cache():
    """Clear Python module cache for MCP-related modules."""
    print("🧹 Clearing Python module cache...")
    
    mcp_modules = [
        'mcp_server.doorloop_mcp_server',
        'mcp_server.connectteam_mcp_server',
        'doorloop_mcp_server',
        'connectteam_mcp_server',
        'mcp.server.fastmcp',
        'mcp.server',
        'mcp'
    ]
    
    cleared_count = 0
    for module_name in mcp_modules:
        if module_name in sys.modules:
            del sys.modules[module_name]
            print(f"   ✅ Cleared: {module_name}")
            cleared_count += 1
        else:
            print(f"   ⚪ Not loaded: {module_name}")
    
    print(f"🎯 Cleared {cleared_count} modules from cache")
    return cleared_count

def force_reload_mcp_modules():
    """Force reload MCP server modules."""
    print("\n🔄 Force reloading MCP modules...")
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    mcp_files = [
        'mcp_server.doorloop_mcp_server',
        'mcp_server.connectteam_mcp_server'
    ]
    
    for module_name in mcp_files:
        try:
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                print(f"   ✅ Reloaded: {module_name}")
            else:
                # Try to import and then reload
                module = importlib.import_module(module_name)
                importlib.reload(module)
                print(f"   ✅ Imported & Reloaded: {module_name}")
        except Exception as e:
            print(f"   ❌ Failed to reload {module_name}: {e}")

def clear_fastmcp_instances():
    """Clear FastMCP instances if any are cached."""
    print("\n🚀 Clearing FastMCP instances...")
    
    # Clear any global FastMCP instances
    if 'mcp_server.doorloop_mcp_server' in sys.modules:
        module = sys.modules['mcp_server.doorloop_mcp_server']
        if hasattr(module, 'mcp'):
            print("   ✅ Found doorloop FastMCP instance")
            # Reset the FastMCP instance
            try:
                module.mcp = None
                print("   ✅ Cleared doorloop FastMCP instance")
            except:
                print("   ⚠️  Could not clear doorloop FastMCP instance")
    
    if 'mcp_server.connectteam_mcp_server' in sys.modules:
        module = sys.modules['mcp_server.connectteam_mcp_server']
        if hasattr(module, 'mcp'):
            print("   ✅ Found connectteam FastMCP instance")
            try:
                module.mcp = None
                print("   ✅ Cleared connectteam FastMCP instance")
            except:
                print("   ⚠️  Could not clear connectteam FastMCP instance")

def reload_environment_variables():
    """Reload environment variables for MCP servers."""
    print("\n🔑 Reloading environment variables...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
        print("   ✅ Environment variables reloaded")
        
        # Check critical variables
        critical_vars = [
            'DOORLOOP_API_KEY',
            'CONNECTTEAM_API_KEY', 
            'CONNECTEAM_TASKBOARD_ID'
        ]
        
        for var in critical_vars:
            status = "✅ Set" if os.getenv(var) else "❌ Missing"
            print(f"   {var}: {status}")
            
    except ImportError:
        print("   ⚠️  python-dotenv not available")

def clear_mcp_stdio_cache():
    """Clear any stdio connection caches."""
    print("\n📡 Clearing MCP stdio caches...")
    
    # Clear any cached stdio connections
    stdio_cache_vars = [
        '_mcp_stdio_cache',
        '_mcp_client_cache',
        '_fastmcp_cache'
    ]
    
    for var in stdio_cache_vars:
        if var in globals():
            del globals()[var]
            print(f"   ✅ Cleared global: {var}")

def main():
    """Main cache clearing function."""
    print("🧹 MCP Server Cache Clearing Tool")
    print("=" * 50)
    
    # Clear different types of caches
    clear_python_module_cache()
    clear_fastmcp_instances() 
    force_reload_mcp_modules()
    reload_environment_variables()
    clear_mcp_stdio_cache()
    
    print("\n" + "=" * 50)
    print("🎉 MCP Server cache clearing completed!")
    print("\n💡 Next steps:")
    print("   1. Restart your application if it's running")
    print("   2. Test MCP server functions")
    print("   3. Check MCP stdio connections")

if __name__ == "__main__":
    main()