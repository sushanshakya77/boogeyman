from enum import Enum

from pydantic import BaseModel


class Severity(str, Enum):
    high = "HIGH"
    medium = "MEDIUM"
    low = "LOW"


class Finding(BaseModel):
    file: str
    line: int
    severity: Severity
    category: str
    explanation: str
    suggested_fix: str


class Review(BaseModel):
    findings: list[Finding]
