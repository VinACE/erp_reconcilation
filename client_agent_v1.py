# client_agent_v2.py
import asyncio
import json
import logging
from mcp_agent.mcp.gen_client import gen_client
from mcp_agent.server_registry.in_memory import InMemoryServerRegistry

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("client_agent")

async def main():
    logger.info("Starting ERP MCP client...")

    # Create in-memory registry and register the ERP MCP server
    registry = InMemoryServerRegistry()
    registry.register_server(
        name="erp",
        command="python",
        args=["erp_reconciliation_mcp.py"],
        description="ERP reconciliation MCP server",
        readiness_timeout=20
    )

    # Pass the registry to gen_client
    async with gen_client("erp", server_registry=registry) as client:
        logger.info("Connected to ERP MCP server.")

        # List tools
        tools = await client.list_tools()
        logger.info("Available tools: %s", [t.name for t in tools])

        # List resources
        resources = await client.list_resources()
        logger.info("Available resources: %s", [r.uri for r in resources])

        # Fetch ERP transactions
        erp_data = await client.read_resource("resource://erp/transactions")
        logger.info(
            "Sample ERP transaction: %s",
            erp_data.content[0] if erp_data.content else "No data"
        )

        # Fetch Bank transactions
        bank_data = await client.read_resource("resource://bank/transactions")
        logger.info(
            "Sample Bank transaction: %s",
            bank_data.content[0] if bank_data.content else "No data"
        )

        # Call reconciliation tool
        result = await client.call_tool("reconcile_transactions", arguments={})
        logger.info("Reconciliation result:")
        print(json.dumps(result.content, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
