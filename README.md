# Microservices-Backend
These are Backend for Nesthost
ops360-backend/
│
├── main.py                     # FastAPI entrypoint (API Gateway)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (API keys, DB URLs)
│
├── routes/                     # API endpoints exposed to frontend (React)
│   ├── __init__.py
│   ├── bookings.py             # /bookings endpoints
│   ├── invoices.py             # /invoices endpoints
│   ├── tasks.py                # /tasks endpoints
│   ├── chat.py                 # /chat endpoints (WebSocket)
│
├── services/                   # Clients that call MCP servers or DB
│   ├── __init__.py
│   ├── zenya_client.py         # calls Zenya MCP server via HTTP/stdio
│   ├── quickbooks_client.py    # calls QuickBooks MCP server
│   ├── connecteam_client.py    # calls Connecteam MCP server
│   ├── mailchimp_client.py     # calls MailChimp MCP server
│   ├── gmail_client.py         # calls Gmail MCP server
│   ├── doorloop_client.py      # calls Doorloop MCP server  
│   ├── Monday_client.py        # calls Monday MCP server 
│
├── mcp_servers/                # Each MCP server exposes tools to wrap APIs
│   ├── __init__.py
│   ├── zenya_server.py         # MCP server exposing Zenya tools
│   ├── quickbooks_server.py    # MCP server exposing QuickBooks tools
│   ├── connecteam_server.py    # MCP server exposing Connecteam tools
│   ├── mailchimp_server.py     # MCP server exposing MailChimp tools
│   ├── gmail_server.py         # MCP server exposing Gmail tools
│   ├── doorloop_server.py      # MCP server exposing Doorloop tools
│   ├── Monday_server.py        # MCP server exposing Monday.com tools    
│
├── models/                     # Pydantic schemas for FastAPI routes
│   ├── __init__.py
│   ├── booking_models.py
│   ├── invoice_models.py
│   ├── task_models.py
│
├── core/                       # Core utilities
│   ├── config.py               # Loads env variables, DB configs
│   ├── db.py                   # Database connection (PostgreSQL, Redis)
│   ├── event_bus.py            # RabbitMQ / Pub-Sub setup
│   ├── security.py             # Auth/JWT helpers
│
├── tests/                      # Unit & integration tests
│   ├── test_bookings.py
│   ├── test_invoices.py
│   ├── test_tasks.py
│
└── Dockerfile                  # For containerizing the app
