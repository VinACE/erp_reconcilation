# client_agent_v2.py
import asyncio
import json
import logging
from mcp_agent.mcp.gen_client import gen_client
from mcp_agent.server_registry.in_memory import InMemoryServerRegistry

# -------------------------
# Configure logging
# -------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("client_agent")

# -------------------------
# Async main function
# -------------------------
async def main():
    logger.info("Starting ERP MCP client...")

    # Create a server registry and register the ERP MCP server
    registry = InMemoryServerRegistry()
    registry.register_server(
        name="erp",
        command="python",
        args=["erp_reconciliation_mcp.py"],
        description="ERP Reconciliation MCP Server",
        readiness_timeout=20
    )

    # Connect to the MCP server using the registry
    async with gen_client("erp", server_registry=registry) as client:
        logger.info("Connected to ERP MCP server.")

        # List available tools
        tools = await client.list_tools()
        logger.debug("Tools available: %s", [t.name for t in tools])

        # List available resources
        resources = await client.list_resources()
        logger.debug("Resources available: %s", [r.uri for r in resources])

        # Fetch ERP transactions
        erp_data = await client.read_resource("resource://erp/transactions")
        logger.debug("ERP transaction sample: %s",
                     erp_data.content[0] if erp_data.content else "No data")

        # Fetch Bank transactions
        bank_data = await client.read_resource("resource://bank/transactions")
        logger.debug("Bank transaction sample: %s",
                     bank_data.content[0] if bank_data.content else "No data")

        # Call reconciliation tool
        result = await client.call_tool("reconcile_transactions", arguments={})
        logger.info("Reconciliation result:")
        print(json.dumps(result.content, indent=2))

# -------------------------
# Run main
# -------------------------
if __name__ == "__main__":
    asyncio.run(main())
