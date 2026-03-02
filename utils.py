def energyCalculator(self,action,energy):
    '''
    Calculates the value of energy for different actions
    '''
    match action:
        case "act":
            energy-= 10
            return energy
        case "recharge":
            energy = 100
            return energy

def showAndChoose(self,AIList):
    '''
    Show the list of agents in terminal and choose one
    '''
    numeral = 0
    for agente in AIList.agentList:
        numeral +=1
        print(f"{numeral}. {agente.name}")
    '''
    Validates the number
    '''
    print("Choose an option--->")
    option =int(input())
    while option>numeral or option<=0:
        print("ingrese un valor valido --->")
        option =int(input())
    return int(option-1)

