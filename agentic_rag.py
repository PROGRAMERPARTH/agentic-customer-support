# %% [markdown]
# Installing Packages 

# %%
#%pip install -r requirements.txt

# %% [markdown]
# Loading The Gemini API And The Model

# %%
import os
from dotenv import load_dotenv 
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("Gemini_Api_Key")
llm = ChatGoogleGenerativeAI(
    model='gemini-3.1-flash-lite',
    google_api_key=GOOGLE_API_KEY,
    temperature=0
)

# %% [markdown]
# Demo Orders Database

# %%
ORDERS_DB ={
    '12345':{'order_id':'12345','customer_email':'john.doe@example.com','items' : ['item1','item2'],'total_amount':100.0,'status':'shipped'},
    '12346':{'order_id':'12346','customer_email':'jane.smith@example.com','items' : ['item3','item4'],'total_amount':200.0,'status':'processing'}
}
# %% [markdown]
# Tool1 : Checks The Order Status 

# %%
from datetime import datetime
def check_order_status(order_id : str) -> dict:
    """Looks Up the Order by its Order ID"""

    order = ORDERS_DB.get(order_id)#if order is none what should we return?
    if order is None:
        return {
            "error":f"Order{order_id} does not found",
            "Source":"order_API"
        }
    return {
        "data": order ,
        "Source":"order_API",
        "timestamp": datetime.now().isoformat()
    }
    

# %% [markdown]
# Tool2: Refund Calculator

# %%
def calculate_refund(order_id : str) -> dict:
    """Calculates Refund Amount for the Order by its Order ID"""
    order = ORDERS_DB.get(order_id)
    if order is None:
        return {
            "error":f"Order{order_id} does not found",
            "Source":"refund_API"
        }
    # Assuming a simple refund policy of 10% of total amount
    refund_amount = order['total_amount'] * 0.1
    return {
        "data": {
            "order_id": order_id,
            "refund_amount": refund_amount
        },
        "Source":"refund_API",
        "timestamp": datetime.now().isoformat()
    }

# %% [markdown]
#                                 OR                         

# %%
def calculate_refund(order_id: str, reason: str) -> dict:
    """Calculate a potential refund using the demo return policy"""

    order = ORDERS_DB.get(order_id)

    if order is None:
        return {
            "error": "Order not found",
            "source": "refund_calculator"
        }
    reason = reason.lower().strip()
    if reason in ["damaged", "defective"]:
        fee = 0.0   
    elif reason in ["changed mind", "no longer needed"]:
        fee = order["total_amount"] * 0.1
    else:
        return {
            "error": "Invalid reason for return",
            "source": "refund_calculator"
        }    

    return {
    "data" : {
        "order_id": order_id,
        "original_amount": order["total_amount"],
        "restocking_fee": round(fee, 2),
        "refund_amount": round(
            order["total_amount"] - fee, 2
        ),
        "reason": reason
    },
    "source": "refund_calculator"
}


# %% [markdown]
# TOOl 3 : Process Return

# %%
def process_return(order_id: str, reason: str) -> dict:
    """check whether the return be initiated"""
    order = ORDERS_DB.get(order_id)
    if order is None:
        return {
            "error": "Order not found",
            "source": "return_API"
        }
    if order["status"] not in ["shipped", "delivered"]:
        return {
            "error": f"Return cannot be initiated for order with status '{order['status']}'",
            "source": "return_API"
        }  
    delivery_date = datetime.strptime(order["delivery_date"], "%Y-%m-%d") if "delivery_date" in order else datetime.now()  # Assuming the order was delivered today for demo purposes
    days_since_delivery = (datetime.now() - delivery_date).days
    if days_since_delivery > 30:
        return{
            "error": "Return period has expired",
            "source": "return_API",
            "policy": "Returns must be initiated within 30 days of delivery"
        }
    return {
        "data": {
            "order_id": order_id,
            "return_initiated": True,
            "reason": reason
        },
        "source": "return_API"
    }
    

