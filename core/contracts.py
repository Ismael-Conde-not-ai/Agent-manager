from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def __getitem__(self, key):
        return self.model_dump()[key]

    def get(self, key, default=None):
        return self.model_dump().get(key, default)


class ErrorCategory(str, Enum):
    VALIDATION = "validation"
    RESEARCH = "research"
    PLANNING = "planning"
    EXECUTION = "execution"
    TOOL = "tool"
    MCP_COMMUNICATION = "mcp_communication"
    EVALUATION = "evaluation"
    INTERNAL = "internal"


class ErrorInfo(ContractModel):
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    category: ErrorCategory
    retryable: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class PlanStep(ContractModel):
    step: int = Field(ge=1)
    action: str = Field(min_length=1)
    description: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_text(self):
        if not self.action.strip():
            raise ValueError("action must not be empty")
        if not self.description.strip():
            raise ValueError("description must not be empty")
        return self


class Plan(ContractModel):
    steps: list[PlanStep] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_order(self):
        numbers = [step.step for step in self.steps]
        expected = list(range(1, len(numbers) + 1))
        if numbers != expected:
            raise ValueError("plan steps must be consecutive and unique")
        return self

    @classmethod
    def from_legacy(cls, value) -> "Plan | None":
        if isinstance(value, cls):
            return value
        if not isinstance(value, list):
            return None
        try:
            return cls(steps=value)
        except (TypeError, ValueError):
            return None

    def __len__(self):
        return len(self.steps)

    def __iter__(self):
        return iter(self.steps)

    def __getitem__(self, index):
        return self.steps[index]

    def __eq__(self, other):
        if isinstance(other, list):
            return [
                step.model_dump(exclude_defaults=True)
                for step in self.steps
            ] == other
        return super().__eq__(other)


class ToolResult(ContractModel):
    success: bool
    action: str = Field(min_length=1)
    source: Literal["local", "mcp"]
    result: Any | None = None
    error: ErrorInfo | None = None

    @model_validator(mode="after")
    def validate_failure(self):
        if not self.success and self.error is None:
            raise ValueError(
                "failed tool results must include an error"
            )
        if self.success and self.error is not None:
            raise ValueError(
                "successful tool results cannot include an error"
            )
        return self

    def get(self, key, default=None):
        if key == "error" and self.error is not None:
            return self.error.message
        return super().get(key, default)

    def __getitem__(self, key):
        if key == "error" and self.error is not None:
            return self.error.message
        return super().__getitem__(key)


class StepExecutionResult(ContractModel):
    step: PlanStep
    result: ToolResult


class ExecutionResult(ContractModel):
    success: bool
    results: list[StepExecutionResult] = Field(default_factory=list)
    error: ErrorInfo | None = None

    @model_validator(mode="after")
    def validate_failure(self):
        if not self.success and self.error is None and not self.results:
            raise ValueError(
                "failed executions without results must include an error"
            )
        return self

    @classmethod
    def from_legacy(cls, value, plan=None):
        if isinstance(value, cls):
            return value
        if not isinstance(value, dict):
            return cls(
                success=False,
                error=ErrorInfo(
                    code="invalid_execution_result",
                    message="Execution result was not an object.",
                    category=ErrorCategory.EXECUTION,
                ),
            )

        legacy_results = value.get("results", [])
        steps = list(plan) if isinstance(plan, Plan) else []
        results = []
        for index, item in enumerate(legacy_results):
            if isinstance(item, StepExecutionResult):
                results.append(item)
                continue
            if not isinstance(item, dict):
                continue
            step_data = (
                steps[index]
                if index < len(steps)
                else {
                    "step": index + 1,
                    "action": item.get("action") or "unknown",
                    "description": "Legacy execution step",
                }
            )
            tool_result = item
            if "source" not in tool_result:
                tool_result = {**tool_result, "source": "local"}
            if "error" in item and isinstance(item["error"], str):
                tool_result = {
                    **tool_result,
                    "success": False,
                    "error": ErrorInfo(
                        code="legacy_execution_error",
                        message=item["error"],
                        category=ErrorCategory.EXECUTION,
                    ).model_dump(),
                }
            elif not tool_result.get("success", False):
                tool_result = {
                    **tool_result,
                    "error": ErrorInfo(
                        code="legacy_tool_failure",
                        message="Legacy tool execution failed.",
                        category=ErrorCategory.TOOL,
                    ).model_dump(),
                }
            results.append(
                StepExecutionResult(
                    step=step_data,
                    result=tool_result,
                )
            )
        return cls(
            success=value.get("success", False),
            results=results,
            error=(
                ErrorInfo(
                    code="legacy_execution_failed",
                    message="Legacy execution reported failure.",
                    category=ErrorCategory.EXECUTION,
                )
                if not value.get("success", False) and not results
                else None
            ),
        )


class ResearchResult(ContractModel):
    text: str
    sources: list[str] = Field(default_factory=list)

    def __str__(self):
        return self.text


class EvaluationResult(ContractModel):
    success: bool
    evaluation: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)
    error: ErrorInfo | None = None

    @classmethod
    def from_legacy(cls, value):
        if isinstance(value, cls):
            return value
        if not isinstance(value, dict):
            return cls(
                success=False,
                evaluation="Evaluation result was not an object.",
                error=ErrorInfo(
                    code="invalid_evaluation",
                    message="Evaluation result was not an object.",
                    category=ErrorCategory.EVALUATION,
                ),
            )
        if "evaluation" not in value:
            return cls(
                success=value.get("success", False),
                evaluation="Evaluation explanation was not provided.",
                error=ErrorInfo(
                    code="missing_evaluation",
                    message="Evaluation explanation was not provided.",
                    category=ErrorCategory.EVALUATION,
                ),
            )
        return cls.model_validate(value)


class WorkflowAttempt(ContractModel):
    attempt: int = Field(ge=1)
    plan: Plan | None = None
    execution: ExecutionResult | None = None
    evaluation: EvaluationResult | None = None
    success: bool
    error: ErrorInfo | None = None


class WorkflowResult(ContractModel):
    success: bool
    goal: str
    research: ResearchResult | None = None
    attempts: list[WorkflowAttempt] = Field(default_factory=list)
    final_plan: Plan | None = None
    final_execution: ExecutionResult | None = None
    final_evaluation: EvaluationResult | None = None
    error: ErrorInfo | None = None

    @property
    def total_attempts(self):
        return len(self.attempts)

    def __getitem__(self, key):
        if key == "total_attempts":
            return self.total_attempts
        if key == "plan":
            return (
                [step.model_dump() for step in self.final_plan]
                if self.final_plan is not None
                else None
            )
        if key == "execution":
            return self.final_execution
        if key == "evaluation":
            return self.final_evaluation
        if key == "error":
            return self.error.message if self.error is not None else None
        return super().__getitem__(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def to_legacy_dict(self):
        return {
            "success": self.success,
            "goal": self.goal,
            "research": (
                self.research.text
                if self.research is not None
                else None
            ),
            "attempts": [attempt.model_dump() for attempt in self.attempts],
            "total_attempts": self.total_attempts,
            "plan": (
                self.final_plan.model_dump()["steps"]
                if self.final_plan is not None
                else None
            ),
            "execution": (
                self.final_execution.model_dump()
                if self.final_execution is not None
                else None
            ),
            "evaluation": (
                self.final_evaluation.model_dump()
                if self.final_evaluation is not None
                else None
            ),
            "error": (
                self.error.message
                if self.error is not None
                else None
            ),
        }
