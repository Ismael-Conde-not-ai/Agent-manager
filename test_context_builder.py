from knowledge.context_builder import ContextBuilder

builder = ContextBuilder()


results = [

    {
        "id": "planning.txt_chunk_0",

        "text": (
            "Planning allows an AI agent "
            "to divide a complex goal "
            "into smaller actions."
        ),

        "metadata": {
            "source": "planning.txt",
            "chunk_index": 0
        }
    },

    {
        "id": "planning.txt_chunk_1",

        "text": (
            "Each action can then be "
            "executed using an appropriate tool."
        ),

        "metadata": {
            "source": "planning.txt",
            "chunk_index": 1
        }
    }
]


context = builder.build_context(
    results
)


print(context)