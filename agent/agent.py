import abc

from agent.task import Task, Result
from utils.prompts import AGENT_REGISTER_PROMPT

class AgentInfo:
    def __init__(self, name: str, description: str, usage: str) -> None:
        self.name = name
        self.description = description
        self.usage = usage

class Agent:
    def __init__(self, name: str, description: str, usage: str) -> None:
        self.name = name
        self.description = description
        self.usage = usage

    @abc.abstractmethod
    def execute(self, task: Task) -> Result:
        pass

    def describe(self) -> AgentInfo:
        return AgentInfo(self.name, self.description, self.usage)
    
    def registration_prompt(self) -> str:
        prompt = AGENT_REGISTER_PROMPT.format(self.name, self.description)
        return prompt