class ToolRegistry:
    """
    Manage a registry of tools (fuctions).
    It allows registry, excute and list functions associated with a name.
    """
    def __init__(self):
        '''Initialize the empty tool registry'''
        self.tools={}

    def register(self, name,func):
        ''' 
        Registrires a new tool to the dictionary
        Args: 
        name:str is the name of the tool
        func: function associated to the name
        '''
        self.tools[name]=func
    
    def execute(self, name, agent):
        '''
        Execute a tool asiciated to an agent object.
        returns none if no tool registered or calls the function using the object
        args
        name:(str) the name of the tool
        agent:(object) object passed as an argument to the tool
        '''

        if name not in self.tools:
            print (f"Tool {name} not found")
            return
        
        return self.tools[name](agent)
    
    def list_tools (self):
        '''
        Returns a list of the names of tools
        '''
        return list(self.tools.keys())