import asyncio
import json
from mcp_agent.server_registry.default import DefaultServerRegistry
from mcp_agent.mcp.gen_client import gen_client

async def main():
    # Create a registry
    registry = DefaultServerRegistry()

    # Register your ERP server
    registry.register_server(
        "erp",
        "python",  # executable
        ["erp_reconciliation_mcp.py"],  # script path
    )

    # Pass the registry into gen_client
    async with gen_client(registry) as client:
        # List tools
        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])

        # Call reconciliation tool
        result = await client.call_tool("reconcile_transactions", arguments={})
        print("Reconciliation result:")
        print(json.dumps(result.content, indent=2))

        # List resources
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
