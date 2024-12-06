# Doctor-Assistant

## Tool Comparison Table
| Name  | Supports RAG | Workflow | Customizable | Available Models | Has Agent | API Access | Cost |
|-----|-----|-----|-----|-----|-----|-----|-----|
| [Langflow](https://www.langflow.org/) | Yes | Yes | Yes | HuggingFace, Ollama, OpenAI, etc. | Yes | Yes | Free |
| [Flowise](https://flowiseai.com/) | Yes | Yes | Yes | Open source LLMs | Yes | Yes | $35/month |
| [Dify](https://dify.ai/) | Yes (Paid) | Yes | Yes (Paid) | HuggingFace, Ollama, OpenAI, etc. | Yes | Yes | Free or $59/month |

## Example Project Using Langflow

### Deployment Steps
Follow these steps to deploy this application:
1. Run Langflow Locally:
   - Modify the `BASE_API_URL` in the code to point to where Langflow is running (e.g., `http://127.0.0.1:7861`).
   - Find the Flow ID from the API section of the Langflow project and enter it into the `FLOW_ID` variable in the code.
   - Make sure the vector store database is not hibernated.

2. Get LINE Bot Access Token and Secret:
   - In [LINE Developers](https://developers.line.biz/zh-hant/), find the LINE Bot's access token and secret, and enter them into the code.

3. Run the Python Application:
   ```sh
   python3 Linebot.py
   ```

4. Start Ngrok for Port Forwarding:
   - Use the URL output from running the Python application (e.g., `Running on http://127.0.0.1:5000/`) to determine the correct local address for Ngrok.

   ```sh
   ngrok http http://127.0.0.1:5000
   ```

5. Modify LINE Webhook Settings:
   - Go to [LINE Developers](https://developers.line.biz/zh-hant/), and change the Webhook URL to the forwarding URL provided by Ngrok.

6. Complete Deployment:
   - Once everything is set up, you can start testing the LINE Chatbot.

### The code

```python=
from flask import Flask, request
import json
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import argparse
from argparse import RawTextHelpFormatter
import requests
from typing import Optional
import warnings
try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

BASE_API_URL = ""
FLOW_ID = ""
ENDPOINT = "" # You can set a specific endpoint name in the flow settings
ACCESS_TOKEN = ''
SECRET = ''

# You can tweak the flow by adding a tweaks dictionary
# e.g {"OpenAI-XXXXX": {"model_name": "gpt-4"}}
TWEAKS = {
  "OpenAIModel-B7GZz": {},
  "ChatOutput-N7iNQ": {},
  "Prompt-DFhHR": {},
  "AstraDB-qT5xK": {},
  "OpenAIEmbeddings-iCPPi": {},
  "SplitText-jpVvF": {},
  "OpenAIEmbeddings-2PiRR": {},
  "File-HM7qi": {},
  "Directory-jQLUz": {},
  "ParseData-vyP2a": {},
  "TextInput-AZCYl": {},
  "AstraDB-ZrJPa": {},
  "ChatInput-FYbX9": {}
}


app = Flask(__name__)
@app.route("/", methods=['POST'])


def linebot():
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        line_bot_api = LineBotApi(ACCESS_TOKEN)
        handler = WebhookHandler(SECRET)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        tk = json_data['events'][0]['replyToken']
        type = json_data['events'][0]['message']['type']
        if type=='text':
            msg = json_data['events'][0]['message']['text']
            reply = combineLangflowAndLine(msg)
        else:
            reply = ' '
        line_bot_api.reply_message(tk,TextSendMessage(reply))
    except:
        print(body)
    return 'OK'


def run_flow(message: str,
  endpoint: str,
  output_type: str = "chat",
  input_type: str = "chat",
  tweaks: Optional[dict] = None,
  api_key: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if api_key:
        headers = {"x-api-key": api_key}
    response = requests.post(api_url, json=payload, headers=headers)
    response_data = response.json()
    try:
        output_text = response_data['outputs'][0]['outputs'][0]['results']['message']['data']['text']
    except (KeyError, IndexError) as e:
        output_text = "Failed to extract output text from response."
    return output_text


def combineLangflowAndLine(userInput: str):
    parser = argparse.ArgumentParser(description="""Run a flow with a given message and optional tweaks.
Run it like: python <your file>.py "your message here" --endpoint "your_endpoint" --tweaks '{"key": "value"}'""",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument("--endpoint", type=str, default=ENDPOINT or FLOW_ID, help="The ID or the endpoint name of the flow")
    parser.add_argument("--tweaks", type=str, help="JSON string representing the tweaks to customize the flow", default=json.dumps(TWEAKS))
    parser.add_argument("--api_key", type=str, help="API key for authentication", default=None)
    parser.add_argument("--output_type", type=str, default="chat", help="The output type")
    parser.add_argument("--input_type", type=str, default="chat", help="The input type")
    parser.add_argument("--upload_file", type=str, help="Path to the file to upload", default=None)
    parser.add_argument("--components", type=str, help="Components to upload the file to", default=None)

    args = parser.parse_args()
    try:
      tweaks = json.loads(args.tweaks)
    except json.JSONDecodeError:
      raise ValueError("Invalid tweaks JSON string")

    if args.upload_file:
        if not upload_file:
            raise ImportError("Langflow is not installed. Please install it to use the upload_file function.")
        elif not args.components:
            raise ValueError("You need to provide the components to upload the file to.")
        tweaks = upload_file(file_path=args.upload_file, host=BASE_API_URL, flow_id=args.endpoint, components=[args.components], tweaks=tweaks)

    response = run_flow(
        message=userInput,
        endpoint=args.endpoint,
        output_type=args.output_type,
        input_type=args.input_type,
        tweaks=tweaks,
        api_key=args.api_key
    )
    return response


if __name__ == "__main__":
    app.run()

```
