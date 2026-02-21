import uvicorn
from returns_service import returns_agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Convert the Returns Agent into an A2A-compliant Starlette application
app = to_a2a(returns_agent, host="localhost", port=8001)

if __name__ == "__main__":
    print("Starting Returns A2A Service on http://localhost:8001...")
    uvicorn.run(app, host="localhost", port=8001)
