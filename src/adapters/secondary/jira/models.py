from dataclasses import dataclass
from enum import StrEnum
from typing import Dict, List, Optional, Union

@dataclass
class JiraFilter:
    """Model for a Jira Filter."""
    id: str
    name: str
    jql: str
    owner_account_id: str


class ProjectCategory(StrEnum):
    """Enumeration of JIRA project categories."""

    CORE_CONNECTIVITY = "10002"


@dataclass
class JiraPlanRequest:
    """Request model for creating a Jira Plan."""

    name: str
    issue_sources: List[Dict[str, str]]  # List of issue sources (projects, boards)
    scheduling: Dict[str, object]  # Scheduling configuration
    lead_account_id: str
    permissions: List[Dict[str, object]]  # List of permission settings
    exclusion_rules: Optional[Dict[str, object]] = None  # Optional exclusion rules
    custom_fields: Optional[List[Dict[str, object]]] = None  # Optional custom fields


@dataclass
class JiraPlanResponse:
    """Response model from creating a Jira Plan."""

    id: str
    name: str
    url: str
