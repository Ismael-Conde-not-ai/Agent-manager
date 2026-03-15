import json


def load_agent_config():
    '''
    Lee la configuracion de agente en agent_config.json, lo guarda en config y lo retorna.
    '''
    with open("config/agent_config.json","r") as file:
        config = json.load(file)

    return config