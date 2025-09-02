# mcp_client_openai.py
import asyncio
from agents import Agent, Runner
from agents.context import RunnerContext

async def main():
    # Define the agent
    agent = Agent(
        name="ReconciliationAgent",
        instructions="Fetch ERP and Bank transactions via MCP and reconcile them.",
        model="gpt-4.1-mini",
    )

    # Tell Runner about your MCP server
    context = RunnerContext(mcp_config={
        "servers": {
            "erp_reconciliation": {
                "command": "python3",
                "args": ["erp_reconciliation_mcp.py"]
            }
        }
    })

    # Run agent with context
    result = await Runner.run(
        agent,
        "Please reconcile ERP and Bank transactions and summarize issues.",
        context=context
    )

    print("---- Final Agent Report ----")
    print(result.output_text)

    # Show reasoning/tool usage
    for step in result.steps:
        print("\nStep:", step.type)
        print("Tool call:", step.tool_call)
        print("Output:", step.output)

if __name__ == "__main__":
    asyncio.run(main())
