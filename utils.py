def energyCalculator(self,action,energy):
    '''
    Calculates the value of energy for different actions
    '''
    match action:
        case "act":
            energy-= 10
            energy = max(energy,0)
            return energy
        case "recharge":
            energy = 100
            return energy
