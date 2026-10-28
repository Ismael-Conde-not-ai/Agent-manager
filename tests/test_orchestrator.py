
from unittest.mock import Mock

from core.orchestrator import Orchestrator


def build_orchestrator(execution_success, evaluation_success):
    manager = Mock()

    research = Mock()
    research.research.return_value = "Research completed"

    planner = Mock()
    planner.create_plan.return_value = '[{"step": 1, "action": "work"}]'
    planner.parse_plan.return_value = ["work"]

    executor = Mock()
    executor.execute_plan.return_value = {
        "success": execution_success,
        "results": [],
    }

    evaluator = Mock()
    evaluator.evaluate.return_value = {
        "success": evaluation_success,
        "evaluation": "Mock evaluation",
    }

    registered = {
        "ResearchAgent": research,
        "PlannerAgent": planner,
        "ExecutorAgent": executor,
        "EvaluatorAgent": evaluator,
    }

    manager.get_agent.side_effect = registered.get

    return Orchestrator(manager), executor, evaluator


def test_success_on_first_attempt():
    orchestrator, executor, evaluator = build_orchestrator(
        execution_success=True,
        evaluation_success=True,
    )

    result = orchestrator.run("Test goal", agent=Mock())

    assert result["success"] is True
    assert result["total_attempts"] == 1
    assert executor.execute_plan.call_count == 1
    assert evaluator.evaluate.call_count == 1


def test_failed_attempt_then_retry():
    orchestrator, executor, evaluator = build_orchestrator(
        execution_success=False,
        evaluation_success=False,
    )

    result = orchestrator.run(
        "Test goal",
        agent=Mock(),
        max_retries=1,
    )

    assert result["success"] is False
    assert result["total_attempts"] == 2
    assert executor.execute_plan.call_count == 2
    assert evaluator.evaluate.call_count == 2


def test_no_retries_when_disabled():
    orchestrator, executor, evaluator = build_orchestrator(
        execution_success=False,
        evaluation_success=False,
    )

    result = orchestrator.run(
        "Test goal",
        agent=Mock(),
        max_retries=0,
    )

    assert result["success"] is False
    assert result["total_attempts"] == 1
    assert executor.execute_plan.call_count == 1
    assert evaluator.evaluate.call_count == 1


if __name__ == "__main__":
    test_success_on_first_attempt()
    test_failed_attempt_then_retry()
    test_no_retries_when_disabled()
    print("All orchestrator tests passed!")
