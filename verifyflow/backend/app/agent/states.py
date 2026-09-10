"""Agent phase definitions for the investigation state machine.

These phases represent the agent's reasoning cycle:

    RECEIVED → OBSERVING → DECIDING → ACTING → EVALUATING
                    ↑                               │
                    └──── ADAPTING ←────────────────┘
                                                    │
                                                    ↓
                                               COMPLETED

The DECIDING → ACTING → EVALUATING → ADAPTING loop is where
the agent becomes genuinely adaptive — it can choose different tools,
stop early, or pivot strategy based on accumulated evidence.
"""

from enum import Enum


class AgentPhase(str, Enum):
    """Explicit phases for the agent reasoning cycle."""

    RECEIVED = "RECEIVED"
    OBSERVING = "OBSERVING"
    DECIDING = "DECIDING"
    ACTING = "ACTING"
    EVALUATING = "EVALUATING"
    FAILURE = "FAILURE"
    ADAPTING = "ADAPTING"
    COMPLETED = "COMPLETED"
