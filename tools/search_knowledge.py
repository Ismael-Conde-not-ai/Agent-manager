def search_knowledge(agent):
    query = agent.goal
    results = agent.knowledge.search(query)
    if results:
        return results[0]
    return "No knowledge found"