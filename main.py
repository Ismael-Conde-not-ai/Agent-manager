
def main():
    from agentManager import aIagentManager
    manager = aIagentManager()

    while True:
        print("\n1. Create Agent")
        print("2. Show Agents")
        print("3. Make Agent Act")
        print("4. Recharge Agent")
        print("5. Exit")

        choice = input("Choose an ooption--->")

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
                break
main()
