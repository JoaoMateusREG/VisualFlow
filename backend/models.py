from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class NodeType(str, Enum):
    LOGIN = "login"
    OPEN_SITE = "openSite"
    CLICK_BUTTON = "clickButton"
    EXTRACT_TABLE = "extractTable"
    CAPTURE_TABLE = "captureTable"
    WAIT = "wait"
    SLEEP = "sleep"
    SPREADSHEET = "spreadsheet"
    LOOP_FOR = "loopFor"
    LOOP_WHILE = "loopWhile"
    VARIABLE = "variable"
    CONDITION = "condition"
    SCHEDULE = "schedule"

    EXECUTE_SCRIPT = "executeScript"
    EXTRACT_TEXT = "extractText"
    TRANSFORM_COLUMN = "transformColumn"
    GROUP_DATA = "groupData"
    EXECUTE_PYTHON = "executePython"

class FlowExecutionStep(BaseModel):
    id: str
    type: NodeType
    label: str
    inputs: Dict[str, Any]
    position: Dict[str, float]

class FlowValidation(BaseModel):
    isValid: bool
    errors: List[str]

class FlowMetadata(BaseModel):
    name: str
    createdAt: str
    version: str
    totalSteps: int

class FlowData(BaseModel):
    metadata: FlowMetadata
    validation: FlowValidation
    executionOrder: List[FlowExecutionStep]
    rawData: Dict[str, Any]

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

class ExecutionResult(BaseModel):
    id: str
    status: ExecutionStatus
    started_at: datetime
    finished_at: Optional[datetime] = None
    flow_name: str
    total_steps: int
    current_step: int
    logs: List[str]
    results: Dict[str, Any]
    error: Optional[str] = None

class SeleniumConfig(BaseModel):
    headless: bool = False
    window_size: str = "1920,1080"
    timeout: int = 30
    implicit_wait: int = 10
    page_load_timeout: int = 30
    
class ExecutionRequest(BaseModel):
    flow_data: FlowData
    config: Optional[SeleniumConfig] = SeleniumConfig()