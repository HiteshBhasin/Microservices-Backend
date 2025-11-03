#!/bin/bash
# MCP Server Reset Script

echo "🔧 MCP Server Reset Commands"
echo "=========================="

echo "1. Kill any running MCP server processes:"
echo "   pkill -f 'doorloop_mcp_server'"
echo "   pkill -f 'connectteam_mcp_server'"
echo ""

echo "2. Clear Python cache manually:"
echo "   find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null"
echo "   find . -name '*.pyc' -delete 2>/dev/null"
echo ""

echo "3. Test MCP servers individually:"
echo "   python mcp_server/doorloop_mcp_server.py"
echo "   python mcp_server/connectteam_mcp_server.py"
echo ""

echo "4. Clear VS Code/Jupyter cache:"
echo "   - Restart Kernel (if using Jupyter)"
echo "   - Reload Window (if using VS Code)"
echo ""

echo "5. Force reload modules in Python:"
cat << 'EOF'
import sys
import importlib

# Clear specific modules
modules_to_clear = [k for k in sys.modules.keys() if 'mcp' in k.lower()]
for mod in modules_to_clear:
    del sys.modules[mod]

# Reload dotenv
from dotenv import load_dotenv
load_dotenv(override=True)
EOF

echo ""
echo "6. Check MCP server status:"
echo "   ps aux | grep mcp"
echo "   netstat -tulpn | grep python"