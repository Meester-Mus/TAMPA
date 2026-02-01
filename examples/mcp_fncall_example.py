"""
Illustration of function-calling flow with a model.
This pseudocode demonstrates providing function schemas to the model, receiving a function_call,
executing the function server-side, and sending the result back to the model for final response generation.

NOTE: This is a minimal example. In production:
- Use proper OpenAI API client library (openai >= 1.0)
- Add error handling and retries
- Log function calls for audit
- Validate function arguments before execution
"""

import json
from src.mcp.function_schemas import FUNCTION_DEFINITIONS
from src.mcp.functions import compute_drhash, search_documents, request_human_review

# Map function names to their actual implementations
FUNCTION_MAP = {
    "compute_drhash": compute_drhash,
    "search_documents": search_documents,
    "request_human_review": request_human_review,
}

def call_model_with_functions(messages, functions=None, model="gpt-4"):
    """
    Pseudocode for calling OpenAI with function definitions.
    Replace with actual openai.ChatCompletion.create() call.
    """
    # In real code:
    # response = openai.ChatCompletion.create(
    #     model=model,
    #     messages=messages,
    #     functions=functions,
    #     function_call="auto"
    # )
    # return response
    print(f"[MOCK] Calling model={model} with {len(messages)} messages and {len(functions or [])} functions")
    return {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": "search_documents",
                    "arguments": json.dumps({"query": "TAMPA verification", "k": 2})
                }
            }
        }]
    }

def execute_function(function_name: str, arguments: dict):
    """Execute a function by name with given arguments."""
    if function_name not in FUNCTION_MAP:
        raise ValueError(f"Unknown function: {function_name}")
    func = FUNCTION_MAP[function_name]
    return func(**arguments)

def run_agent_loop():
    """
    Main agent loop demonstrating function calling:
    1. Send user query + function definitions to model
    2. Model responds with a function_call
    3. Execute the function server-side
    4. Send function result back to model
    5. Model generates final response using the function result
    """
    # Step 1: Initial user query
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to TAMPA document search and verification tools."},
        {"role": "user", "content": "Can you search for documents about TAMPA verification and compute their hash?"}
    ]
    
    print("=== Step 1: Sending initial query to model ===")
    response = call_model_with_functions(messages, functions=FUNCTION_DEFINITIONS)
    
    message = response["choices"][0]["message"]
    
    # Step 2: Check if model wants to call a function
    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        function_args = json.loads(message["function_call"]["arguments"])
        
        print(f"\n=== Step 2: Model requested function call ===")
        print(f"Function: {function_name}")
        print(f"Arguments: {json.dumps(function_args, indent=2)}")
        
        # Step 3: Execute the function
        print(f"\n=== Step 3: Executing {function_name} ===")
        try:
            function_result = execute_function(function_name, function_args)
            print(f"Result: {json.dumps(function_result, indent=2)}")
            
            # Step 4: Send function result back to model
            messages.append(message)  # Add assistant's function_call message
            messages.append({
                "role": "function",
                "name": function_name,
                "content": json.dumps(function_result)
            })
            
            print(f"\n=== Step 4: Sending function result back to model ===")
            final_response = call_model_with_functions(messages, functions=FUNCTION_DEFINITIONS)
            
            # Step 5: Model generates final response
            final_message = final_response["choices"][0]["message"]
            print(f"\n=== Step 5: Final model response ===")
            print(f"Assistant: {final_message.get('content', '[No content]')}")
            
        except Exception as e:
            print(f"Error executing function: {e}")
            # In production: send error back to model or handle gracefully
    else:
        # Model responded directly without function call
        print(f"\n=== Model response (no function call) ===")
        print(f"Assistant: {message.get('content')}")

if __name__ == "__main__":
    print("MCP Function-Calling Example")
    print("=" * 60)
    print("\nThis example demonstrates the function-calling workflow:")
    print("1. User query → Model")
    print("2. Model → Function call request")
    print("3. Server executes function")
    print("4. Function result → Model")
    print("5. Model → Final response to user\n")
    
    run_agent_loop()
    
    print("\n" + "=" * 60)
    print("Note: This is a stub/mock. Replace call_model_with_functions")
    print("with actual OpenAI API calls for production use.")
