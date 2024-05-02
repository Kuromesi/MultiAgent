import abc
from threading import Lock
import uuid

class Conversation:
    def __init__(self, id: str=None) -> None:
        if not id:
            self.id = str(uuid.uuid4())
        else:
            self.id = id
        # define function of the ai 
        self.prefixes = []
        # ask ai
        self.messages = []

    def wrap_message(self, message: str, role="user") -> dict:
        return {
            "role": role,
            "content": message
        }
    
    def add_prefix(self, prefix: str) -> None:
        wrapped_prefix = self.wrap_message(prefix, role="system")
        self.prefixes.append(wrapped_prefix)

    def get_prefixes(self) -> list:
        return self.prefixes
    
    def reset_prefixes(self, prefixes=[]) -> None:
        self.prefixes = prefixes

    def add_message(self, message: str) -> None:
        wrapped_message = self.wrap_message(message)
        self.messages.append(wrapped_message)
    
    def get_messages(self) -> list:
        return self.messages

    def reset_messages(self, messages: list=[]) -> None:
        self.messages = messages

    def get_entire_conversation(self) -> str:
        return self.prefixes + self.messages
    
class ConversationMap:
    def __init__(self) -> None:
        self.conversations: dict[str, Conversation] = {}
        self.lock = Lock()
    
    def add_conversation(self, conversation: Conversation) -> None:
        with self.lock:
            self.conversations[conversation.id] = conversation
        self.lock.release()

    def get_conversation(self, id: str) -> Conversation:
        with self.lock:
            conversation = self.conversations[id]
        return conversation

    def remove_conversation(self, id: str) -> None:
        with self.lock:
            del self.conversations[id]

class ChatAI:

    @abc.abstractmethod
    def ask(self, conversation: Conversation) -> str:
        pass