class AIagent:
    """
    Represents a simple AI agent with a goal, energy level,
    and basic actions such as think, act, and recharge.
    """
    from utils import energyCalculator
    from apiClient import geminiAI
    def __init__(self,name,goal):
        self.name :str = name
        self.goal :str = goal
        self.energy : int = 100
        self.status :str = 'Idle'
        self.memory = []
        self.tools = {
            "work":self.act,
            "recharge":self.recharge,
            "rest":self.rest
        }
        self.plan = []

    def think(self):
        '''
        prints the agent's thoughts and what is willing to do
        '''
        self.status='Thinking'
        self.memory.append("Agent is thinking")
        print(f"the agent {self.name} is thinking")
    
    def act(self):
        '''
        Spend energy to perform an action
        '''
        if self.energy >= 10:
            calcEnergy = self.energyCalculator
            energy = self.energy
            self.energy = calcEnergy('act',energy)
            self.status ='Working'
            self.memory.append("Agent is working")
            print(f"The agent {self.name} is performing: {self.goal}")
        else:
            self.status ='Out of energy'
            self.memory.append("Agent out of energy")

    def recharge(self):
        '''
        Recharges energy
        '''
        calcEnergy = self.energyCalculator
        energy = self.energy
        self.energy=calcEnergy("recharge",energy)
        self.status = 'Recharged'
        self.memory.append("Agent recharged")
        print(f"Agent {self.name} is recharged")

    def rest(self):
        '''
        The agent rests
        '''
        self.status = "Resting"
        self.memory.append("The agent is resting")

    def info(self):
        '''
        Prints agent's informationthin
        '''
        print(f"\n🤖 Agent: {self.name}\n 🎯 Goal: {self.goal}\n 🔋 Energy level: {self.energy}%\n 🏗️ Status: {self.status}")

    def showMemory(self):
        '''
        Print the events in the agent's memory
        '''
        print(f"\n Memory of {self.name}:")
        for event in self.memory:
            print("- ",event)
    
    def thinkAi (self):
        '''
        Send a promt to gemimi 3 flash using name and goal of the agent, uses recent memory 5 entries
        '''
        gemini = self.geminiAI
        prevoiusActions= self.recentMemory()
        
        memory_text="\n".join(prevoiusActions) if prevoiusActions else "No previous actions."
        tools_list = "\n".join(self.tools.keys())
        prompt = self.build_prompt(memory_text,tools_list)
        decision =gemini(prompt).strip().lower()
        self.memory.append(f"AI decision: {decision}")
        print(f"\nAi decision for {self.name}:")
        print(decision)
        return decision
    
    def build_prompt (self,memory_text,tools_list):
        prompt:str = f"""
        ROLE:
        You are an autonomous productivity agent.

        AGENT NAME:
        {self.name}

        GOAL:
        {self.goal}

        CURRENT STATE:
        Energy: {self.energy}
        Status: {self.status}

        MEMORY:
        {memory_text}

        AVAILABLE TOOLS:
        {tools_list}

        RULES:
        - If energy is low, recharge.
        - If energy is high, work toward the goal.
        - Rest if no urgent action is required.
        - If energy < 20 recharge

        INSTRUCTIONS:
        Choose the best tool for the situation.

        Respond ONLY with the tool name.
        """
        return prompt
    
    def recentMemory(self,limit=5):
        '''
        Return only the last 5 memory entries
        '''
        return self.memory[-limit:]
    
    def execute_tool (self,toolName):
        if toolName in self.tools:
            self.tools[toolName]()
            self.memory.append(f"executed tool: {toolName}")
        else:
            self.memory.append(f"Invalid tool: {toolName}")

    '''def autonomousStep (self):
        decision_tool =self.thinkAi()
        #self.executeDecision(decision)
        self.execute_tool(decision_tool)'''

    def create_plan (self):
        prompt =f"""
        You are an autonomous AI agent.

        Agent name: {self.name}
        Goal: {self.goal}

        Available tools:
        {", ".join(self.tools.keys())}

        Create a short plan to achieve the goal.

        Return 3 to 5 steps using only the tool names.
        Example:

        work
        work
        recharge
        rest
        """
        gemini =self.geminiAI
        plan_text =gemini(prompt).strip().lower()
        self.plan = plan_text.split("\n")
        print("\nGenerated Plan:")
        for step in self.plan:
            print("-", step)
    
    def execute_plan_step (self):
        if not self.plan:
            print("No plan available")
            return
        step = self.plan.pop(0)
        print (f"\nExecuting step: {step}")
        self.execute_tool(step)
        self.memory.append(f"Plan step executed: {step}")

    def autonomousStep (self):
        if not self.plan:
            self.create_plan()
        self.execute_plan_step()