import asyncio
import json
from mcp import gen_client

# Optional: for LangChain + local LLaMA/Mixtral
from langchain.agents import Tool, initialize_agent
from langchain.llms import HuggingFacePipeline
from transformers import pipeline

# -----------------------------
# Set up local LLaMA/Mixtral LLM (optional)
# -----------------------------
llm_pipeline = pipeline(
    task="text-generation",
    model="path/to/your/mixtral-7b",  # Replace with your local model path
    torch_dtype="auto",
    device_map="auto",
    max_new_tokens=512
)

llm = HuggingFacePipeline(pipeline=llm_pipeline)

# -----------------------------
# Async main function
# -----------------------------
async def main():
    # Define the ERP MCP server
    erp_server = {
        "name": "erp",
        "command": "python",
        "args": ["erp_reconciliation_mcp.py"],
        "description": "ERP reconciliation MCP server",
        "readiness_timeout": 20,
    }

    # Launch client and connect to the MCP server
    async with gen_client([erp_server]) as client:
        print("Connected to ERP MCP server.")

        # List available tools
        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])

        # List available resources
        resources = await client.list_resources()
        print("Available resources:", [r.uri for r in resources])

        # Fetch ERP transact
