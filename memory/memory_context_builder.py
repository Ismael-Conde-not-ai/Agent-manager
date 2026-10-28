
class MemoryContextBuilder:
    """Builds a concise context from relevant agent memories."""

    def __init__(self, memory_manager, max_experiences=3):
        self.memory_manager = memory_manager
        self.max_experiences = max_experiences

    def build(self, goal):
        if not isinstance(goal, str) or not goal.strip():
            return ""

        experiences = self.memory_manager.search_experiences(
            query=goal,
            limit=self.max_experiences
        )

        lines = ["Relevant past experiences:"]

        for experience in experiences:
            goal_text = experience.get("goal", "Unknown goal")
            action = experience.get("action", "Unknown action")
            success = experience.get("success", "Unknown")
            result = experience.get("result", "")
            error = experience.get("error", "")
            lesson = experience.get("lesson", "")

            lines.append(
                f"- Goal: {goal_text}; "
                f"Action: {action}; "
                f"Success: {success}; "
                f"Result: {result}"
            )

            if error:
                lines.append(f"  Error: {error}")

            if lesson:
                lines.append(f"  Lesson: {lesson}")

        persistent_memories = (
            self.memory_manager.get_persistent_memories()
        )

        if persistent_memories:
            lines.append("Persistent memories:")

            for key, value in persistent_memories.items():
                lines.append(f"- {key}: {value}")

        if len(lines) == 1:
            return ""

        return "\n".join(lines)