# %% [markdown]
# Tool4 : Retrieve A Return Policy  

# %%
Policies = [
    {
        "policy_name": "Return Policy",
        "description": "Customers can return items within 30 days of delivery for a full refund or exchange.",
        "conditions": [
            "Items must be in original condition and packaging.",
            "Proof of purchase is required.",
            "Certain items may be non-returnable (e.g., perishable goods, personalized items)."
        ]
    },
    {
        "policy_name": "Refund Policy",
        "description": "Refunds will be processed within 5-7 business days after the returned item is received and inspected.",
        "conditions": [
            "Refunds will be issued to the original payment method.",
            "Shipping costs are non-refundable.",
            "Restocking fees may apply for certain items."
        ]
    }
]

def retrieve_policies(query: str) -> dict:
    """Retrieves the return and refund policies"""
    return {
        "data": {
            "query": query,
            "policies": Policies
        },

        "source": "Knowledge_Base"
    }

# %% [markdown]
# Convert The Functions Into Langchain Tool

# %%
from langchain_core.tools import StructuredTool
tools=[
    StructuredTool.from_function(check_order_status, name="check_order_status", description="Looks up the order by its Order ID"),
    StructuredTool.from_function(retrieve_policies, name="retrieve_policies", description="Retrieves the return and refund policies"),
    StructuredTool.from_function(calculate_refund, name="calculate_refund", description="Calculates the refund amount for a given order ID and reason"),
    StructuredTool.from_function(process_return, name="process_return", description="Processes a return request for a given order ID and reason")   
]
# %% [markdown]
# Createing A Agent State 

# %%
from typing import Any 
from typing_extensions import  NotRequired, TypedDict
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage

class AgentState(TypedDict):
    query: str
    messages: list[BaseMessage]
    tools_results: list[dict[str, Any]]
    sources: list[str]
    steps: int 
    max_steps: int 
    plan : NotRequired[dict[str, Any]]
    final_response: NotRequired[str]
    


# %% [markdown]
# Build Planner

# %%
#Plan
#Action
#tools
#tools arg
#reson for choosing the tool

from pydantic import BaseModel, Field
from typing import Literal

class Plan(BaseModel):
    """The Plan of the Agent"""
    action: Literal["tool", "final_response"] = Field(default="tool", description="The action to take: 'tool' to use a tool, 'final_response' to provide a final response")
    tool_name: str | None = Field(default=None, description="The name of the tool to use if action is 'tool'")
    tool_args: dict[str, Any] = Field(default_factory=dict, description="The arguments for the tool if action is 'tool'")
    reason_Summary: str | None = Field(default=None, description="The reason for choosing the tool or final response")

# %%
Planner_llm = llm.with_structured_output(Plan)

# %%
TOOL_NAMES = {tool.name for tool in tools}
def planner(state: AgentState) -> dict:
    prompt = f"""
You are an agent that can assist customers with their orders, returns, and refunds.
User question: {state['query']}
Previous tools results: {state['tools_results']}
Available tools: {', '.join(TOOL_NAMES)}
choose one of the Following actions:
1. Use a tool to gather more information or perform an action.
2. Provide a final response to the user based on the information available.
3. Never invent information. If you don't know the answer, say so.
4.Never use a tool that is not in the list of available tools.
"""
    plan = Planner_llm.invoke(prompt)
    if plan.action == "tool" and plan.tool_name not in TOOL_NAMES:
        return {
            "Final_response": f"Invalid tool name: {plan.tool_name}. Available tools are: {', '.join(TOOL_NAMES)}",
            "steps": state["max_steps"],
        }
    return {
        "messages": state["message"],
        "steps": state["steps"] + 1,
        "tool_result": state["tool_result"],
        "sources": state["sources"],
        "final_response":(
            plan.model_dump_json()
        )
    }    

# %% [markdown]
# Tool Executor

