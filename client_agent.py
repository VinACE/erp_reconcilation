import asyncio
import json
import logging
from mcp_agent.mcp.gen_client import gen_client

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("client_agent")


# Minimal registry because 0.1.13 has no built-in server_registry
class SimpleRegistry:
    def __init__(self, executable, args):
        self.executable = executable
        self.args = args

    async def initialize_server(self, *_, **__):
        from mcp_agent.mcp.server_process import ServerProcess
        logger.debug(f"Initializing server: {self.executable} {self.args}")
        return ServerProcess(self.executable, self.args)


async def main():
    registry = SimpleRegistry("python", ["erp_reconciliation_mcp.py"])

    logger.info("Starting client with ERP MCP server...")

    async with gen_client(registry) as client:
        logger.info("Client connected. Listing tools...")

        tools = await client.list_tools()
        logger.debug(f"Raw tools: {tools}")
        print("Available tools:", [t.name for t in tools])

        logger.info("Calling reconciliation tool...")
        result = await client.call_tool("reconcile_transactions", arguments={})
        logger.debug(f"Reconciliation raw result: {result}")
        print("Reconciliation result:")
        print(json.dumps(result.content, indent=2))

        logger.info("Listing resources...")
        resources = await client.list_resources()
        logger.debug(f"Raw resources: {resources}")
        print("Available resources:", [r.uri for r in resources])

        logger.info("Fetching ERP transactions...")
        erp_data = await client.read_resource("resource://erp/transactions")
        logger.debug(f"ERP data response: {erp_data}")
        print("Sample ERP transaction:", erp_data.content[0] if erp_data.content else "No data")

        logger.info("Fetching Bank transactions...")
        bank_data = await client.read_resource("resource://bank/transactions")
        logger.debug(f"Bank data response: {bank_data}")
        print("Sample Bank transaction:", bank_data.content[0] if bank_data.content else "No data")

    logger.info("Client finished successfully.")


if __name__ == "__main__":
    asyncio.run(main())
