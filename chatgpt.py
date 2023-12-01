from openai import OpenAI

# Function to simulate Jarvis-like interaction
def chat_with_jarvis(prompt):

    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key="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",
    )

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are Jarvis from ironman a helpful and knowledgeable yet sassy british assistant."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-3.5-turbo",
    )

    # Extract the message content from the response
    message_content = response.choices[0].message.content

    return message_content

print(chat_with_jarvis("hi jarvis"))

