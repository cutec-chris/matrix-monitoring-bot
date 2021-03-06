import asyncio,subprocess,datetime
from lib2to3.pytree import Base

from numpy import argsort
from init import *
class Server(Config):
    def __init__(self, room, **kwargs) -> None:
        super().__init__(room, **kwargs)
        self.status = None
        self.lastcontact = None
        if not hasattr(self,'remains'):
            self.remains = 0
@bot.listener.on_message_event
async def add(room, message):
    global servers,loop
    match = botlib.MessageMatch(room, message, bot, prefix)
    if match.is_not_from_this_bot() and match.prefix()\
    and match.command("ping"):
        if len(match.args())>2:
            interval=match.args()[2]
        else:
            interval = 60
        server = Server(
            room=room.room_id,
            server=match.args()[1],
            interval=interval
        )
        servers.append(server)
        loop.create_task(check_server(server))
        await save_servers()
        await bot.api.send_text_message(room.room_id,'ok')
@bot.listener.on_message_event
async def bot_help(room, message):
    bot_help_message = f"""
    Help Message:
        prefix: {prefix}
        commands:
            ping:
                command: ping address seconds
                description: add an ping test every seconds to address
            help:
                command: help, ?, h
                description: display help command
                """
    match = botlib.MessageMatch(room, message, bot, prefix)
    if match.is_not_from_this_bot() and match.prefix() and (
       match.command("help") 
    or match.command("?") 
    or match.command("h")):
        await bot.api.send_text_message(room.room_id, bot_help_message)
async def printstatus(server):
    answer = 'Server '+server.server+' is '
    if server.status:
        answer += 'up'
    else:
        answer += 'down'
    if server.lastcontact:
        answer += ' last contact was '+str(server.lastcontact)
    await bot.api.send_text_message(server.room,answer)
async def check_server(server):
    while True:
        try:
            if server.remains>0:
                server.remains -= 1
            else: 
                server.remains = int(server.interval)
                try:
                    if subprocess.check_output(["ping", "-c", "1","-W",str(0.1), server.server]):
                        nstatus = True
                        server.lastcontact = datetime.datetime.now()
                except:
                    nstatus = False
                if nstatus != server.status:
                    server.status = nstatus
                    await printstatus(server)
                    await save_servers()
        except BaseException as e:
            pass
        await asyncio.sleep(1)
@bot.listener.on_startup
async def startup(room):
    global loop,servers
    loop = asyncio.get_running_loop()
    try:
        with open('data.json', 'r') as f:
            aservers = json.load(f)
            for server in aservers:
                nserver = Server(server)
                servers.append(nserver)
    except: pass
    for server in servers:
        loop.create_task(check_server(server))
bot.run()