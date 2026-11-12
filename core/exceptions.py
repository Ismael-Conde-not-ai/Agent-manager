from __future__ import annotations

from typing import Any

from core.contracts import ErrorCategory, ErrorInfo


class AgentError(Exception):
    """Base exception for expected failures in the agent domain."""

    category = ErrorCategory.INTERNAL
    default_code = "agent_error"
    default_retryable = False

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        category: ErrorCategory | None = None,
        details: dict[str, Any] | None = None,
        retryable: bool | None = None,
        cause: BaseException | None = None,
    ):
        super().__init__(message)
        self.code = code or self.default_code
        self.category = category or self.category
        self.details = details or {}
        self.retryable = (
            self.default_retryable
            if retryable is None
            else retryable
        )
        if cause is not None:
            self.__cause__ = cause

    def to_error_info(self) -> ErrorInfo:
        return ErrorInfo(
            code=self.code,
            message=str(self),
            category=self.category,
            retryable=self.retryable,
            details=self.details,
        )


class ValidationError(ValueError, AgentError):
    category = ErrorCategory.VALIDATION
    default_code = "validation_error"


class PlanningError(RuntimeError, AgentError):
    category = ErrorCategory.PLANNING
    default_code = "planning_error"


class ExecutionError(RuntimeError, AgentError):
    category = ErrorCategory.EXECUTION
    default_code = "execution_error"
    default_retryable = True


class ToolExecutionError(ExecutionError):
    category = ErrorCategory.TOOL
    default_code = "tool_execution_error"


class MCPCommunicationError(ValueError, ExecutionError):
    category = ErrorCategory.MCP_COMMUNICATION
    default_code = "mcp_communication_error"
    default_retryable = True


class EvaluationError(RuntimeError, AgentError):
    category = ErrorCategory.EVALUATION
    default_code = "evaluation_error"


class InternalAgentError(RuntimeError, AgentError):
    category = ErrorCategory.INTERNAL
    default_code = "internal_agent_error"
