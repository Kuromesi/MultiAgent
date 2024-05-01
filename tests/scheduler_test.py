import os, sys, dotenv
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR))
dotenv.load_dotenv("envs/ollama.env")

from scheduler.scheduler import Scheduler
from scheduler.schedule_context import ScheduleContext
from chatai.chatai import OllamaAI
from agent.task import Result, Task
from agent.agent import Agent

class FakeAgentWithGranted(Agent):
    def __init__(self, name: str, description: str, usage: str) -> None:
        super().__init__(name, description, usage)

    def execute(self, task: Task) -> Result:
        result = Result()
        result.granted("granted")
        return result
    
class FakeAgentWithDenied(Agent):
    def __init__(self, name: str, description: str, usage: str) -> None:
        super().__init__(name, description, usage)

    def execute(self, task: Task) -> Result:
        result = Result()
        result.denied("denied")
        return result
    
class FakeAgentWithInsufficient(Agent):
    def __init__(self, name: str, description: str, usage: str) -> None:
        super().__init__(name, description,usage)

    def execute(self, task: Task) -> Result:
        result = Result()
        result.insufficient("need host ip")
        return result
    
class FakeAgentWithFailed(Agent):
    def __init__(self, name: str, description: str, usage: str) -> None:
        super().__init__(name, description,usage)

    def execute(self, task: Task) -> Result:
        result = Result()
        result.failed("failed to execute")
        return result

ai = OllamaAI()
scheduler = Scheduler(ai)
# scheduler.register_agent(FakeAgentWithGranted("nmap", "scanning hosts", ""))
scheduler.register_agent(Agent("chatbinary", "decompiling binaries and analyze the source code of it", ""))
scheduler.register_agent(Agent("mhddos", "making DDOS attacks", ""))

def test_scheduler_denied():
    task = Task(target="sql injection")
    context = scheduler.new_schedule_context(task)
    result = scheduler.schedule(context)
    print(result)

def test_schedule_granted():
    scheduler.register_agent(FakeAgentWithGranted("nmap", "scanning hosts", ""))
    task = Task(target="scan host 172.22.164.35")
    context = scheduler.new_schedule_context(task)
    result = scheduler.schedule(context)
    print(result)

def test_schedule_agent_denied():
    scheduler.register_agent(FakeAgentWithDenied("nmap", "scanning open ports of a host", ""))
    task = Task(target="scan host 172.22.164.35")
    context = scheduler.new_schedule_context(task)
    result = scheduler.schedule(context)
    print(result)

def test_schedule_agent_insufficient():
    scheduler.register_agent(FakeAgentWithInsufficient("nmap", "scanning hosts", ""))
    task = Task(target="scan host 172.22.164.35")
    context = scheduler.new_schedule_context(task)
    result = scheduler.schedule(context)
    print(result)

def test_schedule_agent_failed():
    scheduler.register_agent(FakeAgentWithFailed("nmap", "scanning hosts", ""))
    task = Task(target="scan host 172.22.164.35")
    context = scheduler.new_schedule_context(task)
    result = scheduler.schedule(context)
    print(result)

def test_schedule_agent_succeed_retry():
    scheduler.register_agent(FakeAgentWithFailed("nmap", "scanning open ports", ""))
    scheduler.register_agent(FakeAgentWithGranted("nmap2", "scanning hosts", ""))
    task = Task(target="scanning open ports of a host")
    context = scheduler.new_schedule_context(task)
    result = scheduler.schedule(context)
    print(result)

if __name__ == "__main__":
    # test_scheduler_denied()
    # test_schedule_granted()
    # test_schedule_agent_denied()
    # test_schedule_agent_insufficient()
    # test_schedule_agent_failed()
    test_schedule_agent_succeed_retry()