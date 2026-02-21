import os
import sys
from google.adk.agents import LlmAgent
from google.adk.tools import McpToolset
from mcp.client.stdio import StdioServerParameters
from returns_service import check_return_eligibility, initiate_return
from dotenv import load_dotenv

# Load for local discovery
load_dotenv()

# Setup tools
mcp_path = r"C:\Users\jvash\AppData\Local\Programs\Python\Python311\Scripts\postgresql-mcp.exe"
mcp_env = {**os.environ}
mcp_env["PATH"] = r"C:\Users\jvash\AppData\Local\Programs\Python\Python311\Scripts;" + mcp_env.get("PATH", "")

mcp_params = StdioServerParameters(
    command=mcp_path,
    args=[],
    env=mcp_env
)
db_mcp_toolset = McpToolset(connection_params=mcp_params)

# Export the agent clearly for ADK
root_agent = LlmAgent(
    name="MasterSupportAgent",
    model="gemini-flash-latest",
    description="Consolidated agent for all customer support tasks.",
    instruction=(
        "You are a Master Support Specialist. You handle all customer inquiries directly using your specialized tools."
        "\n\nSKILLS:"
        "\n1. Order & Billing: Use the MCP tools to check order status, cancel orders, or verify invoice amounts."
        "\n2. Returns: Use the return tools to check eligibility (30-day policy) and initiate returns."
        "\n3. Tech Support: For bug reports, gather Device Info, OS, and Browser to escalate to engineering."
        "\n\nPOLICIES:"
        "- Never expose internal database IDs or system paths."
        "- If a database call fails, apologize and offer a human follow-up."
        "- Always be professional and clear about the 30-day return policy."
    ),
    tools=[db_mcp_toolset, check_return_eligibility, initiate_return]
)
