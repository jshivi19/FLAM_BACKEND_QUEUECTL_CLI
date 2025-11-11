from datetime import datetime
from enum import Enum
import uuid

class JobState(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD = "dead"

class Job:
    def __init__(self, id=None, command="", state=JobState.PENDING, attempts=0, 
                 max_retries=3, created_at=None, updated_at=None, **kwargs):
        self.id = id or f"job_{uuid.uuid4().hex[:8]}"
        self.command = command
        self.state = state if isinstance(state, JobState) else JobState(state)
        self.attempts = attempts
        self.max_retries = max_retries
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self):
        return {
            "id": self.id,
            "command": self.command,
            "state": self.state.value,
            "attempts": self.attempts,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)
    
    def increment_attempt(self):
        self.attempts += 1
        self.updated_at = datetime.now()
    
    def mark_processing(self):
        self.state = JobState.PROCESSING
        self.updated_at = datetime.now()
    
    def mark_completed(self):
        self.state = JobState.COMPLETED
        self.updated_at = datetime.now()
    
    def mark_failed(self):
        self.state = JobState.FAILED
        self.updated_at = datetime.now()
    
    def mark_dead(self):
        self.state = JobState.DEAD
        self.updated_at = datetime.now()
    
    def should_retry(self):
        return self.attempts < self.max_retries
