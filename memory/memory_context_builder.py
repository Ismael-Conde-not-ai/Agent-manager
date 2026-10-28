
class MemoryContextBuilder:
    """Build a concise context from relevant agent memories."""

    def __init__(
        self,
        memory_manager,
        max_experiences=3,
        max_chars=4000,
    ):
        if max_experiences < 0:
            raise ValueError("max_experiences cannot be negative")

        if max_chars < 1:
            raise ValueError("max_chars must be positive")

        self.memory_manager = memory_manager
        self.max_experiences = max_experiences
        self.max_chars = max_chars

    def build(self, goal):
        if not isinstance(goal, str) or not goal.strip():
            return ""

        lines = []

        experiences = self.memory_manager.search_experiences(
            query=goal,
            limit=self.max_experiences,
        )

        if experiences:
            lines.append("Relevant past experiences:")

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

        if not lines:
            return ""

        # Add complete lines while respecting the character limit.
        context_lines = []
        used_chars = 0

        for line in lines:
            extra_chars = len(line) + (1 if context_lines else 0)

            if used_chars + extra_chars > self.max_chars:
                break

            context_lines.append(line)
            used_chars += extra_chars

        return "\n".join(context_lines)

