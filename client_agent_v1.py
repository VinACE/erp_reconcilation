from mcp_agent import Agent

# Connect to your MCP server over stdio
agent = Agent()

# Call your reconciliation tool
result = agent.call("reconcile_transactions")
print("Reconciliation result:")
for row in result[:10]:  # print first 10 rows for brevity
    print(row)
