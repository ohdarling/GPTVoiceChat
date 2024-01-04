from openai import OpenAI
client = OpenAI()

def openai_api(message):
    print("call openai api")

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "你是一个语音聊天助手，请尽量以口语来回答问题，并且使内容尽量简短。"},
        {"role": "user", "content": message}
    ]
    )

    resp_msg = completion.choices[0].message.content
    print(resp_msg)
    return resp_msg

# openai_api("介绍一下你自己")