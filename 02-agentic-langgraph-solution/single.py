from langgraph.graph import StateGraph, START, END

# This where where my own code imports start
from graph_state import GraphState
from custom_prompts import get_intent, handle_generic


def handle_product(state: GraphState):
    answer = "What product do you want to buy?"
    state["answer"] = answer
    return state


workflow = StateGraph(GraphState)
workflow.add_node("intent", get_intent)
workflow.add_node("handle_product", handle_product)
workflow.add_node("handle_generic", handle_generic)

workflow.add_conditional_edges(
    "intent",
    lambda state: {
        "product": "handle_product",
        "general": "handle_generic",
    }.get(state["user_intent"], END),
)

workflow.add_edge(START, "intent")
workflow.add_edge("intent", END)

app = workflow.compile()

initial_state = {"question": "How are you doing today?", "answer": ""}
result = app.invoke(initial_state)
print(result)
