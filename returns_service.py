import os
import datetime
import psycopg2
import uuid
from dotenv import load_dotenv
from google.adk.agents import LlmAgent

load_dotenv()

def validate_order_id(order_id: str) -> bool:
    """Strictly validates if the string is a valid UUID."""
    try:
        uuid.UUID(str(order_id))
        return True
    except ValueError:
        return False

def check_return_eligibility(order_id: str) -> str:
    """Checks if an order is eligible for return (must be within 30 days)."""
    if not validate_order_id(order_id):
        return f"Error: '{order_id}' is not a valid Order UUID format."

    db_url = os.environ.get("DATABASE_URL")
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Query the order
        try:
            cur.execute("SELECT created_at, order_status FROM orders WHERE id = %s", (order_id,))
            result = cur.fetchone()
        except psycopg2.Error as e:
            return f"Error: Invalid Order ID format or database syntax error. ({str(e)})"
        
        if not result:
            return f"Error: Order ID {order_id} not found."
            
        created_at, status = result
        if status in ['canceled', 'returned', 'return_initiated']:
            return f"Order is already {status} and cannot be processed for a new return."
            
        # Check date (30 days logic)
        days_diff = (datetime.datetime.now(datetime.timezone.utc) - created_at).days
        if days_diff <= 30:
            return f"Order {order_id} is eligible for return. It was placed {days_diff} days ago."
        else:
            return f"Order {order_id} is NOT eligible. It was placed {days_diff} days ago (limit is 30 days)."
            
    except Exception as e:
        return f"Database connection error: {str(e)}"
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

def initiate_return(order_id: str) -> str:
    """Initiates a return for a specific order by updating its status."""
    # Defensive Check: Basic UUID validation
    if len(order_id) < 30:
        return f"Error: '{order_id}' does not look like a valid Order ID."

    db_url = os.environ.get("DATABASE_URL")
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Verify eligibility and current status before updating (Race condition prevention)
        cur.execute("SELECT created_at, order_status FROM orders WHERE id = %s", (order_id,))
        result = cur.fetchone()
        
        if not result:
            return f"Error: Order ID {order_id} not found."
        
        created_at, status = result

        # Re-check policy even if caller didn't check eligibility tool first
        days_diff = (datetime.datetime.now(datetime.timezone.utc) - created_at).days
        if days_diff > 30:
            return f"Error: Cannot initiate return. Order is {days_diff} days old (30-day limit)."

        if status in ['canceled', 'returned', 'return_initiated']:
            return f"Error: Cannot initiate return. Current order status is '{status}'."
        
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
