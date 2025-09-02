import asyncio
import json
from mcp_agent.mcp.gen_client import gen_client

async def main():
    # Launch ERP MCP server manually via gen_client
    server_command = [
        {
            "name": "erp",
            "command": "python",
            "args": ["erp_reconciliation_mcp.py"],
            "description": "ERP Reconciliation MCP Server",
            "readiness_timeout": 20,
        }
    ]

    # Connect to MCP server
    async with gen_client(server_command) as client:
        print("Connected to ERP MCP server.")

        # List tools
        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])

        # List resources
        resources = await client.list_resources()
        print("Available resources:", [r.uri for r in resources])

        # Fetch ERP transactions
        erp_data = await client.read_resource("resource://erp/transactions")
        print("Sample ERP transaction:", erp_data.content[0] if erp_data.content else "No data")

        # Fetch Bank transactions
        bank_data = await client.read_resource("resource://bank/transactions")
        print("Sample Bank transaction:", bank_data.content[0] if bank_data.content else "No data")

        # Call reconciliation tool
        result = await client.call_tool("reconcile_transactions", arguments={})
        print("Reconciliation result:")
        print(json.dumps(result.content, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
