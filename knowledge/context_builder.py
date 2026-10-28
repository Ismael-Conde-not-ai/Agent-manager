class ContextBuilder:

    def build_context(self, results, max_characters=4000):
        """
        Build a readable context from search results,
        respecting the maximum character limit.
        """
        if not results:
            return "No relevant knowledge found."

        context_parts = []

        current_length = 0

        for result in results:
            text = result.get("text", "").strip()
            if not text:
                continue
            metadata = result.get("metadata") or {}
            source = metadata.get("source", "unknown")
            chunk_index = metadata.get("chunk_index", "unknown")
            distance = result.get("distance", "unknown")
            part = (
                f"Source: {source}\n"
                f"Chunk: {chunk_index}\n"
                f"Distance: {distance}\n"
                f"Content:\n{text}\n"
            )        

            remaining = max_characters - current_length
            if remaining <= 0:
                break
            if len(part) > remaining:
                if not context_parts:
                    context_parts.append(part[:remaining])
                break
            context_parts.append(part)
            current_length += len(part)

        if not context_parts:
            return "No relevant knowledge found."

        return "\n".join(context_parts)