import asyncio
from dataclasses import dataclass
from typing import Optional

import dotenv
import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent

logfire.configure(send_to_logfire="if-token-present")

dotenv.load_dotenv()


# --- Dependencies ---
@dataclass
class AgentDependencies:
    user_id: str


# --- Result Models ---
class AgentResult(BaseModel):
    response: str = Field(description="Response to the customer's query")
    next_agent: Optional[str] = Field(description="The next agent to hand off to", default=None)


# --- Agents ---
billing_agent = Agent(
    model="groq:llama-3.3-70b-versatile",
    deps_type=AgentDependencies,
    result_type=AgentResult,
    system_prompt="""
        You are a billing agent. Handle queries about payments and invoices.
        If the query is about a technical issue (e.g., service outages or errors), set `next_agent` to 'tech_support'.
    """,
)

tech_support_agent = Agent(
    model="groq:llama-3.3-70b-versatile",
    deps_type=AgentDependencies,
    result_type=AgentResult,
    system_prompt="""
        You are a tech support agent. Handle queries about technical issues.
        If the query is about billing (e.g., payments or charges), set `next_agent` to 'billing'.
    """,
)


# --- Example Function ---
async def agent_handoff(prompt: str, deps: AgentDependencies) -> str:
    # Start with the billing agent
    current_agent = billing_agent

    while True:
        # Run the current agent
        result = await current_agent.run(prompt, deps=deps)

        # Check if handoff is required
        if result.data.next_agent == "tech_support":
            print("\nHanding off to Tech Support...")
            current_agent = tech_support_agent
        elif result.data.next_agent == "billing":
            print("\nHanding off to Billing...")
            current_agent = billing_agent
        else:
            # No further handoff needed
            return result.data.response


# --- Main Execution ---
if __name__ == "__main__":

    async def main():
        # Define the dependencies
        deps = AgentDependencies(user_id="user_123")

        print("Welcome to the Support System!")
        print("Type 'quit' or 'exit' to end the session.")

        while True:
            prompt = input("\nWhat can I help you with today? ")

            if prompt.lower() in ["quit", "exit"]:
                print("Thank you for using our support system. Goodbye!")
                break

            if not prompt.strip():
                print("Please enter a valid query.")
                continue

            try:
                # Run the agent_handoff function and print the result
                response = await agent_handoff(prompt, deps)
                print("\nSupport Response:", response)

            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
                print("Please try again or contact system administrator.")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user. Goodbye!")
