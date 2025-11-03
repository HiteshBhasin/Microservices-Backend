#!/usr/bin/env python3
"""
Test script for the generate_report function in doorloop_mcp_server.py
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path so we can import modules
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()

def test_generate_report():
    """Test the generate_report function directly."""
    print("🧪 Testing generate_report function...")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv("DOORLOOP_API_KEY")
    if not api_key:
        print("❌ ERROR: DOORLOOP_API_KEY not found in environment variables")
        print("Please make sure your .env file contains the DOORLOOP_API_KEY")
        return False
    
    print(f"✅ Found DOORLOOP_API_KEY: {api_key[:20]}...")
    
    try:
        # Import the doorloop_mcp_server module
        from mcp_server import doorloop_mcp_server as doorloop
        print("✅ Successfully imported doorloop_mcp_server module")
        
        # Call the generate_report function
        print("\n🔄 Calling generate_report()...")
        result = doorloop.generate_report()
        
        # Analyze the result
        print(f"\n📊 Result type: {type(result)}")
        
        if isinstance(result, dict):
            if "error" in result:
                print(f"❌ Function returned an error: {result['error']}")
                if "exception" in result:
                    print(f"   Exception details: {result['exception']}")
                if "raw" in result:
                    print(f"   Raw API response: {str(result['raw'])[:200]}...")
                return False
            else:
                print("✅ Function executed successfully!")
                
                # Check what kind of success response we got
                if "filename" in result and "status" in result:
                    print(f"📄 PDF generated: {result.get('filename')}")
                    print(f"📊 Status: {result.get('status')}")
                    print(f"📏 Rows: {result.get('rows', 'N/A')}")
                    print(f"📐 Columns: {result.get('columns', 'N/A')}")
                    print(f"🖼️  Figure size: {result.get('figure_size', 'N/A')}")
                    
                    # Check if the PDF file was actually created
                    pdf_filename = result.get('filename')
                    if pdf_filename and os.path.exists(pdf_filename):
                        file_size = os.path.getsize(pdf_filename)
                        print(f"✅ PDF file created: {pdf_filename} ({file_size} bytes)")
                    else:
                        print(f"⚠️  PDF file not found: {pdf_filename}")
                        
                elif "result" in result:
                    print(f"📊 Raw result returned: {str(result['result'])[:200]}...")
                else:
                    print(f"🔍 Full result: {str(result)[:500]}...")
                    
                return True
        else:
            print(f"⚠️  Unexpected result type: {type(result)}")
            print(f"🔍 Result: {str(result)[:500]}...")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure the mcp_server module and its dependencies are available")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """Test individual components of the generate_report process."""
    print("\n🔧 Testing individual components...")
    print("=" * 50)
    
    try:
        # Test basic imports
        print("Testing imports...")
        import pandas as pd
        print("✅ pandas imported successfully")
        
        from utils.Report_gen import DoorLoopReportGenerator
        print("✅ DoorLoopReportGenerator imported successfully")
        
        import matplotlib.pyplot as plt
        print("✅ matplotlib imported successfully")
        
        # Test API connection (without making the actual report call)
        print("\n🌐 Testing API connection...")
        import requests
        from mcp_server import doorloop_mcp_server as doorloop
        
        api_key = os.getenv("DOORLOOP_API_KEY")
        base_url = os.getenv("DOORLOOP_API_BASE", "https://app.doorloop.com")
        endpoint = f"{base_url.rstrip('/')}/api/reports/balance-sheet-summary?filter_accountingMethod=CASH"
        headers = {"Authorization": f"Bearer {api_key}", "accept": "application/json"}
        
        print(f"🔗 Testing endpoint: {endpoint}")
        resp = requests.get(endpoint, headers=headers, timeout=10)
        
        print(f"📡 Response status: {resp.status_code}")
        print(f"📋 Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
        
        if resp.ok:
            print("✅ API connection successful")
            try:
                json_data = resp.json()
                print(f"📦 Response keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dict'}")
            except:
                print("⚠️  Response is not valid JSON")
        else:
            print(f"❌ API request failed: {resp.status_code}")
            try:
                error_data = resp.json()
                print(f"🔍 Error response: {error_data}")
            except:
                print(f"🔍 Error text: {resp.text[:200]}...")
                
        return resp.ok
        
    except Exception as e:
        print(f"❌ Component test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting DoorLoop generate_report test")
    print("=" * 60)
    
    # Test individual components first
    components_ok = test_individual_components()
    
    if components_ok:
        # Test the full function
        success = test_generate_report()
        
        if success:
            print("\n🎉 All tests passed! The generate_report function is working correctly.")
        else:
            print("\n❌ generate_report function test failed.")
    else:
        print("\n❌ Component tests failed. Cannot proceed with full function test.")
    
    print("\n" + "=" * 60)
    print("Test completed.")