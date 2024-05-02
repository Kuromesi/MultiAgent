import os, requests, json
from chatai.chatai import ChatAI, Conversation
from utils.logger import logger
from utils.string import filter_string

class OpenapiAI(ChatAI):
    def __init__(self) -> None:
        self.url = os.getenv("API_URL")
        self.model = os.getenv("API_MODEL")
        self.api_key = os.getenv("API_KEY")
        
    def ask(self, conversation: Conversation) -> str:
        data = {
            "model": self.model,
            "messages": conversation.get_entire_conversation(),
            "stream": False
        }
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.api_key}'}
        response = requests.post(self.url, json.dumps(data), headers=headers)
        status_code = response.status_code
        response = response.json()
        logger.debug(f"response received: {response}")
        if status_code == 200:
            return filter_string(response["choices"][0]["message"]["content"])
        else:
            raise Exception(f"failed to request model {self.model} at {self.url}: {response.content}")