import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
    CallbackQuery,
)
from aiogram_forms import dispatcher
from aiogram_forms.forms import Form, fields, FormsManager
from aiogram_forms.errors import ValidationError

from bot.config import config
from bot.services.utils import batch
from bot.services.server import (
    get_ssh_host_and_port,
    start_develop_server,
    create_tunnel,
    get_active_tunnels,
    close_http_tunnel,
    FailedToGetSSHURLException,
)


main_router = Router()

white_list_filter = F.from_user.id.in_(config.server.whitelisted_users)


@main_router.message(~white_list_filter)
async def handle_not_whitelisted_users(message: Message):
    await message.answer(f"You have no acces to this bot. {message.from_user.id}")


@main_router.message(CommandStart())
async def command_start(message: Message) -> None:
    await message.answer("You have acces to this bot. You can select commands in menu.")


@main_router.message(Command("get_ssh"))
async def get_ssh_handler(message: Message) -> None:
    try:
        ssh_user = config.server.ssh_user
        host, port = await get_ssh_host_and_port()

        ssh_connect_command = html.code(f"ssh {ssh_user}@{host} -p {port}")
        ssh_url = f"ssh://{ssh_user}@{host}:{port}"

        await message.answer(
            f"Developer server runs on: {ssh_url}.\n\n{ssh_connect_command}",
        )
    except FailedToGetSSHURLException:
        await message.answer(
            "Developer server off.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Start develop server",
                            callback_data=StartDevelopServer().pack(),
                        )
                    ]
                ]
            ),
        )


class StartDevelopServer(CallbackData, prefix="start_develop_server"):
    ...


@main_router.message(Command("start_develop_server"))
async def start_develop_server_handler(message: Message) -> None:
    try:
        ssh_user = config.server.ssh_user
        host, port = await start_develop_server()

        ssh_connect_command = html.code(f"ssh {ssh_user}@{host} -p {port}")
        ssh_url = f"ssh://{ssh_user}@{host}:{port}"

        await message.answer(
            f"Developer server started on: {ssh_url}.\n\n{ssh_connect_command}",
        )
    except FailedToGetSSHURLException:
        await message.answer(
            "Developer server off.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Start develop server",
                            callback_data=StartDevelopServer().pack(),
                        )
                    ]
                ]
            ),
        )


@main_router.callback_query(StartDevelopServer.filter())
async def start_develop_server_callback_handler(query: CallbackQuery) -> None:
    await start_develop_server_handler(query.message)
    await query.answer("Developer server started.")


def validate_port(port: str):
    """Validate port is integer and between 1 and 65535."""
    try:
        port = int(port)
    except ValueError:
        raise ValidationError("Port must be integer.", code="port_not_int")

    if not 65535 >= port >= 1:
        raise ValidationError(
            "Port must be between 1 and 65535.", code="port_between_1_and_65535"
        )


@dispatcher.register("create-tunnel-form")
class CreateTunnelForm(Form):
    proto = fields.ChoiceField(
        "What protocol?", choices=(("http", "http"), ("tcp", "tcp"))
    )
    port = fields.TextField(
        "What port?",
        validators=[validate_port],
        error_messages={
            "port_not_int": "Port must be integer",
            "port_between_1_and_65535": "Port must be between 1 and 65535",
        },
    )

    @classmethod
    async def callback(cls, message: Message, forms: FormsManager, **data) -> None:
        data = await forms.get_data("create-tunnel-form")
        port = int(data["port"])
        proto = data["proto"]

        n_host, n_port, n_proto = await create_tunnel(port, proto)

        from_url = f"{proto}://127.0.0.1:{port}"

        if proto in ["http"]:
            to_url = f"{n_proto}://{n_host}"
        else:
            to_url = f"{n_proto}://{n_host}:{n_port}"

        await message.answer(
            f"Developer server create tunnel: {from_url} -> {to_url}.",
            reply_markup=ReplyKeyboardRemove(),
        )


@main_router.message(Command("create_tunnel"))
async def create_tunnel_handler(message: Message, forms: FormsManager) -> None:
    await forms.show("create-tunnel-form")


class CloseTunnelCallback(CallbackData, prefix=""):
    port: int


@main_router.message(Command("close_tunnel"))
async def close_tunnel_handler(message: Message) -> None:
    active_tunnels = await get_active_tunnels()

    if not active_tunnels:
        await message.answer("No active tunnels.")
        return

    keyboard = []
    for tunnel in active_tunnels:
        keyboard.append(
            InlineKeyboardButton(
                text=str(tunnel["port"]),
                callback_data=CloseTunnelCallback(port=tunnel["port"]).pack(),
            )
        )

    keyboard = batch(keyboard, 3)

    await message.answer(
        "Choose port that you want to close:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


@main_router.callback_query(CloseTunnelCallback.filter())
async def close_tunnel_callback_handler(
    query: CallbackQuery, callback_data: CloseTunnelCallback
) -> None:
    port = callback_data.port
    await close_http_tunnel(port)
    await query.answer(f"Tunnel closed for port {port}")
    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[])
    )
    await query.message.answer("Tunnel closed.")


async def main():
    bot = Bot(token=config.bot.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dispatcher.attach(dp)

    dp.include_router(main_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
