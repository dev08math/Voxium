from openai import OpenAI

client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key="AIzaSyAwOqT1NUZNJA_e7fQSR7a4X_gAYIhliGw",
)

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[{"role": "user", "content": "Say hello in one word."}],
)

print(response.choices[0].message.content)