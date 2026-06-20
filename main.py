import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors
import argparse
from prompts.prompts import system_prompt
from call_function import available_functions, call_function

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if api_key is None:
    raise RuntimeError("API key not found")

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

messages: list[types.Content] = [
    types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
]

client = genai.Client(api_key=api_key)

config = types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt
)


def generate_with_retry(client, model, contents, config, max_retries=5):
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model=model, contents=contents, config=config
            )
        except errors.ClientError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait = 60
                print(f"Rate limited, waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                raise
        except errors.ServerError as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"Server error, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise


MAX_ITERS = 20

for i in range(MAX_ITERS):
    response = generate_with_retry(client, "gemini-2.5-flash", messages, config)

    if args.verbose:
        usage = response.usage_metadata
        print(f"Prompt tokens: {usage.prompt_token_count}")
        print(f"Response tokens: {usage.candidates_token_count}")

    if response.candidates:
        for candidate in response.candidates:
            messages.append(candidate.content)

    if not response.function_calls:
        print("Final response:")
        print(response.text)
        break

    function_responses = []
    for function_call in response.function_calls:
        function_call_result = call_function(function_call, verbose=args.verbose)

        if not function_call_result.parts:
            raise Exception("Empty response parts from call_function")

        function_response = function_call_result.parts[0].function_response
        if function_response is None:
            raise Exception("No function_response in result")

        if function_response.response is None:
            raise Exception("No response field in function_response")

        if args.verbose:
            print(f"-> {function_response.response}")

        function_responses.append(function_call_result.parts[0])

    messages.append(types.Content(role="user", parts=function_responses))

else:
    print(f"Maximum iterations ({MAX_ITERS}) reached without a final response.")
    sys.exit(1)