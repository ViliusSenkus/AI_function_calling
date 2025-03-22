from dotenv import load_dotenv
from openai import OpenAI
import os
from rich import print
import requests
import json

try:
    load_dotenv()
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.getenv('GITHUB_TOKEN'),
    )
    if client:
        print("Sėkmingai prisijungta Prie Github modelių.\n")
    else:
        print("Prisijungti prie Github modelių nepavyko.\n")
except Exception as e:
    print(f"Prisijungti prie Github modelių nepavyko. Klaida: {e}\n")

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current temperature for provided coordinates in celsius.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"}
            },
            "required": ["latitude", "longitude"],
            "additionalProperties": False
        },
        "strict": True
    }
}]

# messages = [{"role": "user", "content": "What's the weather like in Vilnius today?"}]
messages = [{"role": "user", "content": "What's the human temperature in Vilnius?"}]

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
)

print(completion.choices[0].message.tool_calls)

def get_weather(latitude, longitude):
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
    data = response.json()
    return data['current']['temperature_2m']
# part of data object    
    # {......
    # 'elevation': 111.0,
    # 'current_units': {
    #     'time': 'iso8601',
    #     'interval': 'seconds',
    #     'temperature_2m': '°C',
    #     'wind_speed_10m': 'km/h'
    # },
    # 'current': {'time': '2025-03-22T18:00', 'interval': 900, 'temperature_2m': 6.4, 'wind_speed_10m': 15.8},   
    # ....}
if completion.choices[0].message.tool_calls:
    tool_call = completion.choices[0].message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)

    result = get_weather(args["latitude"], args["longitude"])

    messages.append(completion.choices[0].message)  # append model's function call message
    messages.append({                               # append result message
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": str(result)
    })

    completion_2 = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )

    print(completion_2.choices[0].message.content)
else:
    print(completion.choices[0].message.content)


#PRACTICE and experiment, data here - https://platform.openai.com/docs/guides/function-calling?api-mode=chat&example=get-weather