# Example: Creating an agent with all attributes
from crewai import Agent, LLM, Task, Crew # type: ignore
from crewai_tools import JSONSearchTool # type: ignore
#from email_monitor import fetch_email_with_subject
from dotenv import load_dotenv
import os

load_dotenv()
model_name = os.getenv('OPENAI_MODEL_NAME')
api_key = os.getenv('OPENAI_API_KEY')

llm = LLM(
    model=model_name,
    api_key=api_key
)
search_tool = JSONSearchTool(json_path='./emails.json')
network_engineer_agent = Agent(
  role='Senior Network Engineer',
  goal='Extract critical network information from emails having subject \'Network Upgrade\', \'Change ID\' or \'Device Status\'',
  backstory="""You regularly extract text from emails with critical information like network upgrades, change IDs, and device statuses.""",
  tools=[search_tool],  # Optional, defaults to an empty list
  llm=llm,  # Optional
  verbose=True,  # Optional
  allow_delegation=False,  # Optional
)

information_extraction_task = Task(
    description='Find and extract text from emails with critical information like network upgrades, change IDs, and device statuses.',
    agent=network_engineer_agent,
    expected_output='1.Network Upgrades 2.Change IDs 3.Device Statuses'
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