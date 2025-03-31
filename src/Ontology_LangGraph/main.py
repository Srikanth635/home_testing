import os
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict, List, Any, TypedDict
from function_tools import OntologyTools
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
import operator
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
import dotenv
dotenv.load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


class SimpleInMemoryHistory(BaseChatMessageHistory):
    def __init__(self):
        self.messages: List[BaseMessage] = []

    def add_message(self, message: BaseMessage) -> None:
        self.messages.append(message)

    def clear(self) -> None:
        self.messages.clear()

    @property
    def messages(self) -> List[BaseMessage]:
        return self._messages

    @messages.setter
    def messages(self, value: List[BaseMessage]) -> None:
        self._messages = value

#Initialize Variables.
ontology_tools = OntologyTools("OWLs/SOMA.owl")
llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)

#State
class GraphState(TypedDict):
    messages: List[BaseMessage]
    intermediate_steps: List[Any]
    next: str

# Tools.
find_relevant_classes_tool = Tool.from_function(
    func=ontology_tools.find_relevant_classes,
    name="find_relevant_classes",
    description="Finds classes relevant to the user query."
)

calculator = Tool.from_function(
    func= lambda x,y: x*y,
    name="calculate",
    description="multiply two numbers"
)

tools = [find_relevant_classes_tool, calculator]

# Prompt.
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that uses provided tools to answer user questions."),
    ("user", "{input}"),
    ("assistant", "{tools}"),
])

# Agent.
agent = {
    "input": lambda x: x["messages"],
    "tools": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
    "messages": operator.itemgetter("messages")
} | prompt | llm.bind_tools(tools) | OpenAIToolsAgentOutputParser()

# Nodes.
def agent_node(state: GraphState):
    result = agent.invoke(state)
    return {"messages": [result], "intermediate_steps": [result]}

def tool_node(state: GraphState):
    tool_result = ontology_tools.find_relevant_classes(state["messages"][-1].content)
    return {"messages": state["messages"] + [tool_result], "intermediate_steps": [], "next": "agent"}


#Graph.
workflow = StateGraph(GraphState)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

workflow.set_entry_point("agent")
# chain = RunnableWithMessageHistory(workflow.compile(), get_session_history=get_session_history)

if __name__ == "__main__":
    input_content = input(f"Enter the input search keyword: ")
    inputs = {"messages": [HumanMessage(content=input_content)], "intermediate_steps": []}

    graph = workflow.compile()
    print(graph.get_graph().draw_ascii())
    print('-' * 20)
    print(f'prompt: {prompt}')
    # result = chain.invoke(inputs, config={"configurable": {"session_id": "<foo>"}})
    # result = graph.invoke(input=inputs)

    for output in graph.stream(inputs):
        for key, value in output.items():
            if isinstance(value, dict) and "messages" in value:
                for message in value["messages"]:
                    if isinstance(message, AIMessage):
                        print(f"Assistant Response: {message.content}")

    # print(result)