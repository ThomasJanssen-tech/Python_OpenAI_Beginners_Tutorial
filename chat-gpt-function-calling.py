from openai import OpenAI
from dotenv import load_dotenv
import json
import pandas as pd
import sqlite3

load_dotenv()

client = OpenAI()

# --------------------------------------------------------------
# Define the actual function get_country_population
# --------------------------------------------------------------

def get_country_population(country_code):
    connection = sqlite3.connect('population_data.db')
    cursor = connection.cursor()

    input = [country_code]
    result = cursor.execute("SELECT `population` FROM population_data WHERE country_iso_code=?",input)

    population_result = result.fetchone()

    return population_result[0]

# --------------------------------------------------------------
# Provide the function as a tool
# --------------------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_country_population",
            "description": "Get the population for a specific country",
            "parameters": {
                "type": "object",
                "properties": {
                    "iso_country_code": {
                        "type": "string",
                        "description": "The 3-digit ISO code for a specific country",
                    },
                    "population": {"type": "integer"},
                },
                "required": ["iso_country_code"],
            },
        },
    }
]

# --------------------------------------------------------------
# Requesting and extracting the input parameters from Chat-GPT
# --------------------------------------------------------------

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Please give me the population of the Netherlands"},
  ]

response = client.chat.completions.create(
  model="gpt-6.1-terra",
  reasoning_effort="none",
  messages=messages,
  tools=tools,
  tool_choice="auto"
)

response_message = response.choices[0].message

tool_calls = response_message.tool_calls

if tool_calls:
    available_functions = {
        "get_country_population": get_country_population,
    }

    messages.append(response_message)

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(
            country_code=function_args.get("iso_country_code")
        )

# --------------------------------------------------------------
# Appending the function's output to the messages
# --------------------------------------------------------------

        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": str(function_response),
            }
        )


# --------------------------------------------------------------
# Calling Chat-GPT again and asking it to summarize the output
# --------------------------------------------------------------

    second_response = client.chat.completions.create(
        model="gpt-6.1-terra",
        messages=messages,
    )

    print(second_response.choices[0].message.content)