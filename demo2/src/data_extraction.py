def dummy_function(body):
    # This is a placeholder for actual data extraction logic
    # Simulate extraction of data
    return {
        "network upgrades": "Sample upgrade details",
        "change IDs": "Sample change ID",
        "device statuses": "Sample device status",
    }

# Example: Creating an agent with all attributes
from crewai import Agent, LLM, Task, Crew # type: ignore
from email_monitor import fetch_email_with_subject
from dotenv import load_dotenv
import os

load_dotenv()
model_name = os.getenv('OPENAI_MODEL_NAME')
api_key = os.getenv('OPENAI_API_KEY')
llm = LLM(
    model=model_name,
    api_key=api_key
)
network_engineer_agent = Agent(
  role='Senior Network Engineer',
  goal='Extract actionable insights',
  backstory="""You regularly extract text from emails with critical information like network upgrades, change IDs, and device statuses.""",
  tools=[fetch_email_with_subject],  # Optional, defaults to an empty list
  llm=llm,  # Optional
  verbose=True,  # Optional
  allow_delegation=False,  # Optional
)

information_extraction_task = Task(
    description='Find and extract text from emails with critical information like network upgrades, change IDs, and device statuses.',
    agent=network_engineer_agent,
    expected_output='Network Upgrades AND/OR Change IDs, AND/OR Device Statuses'
)

crew = Crew(
    agents=[network_engineer_agent],
    tasks=[information_extraction_task],
    verbose=True
)

result = crew.kickoff()

print(f"""
      Tasks completed!
      Task: {information_extraction_task.output.description}
Output: {information_extraction_task.output.raw}
      """)