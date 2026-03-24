def search_knowledge(agent):
    query = agent.goal
    result = agent.knowledge.search(query)
    
    return f"Knowledge result: {result[:200]}"