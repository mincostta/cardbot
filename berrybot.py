import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext

from conn import get_cursor
from admins import admins, addsub, addcard, criartag, addtag, removetag, editcard, editag, editsub, checar, reset, ban, desban, girados, allberry, fermentar, fermentarall, presentear, remove, depositar, depositarall, regadm, vinculos, deletar
from users import users, colheita, var, buscar, tag, regar, colher, cesta, top, topremove, topadd, status, trocar, doar, doarsemente, doarcolheita, doarinv, doarcat, doarcol, doartag, doarwish, descartar, descartarsub, descartarcat, checkfruit, saborear, lojinha, casar, saque, wish, wishlist, berryin, berryout, laranja, recolher, desvinc, laranjas, midia, perfil, receita, receita_process
from utils import utils, callback_query_func, is_banned, attuser

load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# -------------------------------------------
# COMANDO START

@dp.message(Command("start"))
async def start(msg: Message):
    if msg.sender_chat:

        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id

    async with get_cursor() as cursor:
        await cursor.execute("SELECT username FROM usuarios WHERE telegram_id = %s", (telegram_id,))
        result = await cursor.fetchall()

        if not result:
            if await is_banned(telegram_id, msg) == False:
                if msg.from_user.username:
                    username = True
                    await cursor.execute("INSERT INTO usuarios (telegram_id, username) VALUES (%s, %s)", (telegram_id, msg.from_user.username,))
            else:
                return
        else:
            username = await attuser(telegram_id, msg)

    canais = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌱", callback_data="canais", url="https://t.me/addlist/GQhSixD-fqVkYjRh")]
    ])

    if username:
        await msg.reply(
            f"🧺 Boas-vindas à Vila Tutti-Frutti, @{msg.from_user.username}! \n\nEntre em @villageberry para ficar por dentro de todas as atualizações do bot. \n\nInicie sua estadia fazendo sua primeira colheita!", reply_markup=canais)


# -------------------------------------------
# HANDLER PARA BOTÕES

@dp.callback_query()
async def handle_botões(call: CallbackQuery, state: FSMContext):
    msg = call.message
    telegram_id = call.from_user.id

    if await is_banned(telegram_id, msg) == False:
        await callback_query_func(call, bot, state)


# -------------------------------------------
# COMANDOS DE USUÁRIOS

