# client_agent_v3.py
import asyncio
import json
import logging
from mcp_agent.mcp.gen_client import gen_client  # works in 0.1.13

# Optional: LangChain + local LLaMA/Mixtral support
# Uncomment if you want to use local LLMs
# from langchain.agents import Tool, initialize_agent
# from langchain.llms import HuggingFacePipeline
# from transformers import pipeline

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("client_agent")

# -----------------------------
# Optional: local LLaMA/Mixtral LLM
# -----------------------------
# llm_pipeline = pipeline(
#     task="text-generation",
#     model="path/to/your/mixtral-7b",  # replace with your local model path
#     torch_dtype="auto",
#     device_map="auto",
#     max_new_tokens=512
# )
# llm = HuggingFacePipeline(pipeline=llm_pipeline)

# -----------------------------
# Async main function
# -----------------------------
async def main():
    logger.info("Starting ERP MCP client...")

    # Direct process command for MCP server
    server_command = ["python", "erp_reconciliation_mcp.py"]

    # Connect to MCP server (direct mode)
    async with gen_client(server_command) as client:
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

        # Call reconciliation
