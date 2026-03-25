"""LLM client for intent routing with tool calling."""

import json
import sys

import httpx
import config
from services import api_client

SYSTEM_PROMPT = """You are an LMS assistant bot. You help users explore lab data: scores, pass rates, timelines, groups, learners, and more.

You have tools to query the LMS backend. Use them to answer the user's question with real data. If the user's question requires data from multiple labs, call the relevant tool for each lab.

If the user sends a greeting, respond friendly and mention what you can do.
If the user sends gibberish or an unclear message, respond helpfully and list what you can do (e.g. "show scores for a lab", "list available labs", "find top students").
If the message is ambiguous (e.g. just "lab 4"), ask what they'd like to know about it.

Always respond concisely with formatted data. Use plain text, not markdown."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get the list of all labs and tasks in the LMS",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get the list of enrolled students and their groups",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution in 4 buckets (0-25, 26-50, 51-75, 76-100) for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return", "default": 5},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync to refresh data from the autochecker",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

# Map tool names to api_client functions
TOOL_DISPATCH = {
    "get_items": lambda args: api_client.get_items(),
    "get_learners": lambda args: api_client.get_learners(),
    "get_scores": lambda args: api_client.get_scores(args["lab"]),
    "get_pass_rates": lambda args: api_client.get_pass_rates(args["lab"]),
    "get_timeline": lambda args: api_client.get_timeline(args["lab"]),
    "get_groups": lambda args: api_client.get_groups(args["lab"]),
    "get_top_learners": lambda args: api_client.get_top_learners(args["lab"], args.get("limit", 5)),
    "get_completion_rate": lambda args: api_client.get_completion_rate(args["lab"]),
    "trigger_sync": lambda args: api_client.trigger_sync(),
}


def _call_llm(messages: list[dict]) -> dict:
    """Send messages to the LLM and return the response."""
    resp = httpx.post(
        f"{config.LLM_API_BASE_URL.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {config.LLM_API_KEY}"},
        json={
            "model": config.LLM_API_MODEL,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool call and return the result as a string."""
    func = TOOL_DISPATCH.get(name)
    if not func:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        result = func(arguments)
        return json.dumps(result, default=str)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def chat(user_message: str, max_rounds: int = 10) -> str:
    """Send a user message through the LLM with tool calling loop."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    for _ in range(max_rounds):
        try:
            response = _call_llm(messages)
        except httpx.ConnectError:
            return "LLM error: connection refused. Check that the LLM service is running."
        except httpx.HTTPStatusError as exc:
            return f"LLM error: HTTP {exc.response.status_code}. The LLM service may be down."
        except Exception as exc:
            return f"LLM error: {exc}"

        choice = response["choices"][0]
        message = choice["message"]

        # Add the assistant message to conversation
        messages.append(message)

        # If no tool calls, return the text response
        tool_calls = message.get("tool_calls")
        if not tool_calls:
            return message.get("content", "").strip() or "I couldn't generate a response."

        # Execute each tool call
        for tc in tool_calls:
            fn_name = tc["function"]["name"]
            try:
                fn_args = json.loads(tc["function"]["arguments"])
            except json.JSONDecodeError:
                fn_args = {}

            print(f"[tool] LLM called: {fn_name}({json.dumps(fn_args)})", file=sys.stderr)
            result = execute_tool(fn_name, fn_args)
            print(f"[tool] Result: {result[:100]}{'...' if len(result) > 100 else ''}", file=sys.stderr)

            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result,
            })

        print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)

    return "I ran out of steps trying to answer. Try a simpler question."
