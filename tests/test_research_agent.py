from agents.research_agent import ResearchAgent


def main():
    result = ResearchAgent().research("What is quantum teleportation?")
    print("\nRESEARCH RESULT\n")
    print(result)


if __name__ == "__main__":
    main()
