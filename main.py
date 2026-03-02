
def main():
    from agentManager import aIagentManager
    manager = aIagentManager()
    print("______MAIN MENU______")
    while True:
        print("\n1. Create Agent")
        print("2. Show Agent Information")
        print("3. Make Agent think")
        print("4. Make Agent Act")
        print("5. Recharge Agent")
        print("6. Show Agent Memory")
        print("7. Exit")

        choice = input("Choose an option--->")

        match choice:
            case "1":
                manager.createAgent()
            case "2":
                manager.agentInformation()
            case "3":
                manager.agentThink()
            case "4":
                manager.agentAction()
            case "5":
                manager.agentRecharge()
            case "6":
                manager.showAgentMemory()
            case "7":
                break
main()
