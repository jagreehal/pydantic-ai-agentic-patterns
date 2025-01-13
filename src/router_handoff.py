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
    response: str = Field(description="Response to the customer")
    target_agent: Optional[str] = Field(description="Agent to hand over to", default=None)


# --- Agents ---
triage_agent = Agent(
    model="groq:llama-3.3-70b-versatile",
    deps_type=AgentDependencies,
    result_type=AgentResult,
    system_prompt="""
        You are a triage agent. Identify if a query should be routed to 'billing' or 'tech_support'.
        For billing issues, set `target_agent` to 'billing'.
        For technical issues, set `target_agent` to 'tech_support'.
    """,
)

billing_agent = Agent(
    model="groq:llama-3.3-70b-versatile",
    deps_type=AgentDependencies,
    result_type=AgentResult,
    system_prompt="""
        You are a billing agent. Handle queries about payments and invoices.
    """,
)

tech_support_agent = Agent(
    model="groq:llama-3.3-70b-versatile",
    deps_type=AgentDependencies,
    result_type=AgentResult,
    system_prompt="""
        You are a tech support agent. Handle queries about technical issues.
    """,
)


# --- Router ---
class AgentRouter:
    def __init__(self):
        self.agents = {
            "triage": triage_agent,
            "billing": billing_agent,
            "tech_support": tech_support_agent,
        }

    async def handle_query(self, prompt: str, deps: AgentDependencies) -> str:
        # Start with the triage agent
        current_agent = self.agents.get("triage", triage_agent)

        while True:
            # Run the current agent
            result = await current_agent.run(prompt, deps=deps)

            # Handle the result based on its type
            if result.data.target_agent:
                print(f"Handing over to {result.data.target_agent}")
                current_agent = self.agents[result.data.target_agent]
                continue

            # No handover needed, return response
            return result.data.response


if __name__ == "__main__":

    async def main():
        deps = AgentDependencies(user_id="user_123")
        router = AgentRouter()

        print("Welcome to the Support System!")
        print("Type 'quit' or 'exit' to end the session.")

        while True:
            # Get user input
            prompt = input("\nWhat can I help you with today? ")

            if prompt.lower() in ["quit", "exit"]:
                print("Thank you for using our support system. Goodbye!")
                break

            if not prompt.strip():
                print("Please enter a valid query.")
                continue

            try:
                # Route the query through the agent router and get response
                response = await router.handle_query(prompt, deps)
                print("\nSupport Response:", response)

            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
                print("Please try again or contact system administrator.")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user. Goodbye!")
