import asyncio
import json
import logging
import subprocess
import sys
from mcp_agent.mcp.gen_client import gen_client_stdio

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("client_agent")

ERP_SERVER_CMD = [sys.executable, "erp_reconciliation_mcp.py"]

async def main():
    # Launch the ERP MCP server manually
    logger.info("Starting ERP MCP server...")
    server_proc = subprocess.Popen(
        ERP_SERVER_CMD,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        # Wait a moment to let the server start
        await asyncio.sleep(2)

        # Connect client via stdio
        logger.info("Connecting client via gen_client_stdio...")
        async with gen_client_stdio(stdin=server_proc.stdin, stdout=server_proc.stdout) as client:
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

    finally:
        # Stop the server
        logger.info("Terminating ERP MCP server...")
        server_proc.terminate()
        await asyncio.sleep(1)  # let it exit cleanly
        server_proc.kill()
        logger.info("ERP MCP server stopped.")


if __name__ == "__main__":
    asyncio.run(main())
