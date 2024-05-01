from agent.agent import Agent
from threading import Lock

from chatai.chatai import ChatAI
from decider.decider import SchedulerDecider
from agent.task import Result, Task
from utils.logger import logger

from utils.prompts import AGENT_DENIES_PROMPT, AGENT_FAILED_PROMPT, SCHEDULER_PROMPT
from scheduler.schedule_context import ScheduleContext

class AgentsMap:
    def __init__(self) -> None:
        self.agents: dict[str, Agent] = {}
        self.lock = Lock()

    def add_agent(self, agent: Agent):
        with self.lock:
            self.agents[agent.name] = agent

    def remove_agent(self, agent: Agent):
        with self.lock:
            del self.agents[agent.name]

    def get_agent(self, agent_name: str) -> Agent:
        with self.lock:
            return self.agents[agent_name]
    
    def values(self) -> list[Agent]:
        with self.lock:
            return list(self.agents.values())

class Scheduler:
    def __init__(self, ai: ChatAI) -> None:
        self.agents_map = AgentsMap()
        self.decider = SchedulerDecider()
        self.decider.register_ai(ai)

    def register_agent(self, agent: Agent) -> str:
        self.agents_map.add_agent(agent)

    def unregister_agent(self, agent: Agent):
        self.agents_map.remove_agent(agent)

    def schedule(self, context: ScheduleContext) -> Result:
        task = context.current_task()
        logger.info(f"scheduling task: {task.target} at {context.schedule_times}")
        try:
            schedule_result = self.decider.decide(context)
        except Exception as e:
            logger.error(f"error when making decisions: {e}")
            schedule_result = Result()
            schedule_result.failed(e)

        if schedule_result.is_granted():
            agent_name = schedule_result.message
            agent = self.agents_map.get_agent(agent_name)
            agent_result = agent.execute(task)

            if agent_result.is_denied():
                logger.info(f"scheduler assigned task to agent-{agent_name}, but agent denies: {agent_result.message}")
                prompt = AGENT_DENIES_PROMPT.format(agent_name)
                context.add_message(prompt)
                context.schedule_times += 1
                context.record_schedule_result(agent_result)
                context.reschedule_phase()
                return self.schedule(context)
            elif agent_result.is_insufficient():
                logger.info(f"scheduler assigned task to agent-{agent_name}, but agent needs more information: {agent_result.message}")
                schedule_result.insufficient(agent_result.message)
                context.reschedule_phase()
            elif agent_result.is_failed():
                logger.info(f"scheduler assigned task to agent-{agent_name}, but agent fails to execute: {agent_result.message}")
                prompt = AGENT_FAILED_PROMPT.format(agent_name)
                context.add_message(prompt)
                context.schedule_times += 1
                context.record_schedule_result(agent_result)
                context.reschedule_phase()
                return self.schedule(context)
            elif agent_result.is_granted():
                logger.info(f"scheduler assigned task to agent-{agent_name}, agent granted and executed successfully: {agent_result.message}")
                schedule_result.granted(agent_result.message)

        elif schedule_result.is_denied():
            logger.info(f"scheduler received task, but seems no agent is capable of it: {schedule_result.message}")
        elif schedule_result.is_insufficient():
            logger.info(f"scheduler received task, but needs more information: {schedule_result.message}")
        context.record_schedule_result(schedule_result)
        return schedule_result
    
    def new_schedule_context(self, task: Task):
        context = ScheduleContext(task)
        context.add_message(SCHEDULER_PROMPT)
        # register agents in current context
        for agent in self.agents_map.values():
            context.add_message(self.decider.register_agent(agent))
        return context
    
if __name__ == "__main__":
    from chatai.chatai import OllamaAI
    import dotenv
    dotenv.load_dotenv("envs/ollama.env")
    ai = OllamaAI()
    scheduler = Scheduler(ai)
    task = Task()
    task.set_target("analyze code")
    agent = Agent("nmap", "scanning hosts", "")
    scheduler.register_agent(agent)
    context = scheduler.new_schedule_context(task)
    scheduler.schedule(context)
    print(ai.ask(context.current_conversation()))
    
    