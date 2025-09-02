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
    model="path/to/your/mixtral-7b",  # <-- Replace with your local model path
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

        # Fetch ERP transactions
        erp_data = await client.read_resource("resource://erp/transactions")
        print("Sample ERP transaction:", erp_data.content[0] if erp_data.content else "No data")

        # Fetch Bank transactions
        bank_data = await client.read_resource("resource://bank/transactions")
        print("Sample Bank transaction:", bank_data.content[0] if bank_data.content else "No data")

        # Wrap the reconciliation tool for LangChain agent
        async def reconcile_tool_wrapper(query: str) -> str:
            result = await client.call_tool("reconcile_transactions", arguments={})
            return json.dumps(result.content, indent=2)

        reconcile_tool = Tool(
            name="Reconcile Transactions",
            func=reconcile_tool_wrapper,
            description="Match ERP and Bank transactions and flag discrepancies."
        )

        # Initialize LangChain agent
        agent = initialize_agent(
            tools=[reconcile_tool],
            llm=llm,
            agent="zero-shot-react-description",
            verbose=True
        )

        # Ask agent to reconcile
        response = await agent.arun(
            "Please reconcile ERP and Bank transactions and summarize discrepancies."
        )
        print("Agent output:\n", response)

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())
