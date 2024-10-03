from disnake import Status, Forbidden, HTTPException
from disnake.ext.commands import Cog
from asyncio import sleep, Lock, Task, create_task, CancelledError

from utils.ClientUser import ClientUser
from logging import getLogger

logger = getLogger(__name__)

GUILDID = 1208756727323955250
ONLINE_CHANNEL = 1234910951506182164
IDLE_CHANNEL = 1234911000558305332
DND_CHANNEL = 1234911297670221936

ONLINE_TEXT = "🟢・online: {online} / {all}"
IDLE_TEXT = "🌙・idle: {idle}"
DND_TEXT = "⛔・dnd: {dnd}"

SLEEP_TIME = 600

class MemberCount(Cog):
    def __init__(self, bot: ClientUser):
        self.bot = bot
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

    def returnMembers(self):
        guild = self.bot.get_guild(GUILDID)
        allMem = guild.members
        return allMem

    def all(self):
        return self.returnMembers()

    def count_member(self):
        online = 0
        idle = 0
        dnd = 0
        for member in self.bot.get_guild(GUILDID).members:
            if member.bot:
                continue
            match member.status:
                case Status.online:
                    online += 1
                case Status.dnd:
                    dnd += 1
                case Status.idle:
                    idle += 1

        return online, dnd, idle

    async def sync_name(self) -> None:
        async with self.lock:
            online, dnd, idle = self.count_member()
            try:
                await self.rename_channel(ONLINE_CHANNEL, ONLINE_TEXT.format(online=online, all=len(self.all())))
                logger.info("START SYNC CHANNEL %s", ONLINE_CHANNEL)
                await sleep(3) # Sleep để tránh ratelimit
                await self.rename_channel(IDLE_CHANNEL, IDLE_TEXT.format(idle=idle))
                logger.info("START SYNC CHANNEL %s", IDLE_CHANNEL)
                await sleep(3) # Sleep để tránh ratelimit
                await self.rename_channel(DND_CHANNEL, DND_TEXT.format(dnd=dnd))
                logger.info("START SYNC CHANNEL %s", DND_CHANNEL)
            except Forbidden or HTTPException as e:
                logger.error(e)
                self.sync_tasks.cancel("Hủy task đếm member vì đã xảy ra sự cố")
            except Exception as e:
                logger.error(e)

    async def run_loop(self):
        while True:
            logger.info("Đã nhận tín hiệu khởi động vòng lặp, Thời gian chờ mỗi lần sync: %s giây", SLEEP_TIME)
            await sleep(SLEEP_TIME)
            await self.sync_name()

    async def initalize(self):
        await sleep(5)
        logger.info("Bắt đầu đếm member cho guildID %s", GUILDID)
        await self.sync_name()
        try:
            self.sync_tasks = create_task(self.run_loop())
        except CancelledError:
            await self.bot.close()

    @Cog.listener()
    async def on_ready(self):
        await self.initalize()

def setup(bot: ClientUser):
    bot.add_cog(MemberCount(bot))