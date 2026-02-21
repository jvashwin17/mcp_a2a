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

    # SUB-AGENT 1: Order Status Agent (Connected via MCP to Supabase)
    order_status_agent = LlmAgent(
        name="OrderStatusAgent",
        model="gemini-flash-latest",
        description="Handles checking order status and cancelling orders. Must be used whenever a customer asks about their order or requests a cancellation.",
        instruction=(
            "You are the Order Status Specialist. Your primary job is to interact with the database to check or update orders."
            "To check an order, use the database query tools to fetch the order details via customer_id or order id."
            "If a customer requests to cancel an order, you must execute an UPDATE SQL query to change that order's status to 'canceled'."
            "Always return clear, factual updates verifying the current status from the database."
        ),
        tools=[db_mcp_toolset]
    )

    # SUB-AGENT 2: Billing Agent
    billing_agent = LlmAgent(
        name="BillingAgent",
        model="gemini-flash-latest",
        description="Handles all inquiries regarding billing, invoices, payment method updates, and refunds.",
        instruction=(
            "You are the Billing Specialist. Handle any questions about payments, invoices, or refunds."
            "You have database access to verify order amounts and billing history."
        ),
        tools=[db_mcp_toolset]
    )

    # SUB-AGENT 3: Technical Issue Escalation Agent
    technical_agent = LlmAgent(
        name="TechnicalIssueEscalationAgent",
        model="gemini-flash-latest",
        description="Handles complex product bugs, site crashes, or app errors, escalating them to the engineering team.",
        instruction=(
            "You are the Technical Escalation Specialist."
            "When users report bugs, app crashes, or errors, gather the device info, OS, and reproduction steps."
            "Assure them this is being escalated to the engineering team."
        )
    )

    # SUB-AGENT 4: General Support Agent
    general_support_agent = LlmAgent(
        name="GeneralSupportAgent",
        model="gemini-flash-latest",
        description="Handles general questions, account settings, generic greetings, and anything not covered by billing, orders, or technical issues.",
        instruction=(
            "You are the General Support Specialist. Answer basic FAQs, guide users on setting up their profiles, "
            "and provide friendly and helpful greetings. Keep it concise."
        )
    )

    from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
    
    # Returns Specialist is now a separate service surfaced via RemoteA2aAgent
    returns_remote_agent = RemoteA2aAgent(
        name="ReturnsSpecialistAgent",
        agent_card="http://localhost:8001",
        description="Specialist for checking return eligibility and processing returns."
    )

    # ROOT ROUTER AGENT:
    root_router = LlmAgent(
        name="RootRouterAgent",
        model="gemini-flash-latest",
        description="Main entry point that routes user requests to the appropriate specialist.",
        instruction=(
            "You are a master router for a customer support system. Your only job is to delegate tasks to your sub-agents."
            "Do NOT attempt to answer questions yourself. Analyze the user's intent and invoke the correct agent's tool."
            " - For order inquiries or cancellations -> OrderStatusAgent"
            " - For product returns or return eligibility -> ReturnsSpecialistAgent"
            " - For payments, refunds, invoices -> BillingAgent"
            " - For bugs, technical problems -> TechnicalIssueEscalationAgent"
            " - For greetings or other questions -> GeneralSupportAgent"
        ),
        # Returns Specialist is integrated as a sub-agent (Remote A2A)
        sub_agents=[
            order_status_agent, 
            billing_agent, 
            technical_agent, 
            general_support_agent,
            returns_remote_agent
        ]
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
        "How much was I charged for order b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b12? I need to verify my invoice.", # Billing (MCP)
        "I want to return my order b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b12. Please initiate it.",               # Returns (A2A)
        "My support portal is showing a '500 Internal Server Error' whenever I log in. Escalating this."     # Escalation (Local)
    ]

    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_router, 
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
