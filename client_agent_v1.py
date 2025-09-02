# client_agent_debug.py
import asyncio
import json
import logging
from mcp_agent.mcp.gen_client import gen_client


# -------------------------
# Configure debug logging
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

    # Define server command for ERP MCP server
    server_command = [
        {
            "name": "erp",
            "command": "python",
            "args": ["erp_reconciliation_mcp.py"],
            "description": "ERP Reconciliation MCP Server",
            "readiness_timeout": 20,  # seconds
        }
    ]

    # Connect to the MCP server
    async with gen_client(server_command) as client:
        logger.info("Connected to ERP MCP server.")

        # List available tools
        tools = await client.list_tools()
        logger.debug("Tools available: %s", [t.name for t in tools])

        # List available resources
        resources = await client.list_resources()
        logger.debug("Resources available: %s", [r.uri for r in resources])

        # Fetch ERP transactions
        erp_data = await client.read_resource("resource://erp/transactions")
        logger.debug("ERP transactions sample: %s",
                     erp_data.content[0] if erp_data.content else "No data")

        # Fetch Bank transactions
        bank_data = await client.read_resource("resource://bank/transactions")
        logger.
