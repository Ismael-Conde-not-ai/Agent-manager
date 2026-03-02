
def main():
    from agentManager import aIagentManager
    manager = aIagentManager()
    print("______MAIN MENU______")
    while True:
        print("\n1. Create Agent")
        print("2. Show Agents")
        print("3. Make Agent Act")
        print("4. Recharge Agent")
        print("5. Show Agent Memory")
        print("6. Exit")

        choice = input("Choose an option--->")

        match choice:
            case "1":
                manager.createAgent()
            case "2":
                manager.agentInformation()
            case "3":
                manager.agentAction()
            case "4":
                manager.agentRecharge()
            case "5":
                manager.showAgentMemory()
            case "6":
                break
main()
