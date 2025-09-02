import asyncio
import json
from mcp_agent.mcp.gen_client import gen_client
from mcp_agent.server_registry.yaml import YamlServerRegistry

# LangChain imports
from langchain.agents import Tool, initialize_agent
from langchain.llms import HuggingFacePipeline
from transformers import pipeline

# -----------------------------
# Set up local LLaMA/Mixtral LLM
# -----------------------------
llm_pipeline = pipeline(
    task="text-generation",
    model="path/to/your/mixtral-7b",  # replace with local path
    torch_dtype="auto",
    device_map="auto",
    max_new_tokens=512
)

llm = HuggingFacePipeline(pipeline=llm_pipeline)

# -----------------------------
# Async main function
# -----------------------------
async def main():
    # Load MCP servers from YAML config
    registry = YamlServerRegistry("mcp_agent.config.yaml")

    # Connect to MCP servers
    async with gen_client(registry) as client:

        print("Available tools and resources:")
        tools_list = await client.list_tools()
        resources_list = await client.list_resources()
        print("Tools:", [t.name for t in tools_list])
        print("Resources:", [r.uri for r in resources_list])

        # Wrap reconciliation tool for LangChain
        async def reconcile_tool_wrapper(query: str) -> str:
            result = await client.call_tool("reconcile_transactions", arguments={})
            return json.dumps(result.content, indent=2)

        reconcile_tool = Tool(
            name="Reconcile Transactions",
            func=reconcile_tool_wrapper,
            description="Match ERP and Bank transactions and flag discrepancies."
        )

        # Initialize LangChain agent with the local LLaMA/Mixtral model
        agent = initialize_agent(
            tools=[reconcile_tool],
            llm=llm,
            agent="zero-shot-react-description",
            verbose=True
        )

        # Run agent on a query
        response = await agent.arun("Please reconcile ERP and Bank transactions and summarize discrepancies.")
        print("Agent output:\n", response)


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())
