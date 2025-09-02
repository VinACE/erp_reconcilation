from mcp_agent import Agent

def main():
    # Create an agent connected to the MCP server (stdio)
    agent = Agent()

    # Call the reconciliation tool
    result = agent.call("reconcile_transactions")

    print("✅ Reconciliation result (first 10 rows):")
    for row in result[:10]:  # just print first 10 for brevity
        print(row)

if __name__ == "__main__":
    main()