@dp.message(Command("colher"))
async def handle_colher(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode colher em chat privado.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await colher(bot, msg)


@dp.message(Command(commands=["safra", "saque"]))
async def handle_saque(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode sacar em chat privado.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await saque(bot, msg)


@dp.message(Command(commands=["colheita", "col"]))
async def handle_colheita(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await colheita(bot, msg)


@dp.message(Command(commands=["var"]))
async def handle_var(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await var(msg)


@dp.message(Command("buscar"))
async def handle_buscar(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await buscar(bot, msg)


@dp.message(Command("checkfruit"))
async def handle_checkfruit(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await checkfruit(telegram_id, msg)


@dp.message(Command("tag"))
async def handle_tag(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await tag(bot, msg)


@dp.message(Command("regar"))
async def handle_regar(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode regar em chat privado.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await regar(msg)


@dp.message(Command("cesta"))
async def handle_cesta(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await cesta(msg)


@dp.message(Command("top"))
async def handle_top(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await top(bot, msg)


@dp.message(Command("topremove"))
async def handle_topremove(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode configurar sua visualização no ranking em chat privado.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await topremove(telegram_id, msg)


@dp.message(Command("topadd"))
async def handle_topadd(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode configurar sua visualização no ranking em chat privado.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await topadd(telegram_id, msg)


@dp.message(Command("status"))
async def handle_status(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await status(telegram_id, msg)


@dp.message(Command("trocar"))
async def handle_trocar(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type == "private":
        await msg.reply("⚙️ Oops, você só pode fazer trocas em grupos.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await trocar(telegram_id, msg, bot)


@dp.message(Command("doar"))
async def handle_doar(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type == "private":
        await msg.reply("⚙️ Oops, você só pode fazer doações em grupos.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await doar(telegram_id, msg)


@dp.message(Command("doarsemente"))
async def handle_doars(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type == "private":
        await msg.reply("⚙️ Oops, você só pode fazer doações em grupos.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await doarsemente(telegram_id, msg)


@dp.message(Command("doarcolheita"))
async def handle_doarc(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type == "private":
        await msg.reply("⚙️ Oops, você só pode fazer doações em grupos.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await doarcolheita(telegram_id, msg)


@dp.message(Command("doarinv"))
async def handle_doarinv(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type == "private":
        await msg.reply("⚙️ Oops, você só pode fazer doações em grupos.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await doarinv(telegram_id, msg)


@dp.message(Command("doarcat"))
async def handle_doarcat(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type == "private":
        await msg.reply("⚙️ Oops, você só pode fazer doações em grupos.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await doarcat(telegram_id, msg)


@dp.message(Command("doarcol"))
async def handle_doarcol(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type == "private":
        await msg.reply("⚙️ Oops, você só pode fazer doações em grupos.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await doarcol(telegram_id, msg)


@dp.message(Command("doartag"))
async def handle_doartag(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type == "private":
        await msg.reply("⚙️ Oops, você só pode fazer doações em grupos.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await doartag(telegram_id, msg)


@dp.message(Command("doarwish"))
async def handle_doarwish(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type == "private":
        await msg.reply("⚙️ Oops, você só pode fazer doações em grupos.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await doarwish(telegram_id, msg)


@dp.message(Command("descartar"))
async def handle_descartar(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode descartar cartas em chat privado.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await descartar(telegram_id, msg)


@dp.message(Command("descartarsub"))
async def handle_descartarsub(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode descartar uma subcategoria em chat privado.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await descartarsub(telegram_id, msg)


@dp.message(Command("descartarcat"))
async def handle_descartarcat(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode descartar uma categoria em chat privado.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await descartarcat(telegram_id, msg)


@dp.message(Command("saborear"))
async def handle_saborear(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode saborear uma subcategoria em chat privado.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await saborear(telegram_id, msg)


@dp.message(Command("lojinha"))
async def handle_lojinha(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username = await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode visitar a lojinha em chat privado.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await lojinha(bot, msg)


@dp.message(Command("casar"))
async def handle_casar(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await casar(telegram_id, msg, bot)


@dp.message(Command("wish"))
async def handle_wish(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await wish(telegram_id, msg, bot)


@dp.message(Command(commands=["wishlist", "wl"]))
async def handle_wishlist(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await wishlist(telegram_id, msg)


@dp.message(Command(commands=["berryin"]))
async def handle_berryin(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await berryin(telegram_id, msg)


@dp.message(Command(commands=["berryout"]))
async def handle_berryout(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await berryout(telegram_id, msg)


@dp.message(Command(commands=["laranja"]))
async def handle_laranja(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await laranja(telegram_id, msg, bot)


@dp.message(Command(commands=["recolher"]))
async def handle_recolher(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await recolher(telegram_id, msg)


@dp.message(Command(commands=["desvinc", "desvincular"]))
async def handle_disconnect(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await desvinc(telegram_id, msg)


@dp.message(Command(commands=["laranjas"]))
async def handle_laranjas(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await laranjas(telegram_id, msg)


@dp.message(Command("midia"))
async def handle_midia(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username =  await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode adicionar mídias em chat privado.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await midia(telegram_id, msg, bot)

@dp.message(Command("perfil"))
async def handle_perfil(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username =  await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await perfil(telegram_id, msg, bot)

@dp.message(Command("receita"))
async def handle_receita(msg: Message, state: FSMContext):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    username =  await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode customizar seu perfil em chat privado.")
        return

    if await is_banned(telegram_id, msg) == False and username:
        await receita(msg, state)

@dp.message(Command(commands=["setbio", "setfav", "setcol", "card1", "card2", "card3"]))
async def handle_wishlist(msg: Message, state: FSMContext):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    username = await attuser(telegram_id, msg)

    if await is_banned(telegram_id, msg) == False and username:
        await receita_process(msg, state)


# -------------------------------------------
# COMANDOS DE ADMINISTRADORES

@dp.message(Command("addsub"))
async def handle_addsub(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)

    await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode adicionar uma subcategoria em chat privado.")
    else:
        await addsub(telegram_id, msg)


@dp.message(Command("editsub"))
async def handle_editsub(msg: Message, state: FSMContext):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode editar uma subcategoria em chat privado.")
    else:
        await editsub(telegram_id, msg, state)


@dp.message(Command("criartag"))
async def handle_criartag(msg: Message, state: FSMContext):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode criar uma tag em chat privado.")
    else:
        await criartag(telegram_id, msg, state)


@dp.message(Command("editag"))
async def handle_editag(msg: Message, state: FSMContext):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode editar uma tag em chat privado.")
    else:
        await editag(telegram_id, msg, state)


@dp.message(Command("addtag"))
async def handle_addtag(msg: Message, state: FSMContext):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode adicionar cartas em uma tag em chat privado.")
    else:
        await addtag(telegram_id, msg, state)


@dp.message(Command("removetag"))
async def handle_removetag(msg: Message, state: FSMContext):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode remover cartas de uma tag em chat privado.")
    else:
        await removetag(telegram_id, msg, state)


@dp.message(Command("addcard"))
async def handle_addcard(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode adicionar uma carta em chat privado.")
    else:
        await addcard(telegram_id, msg)


@dp.message(Command("editcard"))
async def handle_editcard(msg: Message, state: FSMContext):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode editar uma carta em chat privado.")
    else:
        await editcard(telegram_id, msg, state)


@dp.message(Command("checar"))
async def handle_checar(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    await attuser(telegram_id, msg)
    await checar(telegram_id, bot, msg)


@dp.message(Command("reset"))
async def handle_reset(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    await attuser(telegram_id, msg)
    await reset(telegram_id, bot, msg)


@dp.message(Command("ban"))
async def handle_ban(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    await attuser(telegram_id, msg)
    await ban(telegram_id, bot, msg)


@dp.message(Command("desban"))
async def handle_desban(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    await attuser(telegram_id, msg)
    await desban(telegram_id, bot, msg)


@dp.message(Command("girados"))
async def handle_girados(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    await attuser(telegram_id, msg)
    await girados(telegram_id, bot, msg)


@dp.message(Command("allberry"))
async def handle_allberry(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    await attuser(telegram_id, msg)
    await allberry(telegram_id, msg)


@dp.message(Command("fermentar"))
async def handle_fermentar(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    await attuser(telegram_id, msg)
    await fermentar(telegram_id, bot, msg)


@dp.message(Command("fermentarall"))
async def handle_fermentarall(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    await attuser(telegram_id, msg)
    await fermentarall(telegram_id, bot, msg)


@dp.message(Command("presentear"))
async def handle_presentear(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    await attuser(telegram_id, msg)
    await presentear(telegram_id, msg)


@dp.message(Command("remove"))
async def handle_remove(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    await attuser(telegram_id, msg)
    await remove(telegram_id, msg)


@dp.message(Command("depositar"))
async def handle_depositar(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    await attuser(telegram_id, msg)
    await depositar(telegram_id, bot, msg)


@dp.message(Command("depositarall"))
async def handle_depositarall(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    await attuser(telegram_id, msg)
    await depositarall(telegram_id, bot, msg)


@dp.message(Command("regadm"))
async def handle_regadm(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    await attuser(telegram_id, msg)
    await regadm(telegram_id, msg)

@dp.message(Command(commands=["vinc", "vínculos", "vinculos"]))
async def handle_vinculos(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    await attuser(telegram_id, msg)
    await vinculos(telegram_id, msg)

@dp.message(Command("deletar"))
async def handle_deletar(msg: Message):
    if msg.sender_chat:
        await msg.reply("⚙️ Oops, a Vila Tutti-Frutti não aceita canais.")
        return

    telegram_id = msg.from_user.id
    chatid = msg.chat.id
    chat = await bot.get_chat(chatid)
    await attuser(telegram_id, msg)

    if chat.type != "private":
        await msg.reply("⚙️ Oops, você só pode deletar cards e subs em chat privado.")
    else:
        await deletar(telegram_id, msg, bot)

# -------------------------------------------
# INICIA O BOT

dp.include_router(admins)
dp.include_router(utils)
dp.include_router(users)
asyncio.run(dp.start_polling(bot))
