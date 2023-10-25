import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.config import config
from bot.services.server import get_ssh_host_and_port


main_router = Router()

white_list_filter = F.from_user.id.in_(config.server.whitelisted_users)


@main_router.message(~white_list_filter)
async def handle_not_whitelisted_users(message: Message):
    await message.answer(f"You have no acces to this bot. {message.from_user.id}")


@main_router.message(CommandStart())
async def command_start(message: Message) -> None:
    await message.answer("You have acces to this bot. You can select commands in menu.")


@main_router.message(Command("get_ssh"))
async def cancel_handler(message: Message) -> None:
    ssh_user = config.server.ssh_user

    host, port = await get_ssh_host_and_port()

    ssh_connect_command = html.code(f"ssh {ssh_user}@{host} -p {port}")
    ssh_url = f"ssh://{ssh_user}@{host}:{port}"

    await message.answer(
        f"Developer server runs on: {ssh_url}.\n\n{ssh_connect_command}",
    )


async def main():
    bot = Bot(token=config.bot.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.include_router(main_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
