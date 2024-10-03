from __future__ import annotations

from os import walk, path, environ
from disnake import Intents, MemberCacheFlags
from disnake.ext . commands import CommandSyncFlags, InteractionBot, ExtensionAlreadyLoaded, ExtensionNotLoaded
from dotenv import load_dotenv
from logging import getLogger

load_dotenv()

logger = getLogger(__name__)

class ClientUser(InteractionBot):
    
    def __init__(self, *args, intents, command_sync_flag, **kwargs) -> None:
        super().__init__(*args, **kwargs, intents=intents, command_sync_flags=command_sync_flag)
        self.logger = logger

    async def on_ready(self):
        logger.info(f"Logged in as {self.user.name} - {self.user.id}")

    async def close(self):
        logger.warning("Đã nhận tín hiệu ngắt bot")
        await super().close()

    def load_modules(self):

        modules_dir = "Module"
        
        for item in walk(modules_dir):
            files = filter(lambda f: f.endswith('.py'), item[-1])
            for file in files:
                filename, _ = path.splitext(file)
                module_filename = path.join(modules_dir, filename).replace('\\', '.').replace('/', '.')
                try:
                    self.reload_extension(module_filename)
                    logger.info(f'Module {file} Đã tải lên thành công')
                except (ExtensionAlreadyLoaded, ExtensionNotLoaded):
                    try:
                        self.load_extension(module_filename)
                        logger.info(f'Module {file} Đã tải lên thành công')
                    except Exception as e:
                        logger.error(f"Đã có lỗi xảy ra với Module {file}: Lỗi: {repr(e)}")
                        continue
                except Exception as e:
                    logger.error(f"Đã có lỗi xảy ra với Module {file}: Lỗi: {repr(e)}")
                    continue


def load():
        
    logger.info("Booting Client....")
    
    DISCORD_TOKEN = environ.get("TOKEN")
    
    intents = Intents()
    intents.members = True
    intents.guilds = True
    intents.presences = True
    member_cache_Flag = MemberCacheFlags() # WARNING: NHIỀU GUILD == NHIỀU RAM
    member_cache_Flag.joined = True
    member_cache_Flag.voice = False
        
    sync_cfg = True
    command_sync_config = CommandSyncFlags(
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
        logger.error("An Error occured:", repr(e))
