# -*- coding: utf-8 -*-
"""
CrewAI agent với Datask tools.
Multi-agent team để research và summarize web content.

Requires:
  pip install crewai
  DATASK_API_KEY=dtsk_live_...
  OPENAI_API_KEY=sk-...
"""
from crewai import Agent, Crew, Task
from crewai.tools import tool

import datask

_client = datask.Client()


@tool("fetch_web_page")
def fetch_web_page(url: str) -> str:
    """Fetch the content of a web page as Markdown text. Input: URL string."""
    return _client.fetch(url)


@tool("extract_web_data")
def extract_web_data(url_and_prompt: str) -> str:
    """
    Extract structured data from a web page.
    Input format: 'URL | PROMPT'
    Example: 'https://shop.com/product | extract product name, price, availability'
    """
    import json
    parts = url_and_prompt.split("|", 1)
    if len(parts) != 2:
        return "Error: input must be 'URL | PROMPT'"
    url, prompt = parts[0].strip(), parts[1].strip()
    data = _client.extract(url, prompt=prompt)
    return json.dumps(data, indent=2)


researcher = Agent(
    role="Web Researcher",
    goal="Gather accurate information from web sources using Datask",
    backstory="Expert at navigating and extracting data from complex websites.",
    tools=[fetch_web_page, extract_web_data],
    verbose=True,
)

analyst = Agent(
    role="Data Analyst",
    goal="Analyze and summarize data gathered by the researcher",
    backstory="Expert at synthesizing information into clear, actionable insights.",
    verbose=True,
)

research_task = Task(
    description="Fetch and extract the top 5 stories from Hacker News (https://news.ycombinator.com). Get titles and point counts.",
    expected_output="A structured list of the top 5 HN stories with their titles and points.",
    agent=researcher,
)

analysis_task = Task(
    description="Analyze the HN stories fetched by the researcher. What topics are trending? What does this tell us about the tech community today?",
    expected_output="A 2-3 paragraph analysis of current tech trends based on HN data.",
    agent=analyst,
    context=[research_task],
)

crew = Crew(
    agents=[researcher, analyst],
    tasks=[research_task, analysis_task],
    verbose=True,
)

if __name__ == "__main__":
    result = crew.kickoff()
    print("\n=== Crew Result ===")
    print(result)
