import asyncio
import json
import logging
from mcp_agent.mcp.gen_client import gen_client
from mcp_agent.mcp.server_process import ServerProcess

# ---------------------------
# Configure logging
# ---------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("client_agent")

# ---------------------------
# Minimal registry class
# ---------------------------
class SimpleRegistry:
    """
    Minimal registry to satisfy gen_client() in mcp-agent 0.1.13
    """
    def __init__(self, executable, args):
        self.executable = executable
        self.args = args

    async def initialize_server(self, *args, **kwargs):
        logger.debug(f"Initializing ERP MCP server: {self.executable} {self.args}")
        # ServerProcess wraps your executable + args to run the server
        return ServerProcess(self.executable, self.args)


# ---------------------------
# Main client logic
# ---------------------------
async def main():
    # Create the minimal registry pointing to your ERP server
    registry = SimpleRegistry("python", ["erp_reconciliation_mcp.py"])

    logger.info("Starting MCP client...")
    async with gen_client(registry) as client:
        logger.info("Client connected. Listing tools...")
