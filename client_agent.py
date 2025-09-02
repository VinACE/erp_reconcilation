import asyncio
import json
from mcp_agent.mcp.gen_client import gen_client

async def main():
    # Connect to the "erp" server defined in mcp_agent.config.yaml
    async with gen_client("erp") as client:
        # List available tools
        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])

        # Call the reconciliation tool
        result = await client.call_tool("reconcile_transactions", arguments={})

        # Print nicely formatted result
        print("Reconciliation result:")
        print(json.dumps(result.content, indent=2))

        # Optionally: also try listing resources
        resources = await client.list_resources()
        print("Available resources:", [r.uri for r in resources])

        # Fetch ERP transactions resource
        erp_data = await client.read_resource("resource://erp/transactions")
        print("Sample ERP transaction:", erp_data.content[0] if erp_data.content else "No data")

        # Fetch Bank transactions resource
        bank_data = await client.read_resource("resource://bank/transactions")
        print("Sample Bank transaction:", bank_data.content[0] if bank_data.content else "No data")

if __name__ == "__main__":
    asyncio.run(main())