# %%
TOOL_MAP ={tool.name: tool for tool in tools }
def execute_tool(tool_name:str,tool_args: dict) -> dict :
    """
    Execute A Tool By Name with Provided Argument
    """
    tool = TOOL_MAP.get(tool_name)
    if tool is None:
        return{
            "error": f"Tool '{tool_name}' not found.",
            "source":"tool_executor"
        }
    try :
        result =tool.invoke(tool_args)
        return{
            "data":result,
            "source":tool_name
        }
    except Exception as e :
        return{
            "error":str(e),
            "source": tool_name
        }

# %% [markdown]
# Final Responder

# %%
from langchain_core.messages import HumanMessage,SystemMessage
def generate_final_Answer(query:str,tools_results: list[dict])-> str:
    """Generate A Final Answer Based On Query And Tool Results """
    evidence=[]
    sources =[]
    for result  in tools_results:
        source = result.get("source","unknown")
        evidence.append({
            "source": source,
            "result": result 
            })   
        if source not in sources:
            sources.append(source)
    response = llm.invoke([
        SystemMessage(content=(
            "Answer the user query based on the provided evidence and sources. If the evidence is insufficient, respond with 'I don't know'."
            "Do Not Invent Facts. Provide a concise and accurate answer."

        )),
        HumanMessage(content=(f"User Query: {query}\n"
                              f"Evidence: {evidence}\n"
                              f"Sources: {sources}"
        
        )),])
    return response.content

# %% [markdown]
# Connect Everything with Langraph

# %% [markdown]
# Planner Node

# %%
def plan_step(state: "AgentState") -> dict:
    """Plan one step in the agent's process."""
    plan = Planner_llm.invoke(f"""
You are an agent that assists customers with orders, returns, and refunds.

User question: {state["query"]}
Previous tool results: {state["tools_results"]}
Available tools: {", ".join(TOOL_NAMES)}

Select a tool if more information is needed, or choose final_response when
the available information is sufficient.
""")

    return {
        "plan": plan.model_dump(),
        "steps": state["steps"] + 1,
    }


# %% [markdown]
# tool Node

# %%
def run_tool(state: "AgentState") -> dict:
    plan = state["plan"]
    result = execute_tool(plan["tool_name"], plan["tool_args"])
    results = state["tools_results"]+ [result]
    sources = list(state["sources"])
    source = result.get("source","unknown")
    if source not in sources:
        sources.append(source)
    return{
        "tools_results": results,
        "sources": sources,
    }

# %%
def respond(state: "AgentState") -> dict:
    """Generate a final response based on the query and tool results."""
    final_response = generate_final_Answer(state["query"], state["tools_results"])
    return {
        "final_response": final_response,
        "steps": state["steps"] + 1,
    }

# %% [markdown]
# Flow Logic

# %%
from langgraph.graph import StateGraph, START , END 
def route_after_planning(state: "AgentState") -> str:
    """Determine the next step after planning."""
    plan = state.get("plan",{})

    if state["steps"] >= state["max_steps"]:
        return "respond"
    if plan.get("action") == "final_response":
        return "respond"
    if plan.get("action") == "tool" and plan.get("tool_name") in TOOL_NAMES:
        return "run_tool"
    return "respond"  # Default to respond if no valid action is determined

# %%
def build_agent():  
    builder = StateGraph(AgentState)
    builder.add_node("plan_step", plan_step)
    builder.add_node("run_tool", run_tool)
    builder.add_node("respond", respond)
    builder.add_edge(START, "plan_step")
    builder.add_conditional_edges("plan_step", route_after_planning, {"run_tool": "run_tool", "respond": "respond"})
    builder.add_edge("run_tool", "plan_step")
    builder.add_edge("respond", END)
    return builder.compile()


# %%
def ask_agent(query: str) -> str:
    """Run one customer-support request through a newly built agent."""
    agent = build_agent()
    result = agent.invoke({
        "query": query,
        "messages": [],
        "tools_results": [],
        "sources": [],
        "steps": 0,
        "max_steps": 10,
    })
    return result["final_response"]


