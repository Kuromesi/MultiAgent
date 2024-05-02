import uuid
from agent.agent import Agent
from chatai.chatai import Conversation
from agent.task import Result, Task
from utils.prompts import SCHEDULER_PROMPT

PHASE_SCHEDULING = "scheduling"
PHASE_SUPPLEMENT = "supplement"
PHASE_RESCHEDULE = "reschedule"

class ScheduleContext:
    def __init__(self, task: Task) -> None:
        self.phase = PHASE_SCHEDULING
        conversation_id = str(uuid.uuid4())
        self.conversation = Conversation(conversation_id)
        self.conversation.add_prefix(SCHEDULER_PROMPT)
        self.task = task
        self.schedule_times = 1
        self.schedule_history: list[Result] = []
        self.task_history: list[Task] = []
        self.available_agents = {}
        self.agents_modified = False

    def reset_target(self, target: str):
        self.task_history.append(self.task.copy())
        self.task.set_target(target)

    def set_agents(self, agents: dict[str, str]):
        self.available_agents = agents
        self.agents_modified = True

    def add_agent(self, agent: Agent):
        agent_name = agent.describe().name
        assert agent_name not in self.available_agents
        self.available_agents[agent_name] = agent.registration_prompt()
        self.agents_modified = True

    def remove_agent(self, agent_name) -> None:
        assert agent_name in self.available_agents
        del self.available_agents[agent_name]
        self.agents_modified = True

    def current_conversation(self) -> Conversation:
        return self.conversation

    def current_task(self) -> Task:
        return self.task

    def record_schedule_result(self, result: Result):
        self.schedule_history.append(result)

    def add_message(self, message):
        self.conversation.add_message(message)

    def prepare_conversation(self) -> list:
        if self.agents_modified:
            self.conversation.reset_messages([])
            for agent_prompt in self.available_agents.values():
                self.conversation.add_message(agent_prompt)
            self.conversation.add_message(self.task.get_target())
            self.agents_modified = False

    def _init_conversation_prefixes(self):
        self.conversation.reset_prefixes([])
        self.conversation.add_prefix(SCHEDULER_PROMPT)
        for agent_prompt in self.available_agents.values():
            self.conversation.add_prefix(agent_prompt)

    def is_phase_scheduling(self) -> bool:
        return self.phase == PHASE_SCHEDULING
    
    def is_phase_supplement(self) -> bool:
        return self.phase == PHASE_SUPPLEMENT
    
    def is_phase_reschedule(self) -> bool:
        return self.phase == PHASE_RESCHEDULE
    
    def scheduling_phase(self):
        self.phase = PHASE_SCHEDULING

    def supplement_phase(self):
        self.phase = PHASE_SUPPLEMENT

    def reschedule_phase(self):
        self.phase = PHASE_RESCHEDULE