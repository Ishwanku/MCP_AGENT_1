"""
Tool Executor for the MCPAgent.

This module is responsible for translating a classified intent and the original query
into a specific tool call that can be processed by the `ClientManager`.
It maps intents to tool names and prepares the necessary arguments for the tool call.

For example, if the intent is 'save_memory' and the query is 
"Save a memory: I met with John today", this module will determine that the 
'save_memory' tool on the memory MCP server should be called with the content
"I met with John today".

It relies on the `ClientManager` to have the tools correctly mapped and to 
handle the actual dispatching of the call to the appropriate MCP server.
"""
import json
import os
from typing import Dict, Any, Optional, List, cast

from openai.types.chat import ChatCompletionMessageToolCall # For constructing tool call objects
from utils.client_manager import ClientManager # To dispatch the constructed tool call

def _extract_argument(query: str, prefixes: List[str], suffixes: Optional[List[str]] = None) -> str:
    """Helper function to extract the core argument from a query based on prefixes/suffixes."""
    content = query
    for prefix in prefixes:
        if content.lower().startswith(prefix.lower()):
            content = content[len(prefix):].strip()
            break # Stop after first prefix match
    if suffixes:
        for suffix in suffixes:
            if content.lower().endswith(suffix.lower()):
                content = content[:-len(suffix)].strip()
                break # Stop after first suffix match
    return content

async def execute_mcp_tool(query: str, intent: str, client_manager: ClientManager) -> Any:
    """
    Executes an MCP tool based on the classified intent and user query.

    This function constructs a tool call request that `ClientManager.process_tool_call`
    can understand and then invokes it.

    Args:
        query: The original user query string.
        intent: The classified intent (e.g., "save_memory", "readTasks").
        client_manager: The `ClientManager` instance responsible for calling tools.

    Returns:
        The result from the executed tool call, typically a string or structured data.
        Returns a message if no appropriate tool is matched to the intent.
    """
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None

    print(f"ToolExecutor: Preparing tool call for intent '{intent}' with query '{query}'")

    # Map intent to tool_name and prepare tool_input
    if intent == "save_memory":
        tool_name = "save_memory"
        tool_input = {"content": _extract_argument(query, ["Save a memory:", "Remember:"])}
    elif intent == "search_memories":
        tool_name = "search_memories"
        # Example: "Search for memories about Python conferences" -> query: "Python conferences"
        tool_input = {"query": _extract_argument(query, ["Search for memories about", "Search memories for", "Find memories about"])}
    elif intent == "get_all_memories":
        tool_name = "get_all_memories"
        tool_input = {} # No input needed for this tool
    elif intent == "readTasks":
        # Maps to the 'get_tasks' tool on the task server
        tool_name = "get_tasks" 
        tool_input = {} # No input needed
    elif intent == "newTask":
        # Maps to the 'add_new_task' tool (previously add_task) on the task server
        tool_name = "add_new_task" 
        tool_input = {"task": _extract_argument(query, ["Add a task:", "New task:", "Create task:"])}
    elif intent == "markTaskAsDone":
        # Maps to the 'complete_task' tool (previously mark_task_as_done) on the task server
        tool_name = "complete_task" 
        tool_input = {"task": _extract_argument(query, ["Mark task", "Complete task:"], ["as done", "as completed"])}
    elif intent == "getEvents":
        tool_name = "get_events"
        tool_input = {} # No input needed currently
    else:
        print(f"ToolExecutor: Intent '{intent}' does not map to a known tool.")
        return "No specific tool action was identified for your query."

    # By this point, if the code hasn't returned, tool_name and tool_input are set.
    # The previous 'if tool_name and tool_input is not None:' is always true here.
    print(f"ToolExecutor: Mapped to tool '{tool_name}' with input: {tool_input}")
    
    # Construct the tool call object in the format ClientManager expects
    # (similar to OpenAI's ChatCompletionMessageToolCall)
    # We use `cast` here because we are constructing a dict that matches the TypedDict structure.
    tool_call_request = cast(ChatCompletionMessageToolCall, {
        "id": "tool_call_" + tool_name + "_" + os.urandom(4).hex(), # Generate a unique ID for the call
        "type": "function",
        "function": {
            "name": tool_name,
            "arguments": json.dumps(tool_input) # Arguments must be a JSON string
        }
    })
    
    # Use ClientManager to process this single tool call
    # ClientManager.process_tool_call expects a list of tool calls
    results = await client_manager.process_tool_call([tool_call_request])
    
    if results: # process_tool_call returns a list of results
        print(f"ToolExecutor: Result from tool '{tool_name}': {results[0]}")
        return results[0] # Return the first (and only) result
    else:
        print(f"ToolExecutor: Tool '{tool_name}' executed but returned no result.")
        return f"Tool '{tool_name}' executed but no specific result was returned."
