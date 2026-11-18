from openai import OpenAI
from dotenv import load_dotenv
import json
import pandas as pd

load_dotenv()

client = OpenAI()

response = client.chat.completions.create(
  model="gpt-6.1-terra",
  response_format={ "type": "json_object" },
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Give me 10 ideas for a YouTube channel about Python, please provide the response in JSON. Provide a title and a description for every video, called 'title' and 'description' and store them in dictionary videos"},
  ]
)

output = response.choices[0].message.content

output_json = json.loads(output)
videos = output_json['videos']

df = pd.DataFrame(videos)
df.to_excel("videos.xlsx")