# -*- coding: utf-8 -*-
"""
LangChain agent với Datask tools.
Agent có thể fetch và extract dữ liệu từ web.

Requires:
  pip install langchain langchain-openai
  DATASK_API_KEY=dtsk_live_...
  OPENAI_API_KEY=sk-...
"""
import os

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from datask.integrations.langchain import DataskExtractTool, DataskFetchTool

tools = [DataskFetchTool(), DataskExtractTool()]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

template = """You are a helpful research assistant with access to web data tools.

You have access to the following tools:
{tools}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

prompt = PromptTemplate.from_template(template)
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    result = agent_executor.invoke({
        "input": "What are the top stories on Hacker News right now? Get me their titles and point counts."
    })
    print("\n=== Final Answer ===")
    print(result["output"])
