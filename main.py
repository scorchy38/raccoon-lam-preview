import logging
import os

import gradio as gr
import requests
from dotenv import load_dotenv


def handle_chat_input(user_input, history):
    base_url = os.environ.get('BASE_URL')
    headers = {
        "secret-key": os.environ.get('API_KEY'),
        "user-id": "lam-preview-user",
        "platform": "iOS"
    }

    try:
        if user_input.lower().startswith("process task"):
            response = requests.get(
                base_url + "/tasks/process",
                headers=headers
            )
            response_data = response.json()
            message = response_data['message']
            return history + [("user", message)], ""
        else:
            body = {
                "query": user_input,
                "chat_history": []
            }
            response = requests.post(
                base_url + "/sdk/steps/get",
                json=body,
                headers=headers
            )
            response_data = response.json()
            answer = response_data['data']['answer']
            return history + [("user", user_input), ("LAM", answer)], ""
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logging.error(error_message)
        return history + [("system", error_message)], ""


def setup_gradio_interface():
    with gr.Blocks(theme='scorchy38/everything_light', title="Raccoon LAM Service") as interface:
        gr.Markdown("# Raccoon LAM Service - Component Interface")
        gr.Markdown("""
            <div style="background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <strong>Note:</strong> This preview does not have context of chat history and runs on weaker CPUs. Performance may be limited.
            </div>
        """)

        chat_history = gr.Chatbot(label="Conversation", placeholder="Type here...", height=450)

        example_messages = ["Check Order History", "Post a new tweet", "Add a new address"]

        input_text = gr.Textbox(label="Type your message here",
                                placeholder="Type 'process tasks' to initiate task processing or choose a prompt below...")

        with gr.Row():
            for msg in example_messages:
                gr.Button(msg, size="sm").click(
                    lambda x=msg: x,
                    inputs=[],
                    outputs=[input_text]
                )

        submit_button = gr.Button("Send")

        submit_button.click(
            handle_chat_input,
            inputs=[input_text, chat_history],
            outputs=[chat_history, input_text]
        )

    return interface


if __name__ == "__main__":
    load_dotenv()
    app = setup_gradio_interface()
    app.launch(show_api=False)
