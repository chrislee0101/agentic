import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError
import argparse
from prompts import system_prompt
from call_functions import available_functions, call_function

load_dotenv()
api_key = os.environ.get('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)



def main():
    parser = argparse.ArgumentParser(description="Agentic Main Function")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    
    for _ in range(20):
        try:
            response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
            )
        except ClientError as e:
            print("Error: LLM request failed")
            if args.verbose:
                print(str(e))
            return
        
        # Add model outputs to conversation
        for candidate in response.candidates:
            messages.append(candidate.content)

        # Check for function calls
        function_calls = response.function_calls or []

        if not function_calls and response.text:
            print("Final response:")
            print(response.text)
            break

        tool_parts = []

        for function_call in function_calls:
            result_content = call_function(function_call, verbose=args.verbose)

            part = result_content.parts[0]
            if not part.function_response:
                raise RuntimeError("Invalid function response")

            tool_parts.append(part)

            if args.verbose:
                print(f"-> {part.function_response.response}")

        # Feed tool results back to the model
        if tool_parts:
            messages.append(
                types.Content(role="user", parts=tool_parts)
            )

    
    if response.usage_metadata is None:
        raise RuntimeError("API request failed: usage metadata is None")
    
    
    
    #print("Hello from agentic!")
    if args.verbose:
        print(f"User prompt: {args.user_prompt} ")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


if __name__ == "__main__":
    main()
