def search_knowledge(agent):
    
    context = agent.get_relevant_context()
    
    return f"Context used: {context[:200]}"