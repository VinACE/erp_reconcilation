import asyncio
import json
import logging
from mcp_agent.mcp.gen_client import gen_client

# Enable debug logs (optional, comment out if too noisy)
logging.basicConfig(level=logging.INFO)


async def main():
    # Launch your ERP MCP server subprocess directly
    async with gen_client("python", ["erp_reconciliation_mcp.py"]) as client:
        # List available tools
        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])

        # Run reconciliation tool
        result = await client.call_tool("reconcile_transactions", arguments={})
        print("Reconciliation result:")
        print(json.dumps(result.content, indent=2))

        # Discover resources
        resources = await client.list_resources()
        print("Available resources:", [r.uri for r in resources])

        # Fetch ERP transactions
        erp_data = await client.read_resource("resource://erp/transactions")
        print("Sample ERP transaction:", erp_data.content[0] if erp_data.content else "No data")

        # Fetch Bank transactions
        bank_data = await client.read_resource("resource://bank/transactions")
        print("Sample Bank transaction:", bank_data.content[0] if bank_data.content else "No data")

if __name__ == "__main__":
    asyncio.run(main())
