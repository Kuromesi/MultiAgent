import abc, re, json

from agent.agent import Agent
from chatai.chatai import ChatAI
from scheduler.schedule_context import ScheduleContext
from agent.task import Task, Result, is_denied, is_granted, is_insufficient, is_failed
from utils.logger import logger


JSON_REGEX = re.compile(r'\{.*\}')

SCHEDULER_PROMPT = """
You are a scheduler.
You are responsible for recording agents in a agent_list and deciding which agent should be used to complete a task.

If an agent-registration request is received, reply in the following json format:
{
    "succeeded": true or false,
    "message": "a message describing the result"
}
If the agent is not registered, add the agent to the agent_list, the succeeded field is true, and message field can be null.
If the agent is registered, then succeeded field is false, and message field is a message describing the result.

If an agent-unregistration request is received, reply in the following json format:
{
    "succeeded": true or false,
    "message": "a message describing the result"
}
If the agent is registered, remove the agent from the agent_list, tasks can no longer be assigned to it, then succeeded field is true, and message field can be null.
If the agent is not registered in the agent_list, then succeeded field is false, and message field is "Agent (agent name) not registered".

If an list-agent request is received, return the agent_list.

If a task-schedule request is received, you must decide which agent should be used to complete the task and reply in the following json format:
{
    "status": "granted" or "denied",
    "message": "a message describing the result"
    "agent": "the name of the agent that should be used to complete the task"
}
If no agent is capable of the task, the status filed if "denied"
If exists agent which is capable of the task, the status filed if "granted"
"""

AGENT_REGISTER_PROMPT = """
Register a new agent with information below:
The agent name is: {}.
The agent is capable of: {}.
"""

AGENT_UNREGISTER_PROMPT = """
Unregister the agent: {}
"""

TASK_SCHEDULE_PROMPT = """
Schedule the task: {}
"""


class Decider:
    def decide(self, task: Task) -> Result:
        task_target = task.get_target()
        self.ai.ask(task_target)
        result = Result()
        return result

    def register_ai(self, ai: ChatAI) -> bool:
        self.ai = ai
        return True

class SchedulerDecider(Decider):
    def to_result(self, response: str) -> Result:
        ori_response = response
        response = JSON_REGEX.findall(response.replace("\n", ""))
        result = Result()
        if len(response) == 0:
            result.failed(f"invalid response format for response: {ori_response}")
        else:
            response = response[0]
            try:
                response = json.loads(response)
            except Exception as e:
                result.failed(f"failed to load response json: {response}")
                return result
            status = response["status"]
            if is_denied(status):
                result.denied(response["message"])
            elif is_failed(status):
                result.failed(response["message"])
            elif is_granted(status):
                message = response["agent"]
                result.granted(message)
            elif is_insufficient(status):
                result.insufficient(response["message"])
        return result

    
    def decide(self, context: ScheduleContext) -> Result:
        task = context.current_task()
        target = task.get_target()
        if context.is_phase_scheduling():
            prompt = TASK_SCHEDULE_PROMPT.format(target)
            context.add_message(prompt)
        context.prepare_conversation()
        conversation = context.current_conversation()
        response = self.ai.ask(conversation)
        logger.info(f"ai replies with: {response}")
        return self.to_result(response)
        

    def register_agent(self, agent: Agent) -> str:
        agent_info = agent.describe()
        agent_name = agent_info.name
        agent_description = agent_info.description
        logger.info(f"registering agent {agent_name} to decider")
        prompt = AGENT_REGISTER_PROMPT.format(agent_name, agent_description)
        return prompt

    def resolve(self, result: Result) -> tuple[str, Task]:
        pass

class AgentDecider(Decider):
    def decide(self, task: Task) -> Result:
        pass

if __name__ == "__main__":
    test = '{\n"status": "granted",\n"message": "Task scheduled for nmap to scan host 172.22.164.35.",\n"agent": "nmap"\n}'
    a = json.loads(test)
    test = JSON_REGEX.findall(test)
    b = JSON_REGEX.findall("{testsss}")
    print(test)