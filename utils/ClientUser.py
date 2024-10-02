from __future__ import annotations

import os
import disnake
from colorama import *
from disnake.ext import commands
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)       

class ClientUser(commands.InteractionBot):
    
    def __init__(self, *args, intents, command_sync_flag, **kwargs) -> None:
        super().__init__(*args, **kwargs, intents=intents, command_sync_flags=command_sync_flag)
        self.uptime = disnake.utils.utcnow()

    async def on_ready(self):
        logger.info(f"Logged in as {self.user.name} - {self.user.id}")
    

    def load_modules(self):

        modules_dir = "Module"

        load_status = {
            "reloaded": [],
            "loaded": []
        }
        
        for item in os.walk(modules_dir):
            files = filter(lambda f: f.endswith('.py'), item[-1])
            for file in files:
                filename, _ = os.path.splitext(file)
                module_filename = os.path.join(modules_dir, filename).replace('\\', '.').replace('/', '.')
                try:
                    self.reload_extension(module_filename)
                    logger.info(f'{Fore.GREEN} [ ✅ ] Module {file} Đã tải lên thành công{Style.RESET_ALL}')
                except (commands.ExtensionAlreadyLoaded, commands.ExtensionNotLoaded):
                    try:
                        self.load_extension(module_filename)
                        logger.info(f'{Fore.GREEN} [ ✅ ] Module {file} Đã tải lên thành công{Style.RESET_ALL}')
                    except Exception as e:
                        logger.error(f"[❌] Đã có lỗi xảy ra với Module {file}: Lỗi: {repr(e)}")
                        continue
                except Exception as e:
                    logger.error(f"[❌] Đã có lỗi xảy ra với Module {file}: Lỗi: {repr(e)}")
                    continue
                
        return load_status

def load():
        logger.info("Booting Client....")
        
        DISCORD_TOKEN = os.environ.get("TOKEN")
        
        intents = disnake.Intents()
        intents.members = True
        intents.voice_states = True
        intents.guilds = True
        intents.presences = True
        member_cache_Flag = disnake.MemberCacheFlags.all()
           
        sync_cfg = True
        command_sync_config = commands.CommandSyncFlags(
                            allow_command_deletion=sync_cfg,
                            sync_commands=sync_cfg,
                            sync_commands_debug=sync_cfg,
                            sync_global_commands=sync_cfg,
                            sync_guild_commands=sync_cfg
                        )  
        
        bot  = ClientUser(intents=intents, command_sync_flag=command_sync_config, member_cache_flags=member_cache_Flag)

        bot.load_modules()
        print("-"*40)
        
        try:
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            if  "LoginFailure" in str(e):
                logger.error("An Error occured:", repr(e))
