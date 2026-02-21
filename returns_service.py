import os
import datetime
import psycopg2
from dotenv import load_dotenv
from google.adk.agents import LlmAgent

load_dotenv()

def check_return_eligibility(order_id: str) -> str:
    """Checks if an order is eligible for return (must be within 30 days)."""
    db_url = os.environ.get("DATABASE_URL")
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Query the order
        cur.execute("SELECT created_at, order_status FROM orders WHERE id = %s", (order_id,))
        result = cur.fetchone()
        
        if not result:
            return f"Error: Order ID {order_id} not found."
            
        created_at, status = result
        if status == 'canceled' or status == 'returned':
            return f"Order is already {status} and cannot be returned."
            
        # Check date (30 days logic)
        days_diff = (datetime.datetime.now(datetime.timezone.utc) - created_at).days
        if days_diff <= 30:
            return f"Order {order_id} is eligible for return. It was placed {days_diff} days ago."
        else:
            return f"Order {order_id} is NOT eligible for return. It was placed {days_diff} days ago (limit is 30 days)."
            
    except Exception as e:
        return f"Database error: {str(e)}"
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

def initiate_return(order_id: str) -> str:
    """Initiates a return for a specific order by updating its status."""
    db_url = os.environ.get("DATABASE_URL")
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Verify eligibility first (simplified)
        cur.execute("SELECT order_status FROM orders WHERE id = %s", (order_id,))
        result = cur.fetchone()
        
        if not result:
            return f"Error: Order ID {order_id} not found."
        
        # Update the status
        cur.execute("UPDATE orders SET order_status = 'return_initiated' WHERE id = %s", (order_id,))
        conn.commit()
        
        return f"Successfully initiated return for Order {order_id}. Status set to 'return_initiated'."
            
    except Exception as e:
        return f"Database error: {str(e)}"
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

# Define the Returns Specialist Agent
returns_agent = LlmAgent(
    name="ReturnsSpecialistAgent",
    model="gemini-flash-latest",
    description="Specialist for checking return eligibility and processing returns.",
    instruction=(
        "You are the Returns Specialist. You handle all inquiries about returning products."
        "Use your tools to check if an order can be returned and to initiate the return process."
        "Always be clear about the 30-day policy if an order is rejected."
    ),
    tools=[check_return_eligibility, initiate_return]
)
