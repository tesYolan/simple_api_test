# this is a gradio app that allows to chat with multiple openai assistants so that they can enable a chatbot
# to be used in a program ideation stage. 

import gradio as gr
from openai import OpenAI
import pandas as pd

# gets API Key from environment variable openai .env file

with open(".env") as f:
    api_key = f.read().strip()

client = OpenAI(api_key=api_key)
def get_assistant(name):
    return client.beta.assistants.retrieve(name)


assistants = {'@tech': 'asst_j66ZdbapEwQd5WBjHuW7dCqG', 
              '@design': 'asst_e46hmiot1roakseFZnw1mByP', 
              '@manager': 'asst_o5xuIIANLSDc58geczMY94Qx'
              }

colors = {'@tech': 'blue', '@design':'pink', '@manager': 'green'}

fetched_assistants = {key: get_assistant(value) for key, value in assistants.items()}

thread = client.beta.threads.create()

def get_message_content(message):
    content_block = message.content[0]

    # Get the text from the content block
    text = content_block.text

    # Get the value from the text
    value = text.value

    return value

def message_hander(message, history):
    # message has a @tech @design @manager at the beginning followed up the request. 
    # the request is aptly parsed and correct feteched_assistant is asked. 
    # the message format is @tech what do you think?

    assistant_name = message.split(' ')[0]

    assistant = fetched_assistants[assistant_name]

    message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=' '.join(message.split(' ')[1:])
            )

    run=client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, 
        assistant_id=assistant.id,
        instructions="Be succint and to the point in the conversation"
    )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        print(messages)
    else:
        print("in progress...")

    # return string from messages

    

    result = messages.data[0].content[0].text.value

    # add span for the result in text. 
    # add span for the assistant name in text.
    result = f"<span style='color:{colors[assistant_name]}'>{result}</span>"

    return result

def clear_status():
    global thread

    thread = client.beta.threads.create()

    # call chat






    
CSS ="""
.contain { display: flex; flex-direction: column; }
#component-0 { height: 100%; }
#chatbot { flex-grow: 1; }
"""
with gr.Blocks(css=CSS) as demo:
    with gr.Column():

        cbot = gr.Chatbot(
            height=700, render=False, render_markdown=True,
        )
        chat = gr.ChatInterface(fn=message_hander, chatbot=cbot, title='Chat Convo')

    # add button to clear

    with gr.Row():
        button = gr.Button("Use this instead Clear")

        button.click(clear_status)
        gr.Markdown("""
                    
                    We have definied the following assistants:
                    @tech: A technical assistant that can answer technical questions.
                    @design: A design assistant that can answer design questions.
                    @manager: A manager assistant that can answer managerial questions.

                    They could be defined in code or can be found here https://platform.openai.com/playground/assistants?assistant=asst_e46hmiot1roakseFZnw1mByP

                    To use them type first `@tech` or `@design` or `@manager` followed by space your question. That is

                    ```
                    @design what do you think i should do for fun tv stand. 
                    ```

                    to clear, clear the chat and also press the 'use this instead clear'

                    

                    """
                    )
        save_btn = gr.Button("Save")

        def save_btn_fn(chat_history):

            # make sure the name isn't overwriting something. 
            import random

            filename = "chat_history" + str(random.randint(0, 1000)) + ".txt"

            df = pd.DataFrame(chat_history)

            df.to_csv(filename, index=False)


        save_btn.click(save_btn_fn, cbot)

if __name__ == "__main__":

    demo.queue().launch()