import simplematrixbotlib as botlib,yaml,json
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)
try: 
    prefix = config['server']['prefix']
except:
    prefix = config['server']['user']
creds = botlib.Creds(config['server']['url'], config['server']['user'], config['server']['password'])
bot = botlib.Bot(creds)
class Config(object):
    def __init__(self,room,**kwargs) -> None:
        if isinstance(room, dict):
            self.__dict__.update(room)
        else:
            self.room = room
            self.__dict__.update(kwargs)
loop = None
servers = []
async def save_servers():
    global servers
    sservers = []
    for server in servers:
        ndict = {k: v for k, v in server.__dict__.items() if not k.startswith('_')}
        sservers.append(ndict)
    with open('data.json', 'w') as f:
        json.dump(sservers,f, skipkeys=True)