import abc
import json
import os
from threading import Lock
import uuid
import requests
from utils.logger import logger

class Conversation:
    def __init__(self, id: str=None, messages: list=[]) -> None:
        if not id:
            self.id = str(uuid.uuid4())
        else:
            self.id = id
        self.messages = messages

    def wrap_message(self, message: str) -> dict:
        return {
            "role": "user",
            "content": message
        }
    
    def add_message(self, message: str) -> None:
        wrapped_message = self.wrap_message(message)
        self.messages.append(wrapped_message)
    
    def get_messages(self) -> list:
        return self.messages
    
    def get_last_message(self):
        return self.messages[-1]
    
class ConversationMap:
    def __init__(self) -> None:
        self.conversations: dict[str, Conversation] = {}
        self.lock = Lock()
    
    def add_conversation(self, conversation: Conversation) -> None:
        self.lock.acquire()
        self.conversations[conversation.id] = conversation
        self.lock.release()

    def get_conversation(self, id: str) -> Conversation:
        self.lock.acquire()
        conversation = self.conversations[id]
        self.lock.release()
        return conversation

    def remove_conversation(self, id: str) -> None:
        self.lock.acquire()
        del self.conversations[id]
        self.lock.release()

class ChatAI:
    conversations: list[Conversation]
    conversation_map: ConversationMap

    @abc.abstractmethod
    def ask(self, conversation: Conversation) -> str:
        pass
    
class OpenAI(ChatAI):
    def ask(self, conversation: Conversation) -> str:
        pass

class OllamaAI(ChatAI):
    def __init__(self) -> None:
        self.url = os.getenv("OLLAMA_URL")
        self.model = os.getenv("OLLAMA_MODEL")
        
    def ask(self, conversation: Conversation) -> str:
        data = {
            "model": self.model,
            "messages": conversation.get_messages(),
            "stream": False
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.url, json.dumps(data), headers=headers)
        status_code = response.status_code
        response = response.json()
        logger.info(f"response received: {response}")
        if status_code == 200:
            return response["message"]["content"]
        else:
            raise Exception(f"failed to request model {self.model} at {self.url}: {response.content}")

if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv("envs/ollama.env")
    ai = OllamaAI()
    conversation = Conversation()
    conversation.add_message("hello")
    print(ai.ask(conversation))