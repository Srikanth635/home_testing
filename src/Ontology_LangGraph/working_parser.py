from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages.tool import tool_call, ToolMessage
from langgraph.graph import StateGraph, START, END
import json
from owlready2 import get_ontology, Ontology, ThingClass
from ontology_parser import *
from typing import Annotated, List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool, tool
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(),override=True)

# 1. Configuration
ONTOLOGY_FILE = "OWLs/SOMA.owl"
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.3

# 2. State Definition
class State(TypedDict):
    messages: Annotated[list, add_messages()]

# 3. Tools
@tool
def find_relevant_classes(query: str) -> List[Dict[str, Any]]:
    """
    Finds classes relevant to the user query.
    :param query: User query string.
    :return: List of relevant classes.
    """
    ontology = load_ontology(ONTOLOGY_FILE)
    class_details = extract_all_class_details(ontology)

    relevant_classes = ["srikanth"] #Remove hardcoded srikanth

    query_lower = query.lower()
    for class_detail in class_details:
        if query_lower in class_detail["name"].lower():
            relevant_classes.append(class_detail)
        else:
            for comment_value in class_detail["comment"]:
                if query_lower in str(comment_value).lower():
                    relevant_classes.append(class_detail)
    return relevant_classes

@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b."""
    return a * b

tools = [find_relevant_classes, multiply]

# 4. LLM and Tool Binding
llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
llm_with_tools = llm.bind_tools(tools)

# 5. Agent Node
def onto_agent(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# 6. Tool Node
class BasicToolNode:
    def __init__(self, tools: list):
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No Message found in input")

        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}

tool_node = BasicToolNode(tools=tools)

# 7. Routing Function
def route_tools(state: dict):
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END

# 8. Graph Construction
graph_builder = StateGraph(State)
graph_builder.add_node("agent", onto_agent)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("agent", route_tools, {"tools": "tools", END: END})
graph_builder.add_edge("tools", "agent")
graph_builder.add_edge(START, "agent")
graph = graph_builder.compile()

# 9. Stream Function
def stream_graph_updates(user_input: str):
    state = {"messages": [HumanMessage(content=user_input)]}
    for event in graph.stream(state):
        for node_output in event.values():
            if "messages" in node_output:
                messages = node_output["messages"]
                if messages:
                    last_message = messages[-1]

                    if isinstance(last_message, HumanMessage):
                        print(f"Human Message: {last_message.content}")
                    elif isinstance(last_message, AIMessage):
                        print(f"AI Message: {last_message.content}")
                        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                            for tool_call in last_message.tool_calls:
                                print(f"  Tool: {tool_call['name']}")
                                print(f"  Tool Args: {tool_call['args']}")
                                tool_results = tool_node({"messages": [last_message]})
                                tool_result_message = tool_results["messages"][-1]
                                if isinstance(tool_result_message, ToolMessage):
                                    print(f"  Tool Message: {tool_result_message.content}")
                    elif isinstance(last_message, ToolMessage):
                        print(f"Tool Message: {last_message.content}")

#10. Example Usage
stream_graph_updates("2 times 3 times 4")
# ans = graph.invoke({"messages" : [HumanMessage(content="navigating")]})
# # print(ans['messages'])
# for msg in ans['messages']:
#     print(msg)