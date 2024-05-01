import uuid
from chatai.chatai import Conversation
from agent.task import Result, Task


PHASE_SCHEDULING = "scheduling"
PHASE_SUPPLEMENT = "supplement"
PHASE_RESCHEDULE = "reschedule"

class ScheduleContext:
    def __init__(self, task: Task) -> None:
        self.phase = PHASE_SCHEDULING
        conversation_id = str(uuid.uuid4())
        self.conversation = Conversation(conversation_id)
        self.task = task
        self.schedule_times = 1
        self.schedule_history: list[Result] = []

    def current_conversation(self) -> Conversation:
        return self.conversation

    def current_task(self) -> Task:
        return self.task

    def record_schedule_result(self, result: Result):
        self.schedule_history.append(result)

    def add_message(self, message):
        self.conversation.add_message(message)

    def get_messages(self) -> list:
        return self.conversation.get_messages()

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