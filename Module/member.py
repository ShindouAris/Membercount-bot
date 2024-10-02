import disnake
from disnake.ext import commands
from asyncio import sleep, Lock, Task, create_task, CancelledError

from utils.ClientUser import ClientUser
import logging

logger = logging.getLogger(__name__)

GUILDID = 1208756727323955250
ONLINE_CHANNEL = 1234910951506182164
IDLE_CHANNEL = 1234911000558305332
DND_CHANNEL = 1234911297670221936

ONLINE_TEXT = "🟢・online: {online} / {all}"
IDLE_TEXT = "🌙・idle: {idle}"
DND_TEXT = "⛔・dnd: {dnd}"

SLEEP_TIME = 600

class MemberCount(commands.Cog):
    def __init__(self, bot: ClientUser):
        self.bot = bot
        self.list_idle_mem: list[disnake.Member] = []
        self.list_online_mem: list[disnake.Member] = []
        self.list_dnd_mem: list[disnake.Member] = []
        self.lock = Lock()
        self.sync_tasks: Task = None # type: ignore

    async def rename_channel(self, ChannelID = None, text = None):
        guild = self.bot.get_guild(GUILDID)
        if not guild:
            return
        channel = guild.get_channel(ChannelID)
        if not channel:
            return
        await channel.edit(name=text)

    def count_members(self):
        guild = self.bot.get_guild(GUILDID)
        allMem = guild.members
        return allMem

    def all(self):
        return self.count_members()

    def idle(self):
        if self.list_idle_mem:
            self.list_idle_mem.clear()
        for member in self.count_members():
            if member.bot:
                continue
            if member.status == disnake.Status.idle:
                self.list_idle_mem.append(member)

    def online(self):
        if self.list_online_mem:
            self.list_online_mem.clear()
        for member in self.count_members():
            if member.bot:
                continue
            if member.status == disnake.Status.online:
                self.list_online_mem.append(member)

    def dnd(self):
        if self.list_dnd_mem:
            self.list_dnd_mem.clear()

        for member in self.count_members():
            if member.bot:
                continue
            if member.status == disnake.Status.dnd:
                self.list_dnd_mem.append(member)

    async def sync_name(self) -> None:
        async with self.lock:
            try:
                await self.rename_channel(ONLINE_CHANNEL, ONLINE_TEXT.format(online=len(self.list_online_mem), all=len(self.all())))
                logger.info("START SYNC CHANNEL %s", ONLINE_CHANNEL)
                await sleep(3)
                await self.rename_channel(IDLE_CHANNEL, IDLE_TEXT.format(idle=len(self.list_idle_mem)))
                logger.info("START SYNC CHANNEL %s", IDLE_CHANNEL)
                await sleep(3)
                await self.rename_channel(DND_CHANNEL, DND_TEXT.format(dnd=len(self.list_dnd_mem)))
                logger.info("START SYNC CHANNEL %s", DND_CHANNEL)
            except disnake.Forbidden or disnake.HTTPException as e:
                logger.error(e)
                self.sync_tasks.cancel("Hủy task đếm member vì đã xảy ra sự cố")
            except Exception as e:
                logger.error(e)

    async def run_loop(self):
        logger.info("Đã nhận tín hiệu khởi động vòng lặp, Thời gian chờ mỗi lần sync: %s", SLEEP_TIME)
        await sleep(SLEEP_TIME)
        self.idle()
        self.online()
        self.dnd()
        await self.sync_name()

    async def initalize(self):
        logger.info("Bắt đầu đếm member cho guildID %s", GUILDID)
        self.idle()
        self.online()
        self.dnd()
        await self.sync_name()
        try:
            self.sync_tasks = create_task(self.run_loop())
        except CancelledError:
            await self.bot.close()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.initalize()

def setup(bot: ClientUser):
    bot.add_cog(MemberCount(bot))