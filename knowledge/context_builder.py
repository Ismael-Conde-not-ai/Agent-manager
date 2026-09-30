class ContextBuilder:

    def build_context(self, results, max_characters=4000):
        """
        Build a context string from the search results.
        """
        if not results:
            return "No relevant knowledge found."

        context_parts = []

        current_length = 0

        for result in results:
            text = result.get("text", "")
            metadata = result.get("metadata", {})
            source = metadata.get("source", "unknown")
            chunk_index = metadata.get("chunk_index", "unknown")
            distance = result.get("distance", "unknown")
            part = (
                f"Source: {source}\n"
                f"Chunk: {chunk_index}\n"
                f"Distance: {distance}\n"
                f"Content:\n{text}\n"
            )        

            if current_length + len(part) > max_characters:
                break

            context_parts.append(part)
            current_length += len(part)

        return "\n".join(context_parts)