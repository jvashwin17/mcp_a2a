import os
import sys
import asyncio
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.tools import McpToolset
from mcp.client.stdio import StdioServerParameters

# Load environment variables (including DATABASE_URL and GEMINI_API_KEY)
load_dotenv()

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("Error: DATABASE_URL not set in .env file", file=sys.stderr)
    sys.exit(1)

async def run_multi_agent():
    print("Initializing Root Router and 4 Sub-Agents...", flush=True)

    mcp_path = r"C:\Users\jvash\AppData\Local\Programs\Python\Python311\Scripts\postgresql-mcp.exe"
    mcp_env = {**os.environ} 
    mcp_env["PATH"] = r"C:\Users\jvash\AppData\Local\Programs\Python\Python311\Scripts;" + mcp_env.get("PATH", "")

    # 1. Setup the MCP connection parameters for postgresql-mcp
    mcp_params = StdioServerParameters(
        command=mcp_path,
        args=[],
        env=mcp_env
    )
    db_mcp_toolset = McpToolset(connection_params=mcp_params)

    # Optimized Master Agent: One agent handles all tools directly to save costs (2 requests vs 4)
    from returns_service import check_return_eligibility, initiate_return

    master_agent = LlmAgent(
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

    # Check if API key is set before running
    if not os.environ.get("GEMINI_API_KEY"):
        print("\n[Warning] GEMINI_API_KEY is not set. Please get a free key from https://aistudio.google.com/app/apikey and add it to .env.")
        print("Waiting for key to be added...\n")
        return

    print("Waiting 2s for startup...", flush=True)
    await asyncio.sleep(2)

    # User-requested test scenarios
    test_queries = [
        "I want to return my order b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b14. Please initiate it."
    ]

    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    
    session_service = InMemorySessionService()
    runner = Runner(
        agent=master_agent, 
        app_name="CustomerSupportApp", 
        session_service=session_service
    )
    
    try:
        user_id = "test_user"
        for idx, query in enumerate(test_queries, 1):
            session_id = f"session_{idx}"
            print(f"\n[Test Query {idx}]: '{query}'", flush=True)
            
            # Create session 
            await session_service.create_session(user_id=user_id, session_id=session_id, app_name="CustomerSupportApp")
            
            # Construct the user message
            user_msg = types.Content(
                role="user",
                parts=[types.Part(text=query)]
            )
            
            # Retry loop for ResourceExhausted (Quota) issues
            max_retries = 3
            retry_delay = 65 # Gemini Free Tier is usually 60s window
            
            for attempt in range(max_retries):
                try:
                    print(f"Routing request (Attempt {attempt + 1})...", flush=True)
                    final_text = ""
                    async for event in runner.run_async(
                        user_id=user_id,
                        session_id=session_id,
                        new_message=user_msg
                    ):
                        if event.content and event.content.parts:
                            for part in event.content.parts:
                                if part.text:
                                    final_text += part.text
                    
                    # Check if the text itself contains a quota error (Provider might return it as text)
                    if "429" in final_text or "RESOURCE_EXHAUSTED" in final_text:
                         if attempt < max_retries - 1:
                            print(f"\n[Quota Limit Reached in text] Waiting {retry_delay} seconds for refresh...", flush=True)
                            await asyncio.sleep(retry_delay)
                            continue

                    print(f"\n[Final Response]:\n{final_text}", flush=True)
                    break # Success, exit retry loop
                    
                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                        if attempt < max_retries - 1:
                            print(f"\n[Quota Limit Reached in exception] Waiting {retry_delay} seconds for refresh...", flush=True)
                            await asyncio.sleep(retry_delay)
                            continue
                    
                    print(f"\n[Error]: Details: {e}", flush=True)
                    break
            
            print("-" * 40, flush=True)
            
    except Exception as e:
        print(f"\n[Error]: Failed to run the agent. Details: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_multi_agent())
