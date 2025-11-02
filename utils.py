import os
import telebot
import random
import math
import aiohttp
import io

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.types import Message, CallbackQuery
from io import BytesIO
from ftplib import FTP

from datetime import datetime, timedelta

from dotenv import load_dotenv
from conn import get_cursor
from states import Loja

load_dotenv()
emoji_numeros = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]

categoria_emojis = {
    "ASIAFARM": "🍇",
    "MORANGEEK": "🍏",
    "FRUITMIX": "🫐",
    "STREAMBERRY": "🍋"
}

raridade_emojis = {
    1: "🥇",
    2: "🥈",
    3: "🥉"
}

utils = Router()

# -------------------------------------------
# SELECIONA OS EMOJIS DA CESTA E TOP

def get_emoji(valor):
    if 10 <= valor <= 49:
        return "🌱" 
    elif 50 <= valor <= 99:
        return "🎀"
    elif 100 <= valor <= 499:
        return "🍯"
    elif 500 <= valor <= 999:
        return "🐑"
    elif 1000 <= valor <= 2499:
        return "🍉"
    elif 2500 <= valor <= 4999:
        return "👒"
    elif 5000 <= valor <= 9999:
        return "🌷"
    elif valor >= 10000:
        return "🍰"
    else:
        return ""

# -------------------------------------------
# ATUALIZA O USERNAME DO USUÁRIO
async def attuser(telegram_id, msg):
    if msg.from_user.username:
        async with get_cursor() as cursor:
            await cursor.execute("SELECT telegram_id, username FROM usuarios WHERE telegram_id = %s", (telegram_id,))
            result = await cursor.fetchone()

            if result:
                telegram_id = result[0]
                username = result[1] if result[1] is not None else 0

                if username != msg.from_user.username:
                    await cursor.execute("UPDATE usuarios SET username = %s WHERE telegram_id = %s", (msg.from_user.username, telegram_id,))    
                    await cursor.execute("SELECT parceiro FROM usuarios WHERE parceiro = %s", (username,))
                    casado = await cursor.fetchone()

                    if casado:
                        await cursor.execute("UPDATE usuarios SET parceiro = %s WHERE parceiro = %s", (username, msg.from_user.username,))
        return True
    else:
        await msg.reply("⚙️ Oops, você só pode usar o bot se tiver um username no Telegram.")
        return False
    
# -------------------------------------------
# VERIFICA SE O USUÁRIO É ADM
async def is_admin(telegram_id, msg):
    admins = os.getenv("ADMINS", "").split(",")
    txt_id = str(telegram_id)

    if txt_id in admins:
        return True
    else:
        if isinstance(msg, Message):
            await msg.reply(f"⚙️ Oops, @{msg.from_user.username}! Somente administradores podem usar esse comando.")
        elif isinstance(msg, CallbackQuery):
            await msg.answer(f"⚙️ Oops, você não é um ADM.")

# -------------------------------------------
# VERIFICA SE O USUÁRIO ESTÁ BANIDO
async def is_banned(telegram_id, msg, user = 0):
    async with get_cursor() as cursor:
        await cursor.execute("SELECT telegram_id, username FROM banidos WHERE telegram_id = %s", (telegram_id,))
        result = await cursor.fetchone()

        if not result:
            return False

        telegram_id = result[0]
        username = result[1] if result[1] else 0

        if username != user:
            await cursor.execute("UPDATE banidos SET username = %s WHERE telegram_id = %s", (user, telegram_id,))

        if user == 0:
            user = msg.from_user.username
            if isinstance(msg, Message):
                await msg.reply(f"⚙️ Oops, @{msg.from_user.username}, você foi expulso da Vila Tutti-Frutti.")
            elif isinstance(msg, CallbackQuery):
                await msg.answer(f"⚙️ Oops, @{msg.from_user.username}, você foi expulso da Vila Tutti-Frutti.")
                
        return True

# -------------------------------------------
# MONTA O PAINEL DE BOTÕES DE CATEGORIAS
async def painel_categorias(action):
    categorias = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="ASIAFARM 🍇", callback_data=f'{action}_ASIAFARM'),
                InlineKeyboardButton(text="STREAMBERRY 🍋", callback_data=f'{action}_STREAMBERRY')
            ],
            [
                InlineKeyboardButton(text="FRUITMIX 🫐", callback_data=f'{action}_FRUITMIX'),
                InlineKeyboardButton(text="MORANGEEK 🍏", callback_data=f'{action}_MORANGEEK')
            ]
        ]
    )
    return categorias

# -------------------------------------------
# VERIFICA SE A TAG EXISTE NO BD
async def exist_tag(tag):
    async with get_cursor() as cursor:
        await cursor.execute("SELECT * FROM tags WHERE nome = %s", (tag,))
        result = await cursor.fetchone()

    if result:
        return result
    else:
        return False

# -------------------------------------------
# VERIFICA SE A CARTA EXISTE NO BD
async def exist_card(card, msg):
    async with get_cursor() as cursor:
        try:
            card = int(card)
            await cursor.execute("SELECT * FROM cartas WHERE id = %s", (card,))
        except ValueError:
            await cursor.execute("SELECT * FROM cartas WHERE nome = %s LIMIT 1", (card,))
        result = await cursor.fetchone()

    if result:
        return result
    else:
        await msg.reply("⚙️ Oops, parece que esse card não existe.")
        return False

# -------------------------------------------
# VERIFICA SE A CARTA ESTÁ REGISTRADA EM UMA CAT ESPECÍFICA
async def exist_card_in_cat(card, cat):
    async with get_cursor() as cursor:
        try:
            card = int(card)
            await cursor.execute("SELECT * FROM cartas WHERE id = %s AND categoria = %s LIMIT 1", (card, cat,))
        except ValueError:
            await cursor.execute("SELECT * FROM cartas WHERE nome = %s AND categoria = %s LIMIT 1", (card, cat,))
        result = await cursor.fetchall()

    if result:
        return True
    else:
        return False

# -------------------------------------------
# VERIFICA SE A CARTA ESTÁ REGISTRADA EM UMA SUB ESPECÍFICA
async def exist_card_in_sub(card, msg, sub):
    async with get_cursor() as cursor:
        await cursor.execute("SELECT * FROM cartas WHERE nome = %s AND subcategoria = %s LIMIT 1", (card, sub,))
        result = await cursor.fetchall()

    if result:
        await msg.reply("⚙️ Oops, parece que esse card já existe nessa subcategoria. Operação cancelada.")
    else:
        return False

# -------------------------------------------
# VERIFICA SE UMA SUB EXISTE
async def exist_sub(sub, msg):
    async with get_cursor() as cursor:
        await cursor.execute("SELECT * FROM divisoes WHERE subcategoria = %s", (sub,))
        result = await cursor.fetchone()

        if not result:
            await cursor.execute("SELECT * FROM divisoes WHERE FIND_IN_SET(%s, shortner)", (sub,))
            result = await cursor.fetchone()

    if result:
        return result
    else:
        await msg.reply("⚙️ Oops, não encontrei resultados para essa subcategoria.")
        return False
    
# -------------------------------------------
# VERIFICA SE UMA SUB EXISTE DENTRO DE UMA CATEGORIA ESPECÍFICA
async def exist_sub_in_cat(cat, sub):
    async with get_cursor() as cursor:
        await cursor.execute("SELECT * FROM divisoes WHERE categoria = %s AND subcategoria = %s", (cat, sub,))
        result = await cursor.fetchone()

    if result:
        return result
    else:
        return False

# -------------------------------------------
# CONTA QUANTO DE UMA CARTA ESPECÍFICA UM USER TEM
async def carta_user(id_user, carta, cursor=None):
    if cursor != None:
        try:
            carta = int(carta)
            await cursor.execute("SELECT quantidade FROM inventario WHERE id_user = %s AND id_carta = %s", (id_user, carta,))
            quantidade = await cursor.fetchone()
        except ValueError:
            await cursor.execute("SELECT id FROM cartas WHERE nome = %s", (carta,))
            result = await cursor.fetchone()
            id = result[0]
            await cursor.execute("SELECT quantidade FROM inventario WHERE id_user = %s AND id_carta = %s", (id_user, id,))
            quantidade = await cursor.fetchone()
    else:
        async with get_cursor() as cursor:
            try:
                carta = int(carta)
                await cursor.execute("SELECT quantidade FROM inventario WHERE id_user = %s AND id_carta = %s", (id_user, carta,))
                quantidade = await cursor.fetchone()
            except ValueError:
                await cursor.execute("SELECT id FROM cartas WHERE nome = %s", (carta,))
                result = await cursor.fetchone()
                id = result[0]
                await cursor.execute("SELECT quantidade FROM inventario WHERE id_user = %s AND id_carta = %s", (id_user, id,))
                quantidade = await cursor.fetchone()

    if quantidade is not None:
        return int(quantidade[0])
    else:
        return None

# -------------------------------------------
# MONTA O PAINEL DE SUBCATEGORIAS ALEATÓRIAS PARA COLHER
async def get_subcats(cat, bot, call):
    async with get_cursor() as cursor:
        await cursor.execute("SELECT subcategoria FROM divisoes WHERE categoria = %s", (cat,))
        sub_list = await cursor.fetchall()

    subcategorias = [sub[0] for sub in sub_list]
    random.shuffle(subcategorias)
    subcategorias = subcategorias[:6]

    lista = "\n".join([f"{i + 1}. {sub}" for i, sub in enumerate(subcategorias)])

    botoes = []
    for i, sub in enumerate(subcategorias):
        emoji = emoji_numeros[i] if i < len(emoji_numeros) else '❓' 
        botoes.append(InlineKeyboardButton(text=emoji, callback_data=f"subcat_{sub}"))

    subs = InlineKeyboardMarkup(inline_keyboard=[
        botoes[i:i+3] for i in range(0, len(botoes), 3)
    ])

    texto = f"{categoria_emojis.get(cat, '❓')} Que sorte! Quantos frutos disponíveis, qual você quer escolher? \n\n{lista}"

    await bot.edit_message_caption(
        caption=texto,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=subs
    )

# -------------------------------------------
# COLHE UMA CARTA ALEATÓRIA COM BASE NA RARIDADE
async def get_card(sub, bot, call):
    chances = [20, 30, 50]
    raridade_escolhida = random.choices([1, 2, 3], weights=chances, k=1)[0]

    async with get_cursor() as cursor:
        await cursor.execute("SELECT id, nome, raridade, imagem, categoria FROM cartas WHERE subcategoria = %s AND raridade = %s ORDER BY RAND() LIMIT 1", (sub, raridade_escolhida,))
        carta = await cursor.fetchone()

        if not carta and raridade_escolhida in (1, 3):
            await cursor.execute("SELECT id, nome, raridade, imagem, categoria FROM cartas WHERE subcategoria = %s AND raridade = %s ORDER BY RAND() LIMIT 1", (sub, 2,))
            carta = await cursor.fetchone()

            if not carta:
                await call.answer(f"⚙️ Oops, a colheita {sub} ainda não tem frutinhas.")
                return
        elif not carta:
            await call.answer(f"⚙️ Oops, a colheita {sub} ainda não tem frutinhas.")
            return
            
        await call.answer()
        id, nome, raridade, imagem, categoria = carta

        user_id = call.from_user.id

        nome_user = f"{call.from_user.first_name} {call.from_user.last_name or ''}".strip()
        nome_user = f"[{nome_user}](tg://user?id={user_id})"

        result = await carta_user(user_id, id, cursor)

        quantidade = result + 1 if result != None else 1

        texto = f"🍓 {nome_user}, após sua colheita, você conseguiu: \n\n{raridade_emojis.get(raridade, '❓')} `{id}`. {nome} \n{categoria_emojis.get(categoria, '❓')} {sub} \n\n🧺 Você possui {quantidade} dessa fruta."
        media = InputMediaPhoto(
            media=imagem,
            caption=texto
        )

        if result != None:
            await cursor.execute("UPDATE inventario SET quantidade = %s WHERE id_user = %s AND id_carta = %s", (quantidade, user_id, id))
        else:
            await cursor.execute("INSERT INTO inventario (id_user, id_carta, quantidade) VALUES (%s, %s, %s)", (user_id, id, 1))      

    await bot.edit_message_media(
        media=media,          
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )

# -------------------------------------------
# EFETUA COMPRA DE GIROS
@utils.message(StateFilter(Loja.giros))
async def compragiros(msg, state):
    try:
        giros = int(msg.text)

        if giros == 0:
            await msg.reply("⚙️ Certo, compra cancelada. Não se preocupe, nenhuma semente foi descontada.")
            return

        gasto = giros * 1000
        id = msg.from_user.id

        async with get_cursor() as cursor:
            await cursor.execute("SELECT sementes FROM usuarios WHERE telegram_id = %s", (id,))
            result = await cursor.fetchone()

            sementes = result[0] if result[0] else 0

            if sementes < gasto:
                await msg.reply("⚙️ Oops, você não tem sementes suficientes para essa compra.")
                await state.clear()
                return
            else:
                await cursor.execute("UPDATE usuarios SET sementes = sementes - %s WHERE telegram_id = %s", (gasto, id,))
                await cursor.execute("UPDATE usuarios SET giros = giros + %s WHERE telegram_id = %s", (giros, id,))

        nome = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
        nome = f"[{nome}](tg://user?id={id})"
        await msg.reply(f"🌾 Certo, {nome}, sua compra de {giros} giros foi feita com sucesso! O total de {gasto} sementes foi gasto.")
        await state.clear()

    except ValueError:
        await msg.reply("⚙️ Oops, parece que você não informou um número válido de giros.")
        await state.clear()

# -------------------------------------------
# EFETUA COMPRA DE VIP
@utils.message(StateFilter(Loja.vip))
async def compravip(msg, state):
    if msg.text == "/confirmar":
        id = msg.from_user.id

        async with get_cursor() as cursor:
            await cursor.execute("SELECT sementes FROM usuarios WHERE telegram_id = %s", (id,))
            result = await cursor.fetchone()

            sementes = result[0] if result[0] else 0

            if sementes < 150000:
                await msg.reply("⚙️ Oops, você ainda não tem sementes suficientes para se tornar um jardineiro VIP.")
                await state.clear()
            else:
                await cursor.execute("UPDATE usuarios SET vip = 1 WHERE telegram_id = %s", (id,))
                await cursor.execute("UPDATE usuarios SET sementes = sementes - 150000 WHERE telegram_id = %s", (id,))

                grupoofc = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text="🍁", callback_data=f'grupoofc')
                        ]
                    ]
                )

                await msg.reply("Parabéns! Você é oficialmente um jardineiro VIP da Vila Tutti-Frutti. 🎟️\n\n— Entre no nosso grupo oficial clicando no botão abaixo, onde teremos sorteios e dinâmicas semanais para vocês.", reply_markup=grupoofc)
                await state.clear()
    else:
        await msg.reply("🌿 Certo, compra cancelada! Infelizmente você continua sendo um jardineiro comum.")
        await state.clear()

# -------------------------------------------
# EFETUA COMPRA DE DIVÓRCIO
@utils.message(StateFilter(Loja.divorcio))
async def divorciar(msg, state, bot):
    if msg.text == "/confirmar":
        id = msg.from_user.id
        dados = await state.get_data()
        parceiro = dados.get('parceiro')

        async with get_cursor() as cursor:
            await cursor.execute("SELECT sementes FROM usuarios WHERE telegram_id = %s", (id,))
            result = await cursor.fetchone()

            sementes = result[0] if result[0] else 0

            if sementes < 2500:
                await msg.reply("⚙️ Oops, você não tem sementes suficientes para arcar com os custos do divórcio.")
                await state.clear()
            else:
                await cursor.execute("SELECT telegram_id FROM usuarios WHERE username = %s", (parceiro,))
                result = await cursor.fetchone()
                ex = result[0]

                await cursor.execute("UPDATE usuarios SET parceiro = %s WHERE telegram_id = %s", (None, id,))
                await cursor.execute("UPDATE usuarios SET parceiro = %s WHERE username = %s", (None, parceiro,))
                await cursor.execute("UPDATE usuarios SET sementes = sementes - 2500 WHERE telegram_id = %s", (id,))

                await msg.reply("🪻 Você está oficialmente solteiro outra vez! Explore a Vila Tutti-Frutti e, quem sabe, desenvolva uma nova paixão.")
                await bot.send_message(ex, f"🪻 Oh, más notícias... @{msg.from_user.username} acabou de oficializar o divórcio, finalizando o casamento de vocês. Porém não se preocupe, você pode encontrar outro alguém especial!")
                await state.clear()
    else:
        await msg.reply("🪻 Certo, divórcio cancelado. Esperamos que seu casamento continue florecendo!")
        await state.clear()

# -------------------------------------------
# PASSOS PARA EFETUAR COMPRA DE CAIXINHA
async def caixinhacat(msg, state, bot, cat):
    await bot.send_message(msg.from_user.id, f"{categoria_emojis.get(cat, '❓')} Certo, caixinha da categoria {cat}! Agora envie /confirmar seguido dos 5 IDs de sua preferência para prosseguir, todos pertencentes a essa categoria e sem repetições.")
    await state.update_data(cat=cat)
    await state.set_state(Loja.caixinha)

@utils.message(StateFilter(Loja.caixinha))
async def caixinha(msg, state, bot):
    confirm = msg.text.split()

    if confirm[0] == "/confirmar":
        if len(confirm) != 6:
            await msg.reply("⚙️ Oops, você precisa enviar exatamente 5 IDs após a confirmação. Compra cancelada.")
            await state.clear()
            return
        else:
            try:
                ids = [int(n) for n in confirm[1:]]

                if len(set(ids)) != len(ids):
                    await msg.reply("⚙️ Oops, você não pode repetir nenhum ID. Compra cancelada.")
                    await state.clear()
                    return
            except ValueError:
                await msg.reply("⚙️ Oops, só são aceitos IDs numéricos.")
                await state.clear()
                return
        
        dados = await state.get_data()
        cat = dados.get('cat')   
        for i in ids:
            result = await exist_card_in_cat(i, cat)

            if not result:
                await msg.reply(f"⚙️ Oops, parece que algum dos IDs não existe dentro da categoria {cat}.")
                await state.clear()
                return
 
        garantido = random.choice(ids)
        boost = [i for i in ids if i != garantido]
        chances = [20, 30, 50]

        user = await bot.get_chat(msg.from_user.id)
        nome = f"{user.first_name} {user.last_name or ''}".strip()
        nome = f"[{nome}](tg://user?id={msg.from_user.id})"

        texto = f"🗳️ Sua caixinha chegou, {nome}! Aqui estão as frutas que conseguiu:\n"
        texto2 = ""
        texto3 = ""

        async with get_cursor() as cursor:
            await cursor.execute("SELECT nome, subcategoria FROM cartas WHERE id = %s", (garantido,))
            carta = await cursor.fetchone()
            Gcards = await carta_user(msg.from_user.id, garantido, cursor)

            texto += f"\n🏅 `{garantido}`. {carta[0]} — {carta[1]} (`{Gcards}`x)."

            for _ in range(14):
                chance_extra = random.random()

                if chance_extra <= 0.3:
                    escolhida = random.choice(boost)
                    await cursor.execute("SELECT id, nome, raridade, subcategoria FROM cartas WHERE categoria = %s AND id = %s", (cat, escolhida,))
                    carta = await cursor.fetchone()
                else:
                    raridade_escolhida = random.choices([1, 2, 3], weights=chances, k=1)[0]
                    await cursor.execute("SELECT id, nome, raridade, subcategoria FROM cartas WHERE categoria = %s AND raridade = %s ORDER BY RAND() LIMIT 1", (cat, raridade_escolhida,))
                    carta = await cursor.fetchone()

                    if not carta:
                        await cursor.execute("SELECT id, nome, raridade, subcategoria FROM cartas WHERE categoria = %s AND raridade = %s ORDER BY RAND() LIMIT 1", (cat, 2,))
                        carta = await cursor.fetchone()

                Ncards = await carta_user(msg.from_user.id, carta[0], cursor)

                if Ncards == None:
                    Ncards = 1
                    await cursor.execute("INSERT INTO inventario (id_user, id_carta, quantidade) VALUES (%s, %s, %s)", (msg.from_user.id, carta[0], Ncards))      
                else:
                    Ncards += 1
                    await cursor.execute("UPDATE inventario SET quantidade = %s WHERE id_user = %s AND id_carta = %s", (Ncards, msg.from_user.id, carta[0],))

                match carta[2]:
                    case 1:
                        texto += f"\n{raridade_emojis.get(carta[2], '❓')} `{carta[0]}`. {carta[1]} — {carta[3]} (`{Ncards}`x)."
                    case 2:
                        texto2 += f"\n{raridade_emojis.get(carta[2], '❓')} `{carta[0]}`. {carta[1]} — {carta[3]} (`{Ncards}`x)."
                    case 3:
                        texto3 += f"\n{raridade_emojis.get(carta[2], '❓')} `{carta[0]}`. {carta[1]} — {carta[3]} (`{Ncards}`x)."
            
            texto += texto2
            texto += texto3

            await cursor.execute("UPDATE usuarios SET sementes = sementes - 10000 WHERE telegram_id = %s", (msg.from_user.id,))
            await msg.reply(texto)
            await state.clear()
    else:
        await msg.reply("⚙️ Certo, compra cancelada. Nenhuma semente foi descontada.")
        await state.clear()

# -------------------------------------------
# FUNÇÃO PARA PEGAR WISHLIST
async def get_wl(telegram_id, cat = 0):
    async with get_cursor() as cursor:
        if cat == 0:
            await cursor.execute("SELECT id_carta FROM wishlists WHERE id_user = %s", (telegram_id,))
            result = await cursor.fetchall()
        else:
            await cursor.execute("SELECT id_carta FROM wishlists WHERE id_user = %s AND categoria = %s", (telegram_id, cat,))
            result = await cursor.fetchall()

    if result:
        return result
    else:
        return None

# -------------------------------------------
# SUBIR MÍDIAS NO BUNNY
async def up_bunny(card, tlid, link, tipo):
    USER = os.getenv("BUNNYUSER")
    SENHA = os.getenv("BUNNYSENHA")

    ftp = FTP()
    ftp.connect('br.storage.bunnycdn.com', 21)
    ftp.login(user=USER, passwd=SENHA)
    ftp.set_pasv(True)

    if tlid != 0:
        midia = f"{tlid}_{card}"
        
        try:
           ftp.delete(f"midiasesp/{midia}.mp4")
        except Exception as e:
            print(f"⚠️ Não foi possível apagar: {e}")

        try:
            ftp.delete(f"midiasesp/{midia}.jpg")
        except Exception as e:
            print(f"⚠️ Não foi possível apagar: {e}")
    else:
        midia = f"{card}"
        if isinstance(card, str):
            midia = card.replace(" ", "-")
            tipo = "sub"
            try:
                ftp.delete(f"midias/subs/{midia}.jpg")
            except Exception as e:
                print(f"⚠️ Não foi possível apagar: {e}")
        else:
            tipo = "card"
            try:
                ftp.delete(f"midias/cards/{midia}.jpg")
            except Exception as e:
                print(f"⚠️ Não foi possível apagar: {e}")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            if resp.status == 200:
                conteudo = await resp.read()
                buffer = io.BytesIO(conteudo)
                buffer.seek(0)
                
                if tlid != 0: 
                    ftp.storbinary(f"STOR midiasesp/{midia}.{tipo}", buffer)
                    ftp.quit()
                    
                    upload = f"https://berrypull.b-cdn.net/midiasesp/{midia}.{tipo}"
                else:
                    if tipo == "sub":
                        ftp.storbinary(f"STOR midias/subs/{midia}.jpg", buffer)
                        ftp.quit()
                        
                        upload = f"https://berrypull.b-cdn.net/midias/subs/{midia}.jpg"
                    else:
                        ftp.storbinary(f"STOR midias/cards/{midia}.jpg", buffer)
                        ftp.quit()
                        
                        upload = f"https://berrypull.b-cdn.net/midias/cards/{midia}.jpg"
                return upload
            else:
                print(f"❌ Erro no upload para Bunny.")
                return False
    
# -------------------------------------------
# BUSCAR MÍDIA ESPECIAL
async def midiaesp(card, tlid):
    async with get_cursor() as cursor:
        await cursor.execute("SELECT midia, tipo FROM midiasesp WHERE id_user = %s AND id_carta = %s", (tlid, card,))
        midia = await cursor.fetchone()
    
    if midia:
        return midia
    else:
        return False
    
# -------------------------------------------
# LIDA COM TODOS OS CLIQUES EM BOTÕES DO BOT
last_inline_click_time = {}
inline_click_cooldown = timedelta(seconds=3)

async def callback_query_func(call, bot, state):
    try:
        data = call.data
        chat_id = call.message.chat.id
        msg_id = call.message.message_id
        user_id = call.from_user.id
        now = datetime.now()

        if user_id in last_inline_click_time:
            if call.data in last_inline_click_time[user_id]:
                last_click_time = last_inline_click_time[user_id][call.data]
                if now - last_click_time < inline_click_cooldown:
                    await call.answer("⏱️ Não sobrecarregue o Berry com tantos cliques!")
                    return

        if user_id not in last_inline_click_time:
            last_inline_click_time[user_id] = {}
        last_inline_click_time[user_id][call.data] = now

        match data:
            case "cancelar":
                await bot.delete_message(chat_id, msg_id)
                
            case "addsub_ASIAFARM" | "addsub_MORANGEEK" | "addsub_STREAMBERRY" | "addsub_FRUITMIX":
                from admins import resposta_cat
                await call.answer()
                await resposta_cat(call, bot, state)
                await bot.delete_message(chat_id, msg_id)

            case "addcard_ASIAFARM" | "addcard_MORANGEEK" | "addcard_STREAMBERRY" | "addcard_FRUITMIX":
                from admins import card_cat
                await call.answer()
                await card_cat(call, bot, state)
                await bot.delete_message(chat_id, msg_id)
            
            case "colher_ASIAFARM" | "colher_MORANGEEK" | "colher_STREAMBERRY" | "colher_FRUITMIX":
                cat = data.split('_')[1]
                await call.answer()
                await get_subcats(cat, bot, call)
            
            case "caixinha_ASIAFARM" | "caixinha_MORANGEEK" | "caixinha_STREAMBERRY" | "caixinha_FRUITMIX":
                cat = data.split('_')[1]
                await call.answer()
                await bot.delete_message(chat_id, msg_id)
                await caixinhacat(call, state, bot, cat)

            case _ if data.split('_')[0] == "midiarep":
                _, motivo, tlid, card = data.split('_')
                
                resposta = f"🍎 Sua mídia para a frutinha `{card}` foi reprovada. Motivo: "
                match motivo:
                    case "flash":
                        resposta += "sua mídia contém muitos flashes."
                    case "cont":
                        resposta += "sua mídia contém conteúdo sensível."
                    case "outro":
                        resposta += "porque eu quis."
                await bot.send_message(tlid, resposta)

                texto = "🍎 Sua reprovação e justificativa foram enviadas com sucesso."
                await bot.edit_message_caption(
                    caption=texto,
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id
                )

            case _ if data.split('_')[0] == "midia":
                _, acao, tlid, card = data.split('_')

                if acao == "rec":
                    texto = "🎥 Escolha o motivo da reprovação dentre as opções abaixo:"

                    rep = InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(text="FLASH 📸", callback_data=f"midiarep_flash_{tlid}_{card}"),
                            InlineKeyboardButton(text="CONTEÚDO 🎞️", callback_data=f"midiarep_cont_{tlid}_{card}")
                        ],
                        [
                            InlineKeyboardButton(text="OUTRO 📌", callback_data=f"midiarep_outro_{tlid}_{card}")
                        ]
                    ])

                    await bot.edit_message_caption(
                        caption=texto,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=rep
                    )
                else:
                    TOKEN = os.getenv("TOKEN")
                    mensagem = call.message

                    if mensagem.photo:
                        file = await bot.get_file(mensagem.photo[-1].file_id)
                        tipo = "jpg"
                        arq = "foto"
                    elif mensagem.video:
                        file_id = mensagem.video.file_id
                        file = await bot.get_file(file_id)
                        tipo = "mp4"
                        arq = "video"

                    path = file.file_path
                    url = f"https://api.telegram.org/file/bot{TOKEN}/{path}"

                    bunny = await up_bunny(card, tlid, url, tipo)
                        
                    if bunny:
                        texto = "🍏 A mídia foi aprovada com sucesso!"
                        resposta = f"🍏 A sua mídia para a frutinha `{card}` foi aprovada com sucesso!"

                        async with get_cursor() as cursor:
                            if await midiaesp(card, tlid):
                                    await cursor.execute("UPDATE midiasesp SET midia = %s, tipo = %s WHERE id_user = %s AND id_carta = %s", (bunny, arq, tlid, card,))
                            else:
                                await cursor.execute("INSERT INTO midiasesp (id_user, id_carta, midia, tipo) VALUES (%s, %s, %s, %s, %s)", (tlid, card, bunny, arq,))
                    else:
                        texto = "⚙️ Oops, houve algum erro ao tentar fazer upload da mídia."
                        resposta = f"⚙️ Oops, houve algum erro ao aprovar sua mídia para a frutinha `{card}`. Tente novamente!" 

                    await bot.edit_message_caption(
                            caption=texto,
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id
                        )
                    await bot.send_message(tlid, resposta)

            case "troca_neg":
                from states import em_troca
                troca = em_troca.get(user_id)

                if not troca:
                    await call.answer("🍎 Oops, você não faz parte dessa troca.")
                    return
                elif troca["msg_id"] != msg_id:
                    await call.answer("🍎 Oops, você não faz parte dessa troca.")
                    return
                else:
                    await call.answer()
                    await bot.send_message(chat_id, f"🍎 Certo, a troca foi recusada.")

                    user1 = troca["user1"]
                    user2 = troca["user2"]
                    em_troca.pop(user1, None)
                    em_troca.pop(user2, None)
                
                    await state.clear()
                    await bot.delete_message(chat_id, msg_id)
        
            case "troca_confirm":
                from states import em_troca
                troca = em_troca.get(user_id)

                if not troca:
                    await call.answer("🍎 Oops, você não faz parte dessa troca.")
                    return
                elif troca["msg_id"] != msg_id:
                    await call.answer("🍎 Oops, você não faz parte dessa troca.")
                    return
                elif user_id != troca["user2"]:
                    await call.answer("🍎 Oops, somente seu parceiro pode aceitar a troca.")
                    return
                else:
                    user1 = troca["user1"]
                    n1 = await bot.get_chat(user1)
                    nome1 = f"{n1.first_name} {n1.last_name or ''}".strip()
                    nome1 = f"[{nome1}](tg://user?id={user1})"

                    user2 = troca["user2"]
                    n2 = await bot.get_chat(user2)
                    nome2 = f"{n2.first_name} {n2.last_name or ''}".strip()
                    nome2 = f"[{nome2}](tg://user?id={user2})"
                    
                    pares1 = troca["pares1"]
                    pares2 = troca["pares2"]

                    texto = f"🌻 Troca realizada com sucesso!\n"
                    texto += f"\n{nome2} recebeu:"

                    imagem = FSInputFile("assets\\trocado.jpg")

                    async with get_cursor() as cursor:
                        for id, qtd in pares1:
                            await cursor.execute("SELECT quantidade FROM inventario WHERE id_carta = %s AND id_user = %s", (id, user2,))
                            result = await cursor.fetchone()

                            if result is None:
                                await cursor.execute("INSERT INTO inventario (id_user, id_carta, quantidade) VALUES (%s, %s, %s)", (user2, id, qtd,))
                            else:
                                await cursor.execute("UPDATE inventario SET quantidade = quantidade + %s WHERE id_user = %s AND id_carta = %s", (qtd, user2, id,))

                            Ncards = await carta_user(user1, id, cursor)
                            valor = Ncards - qtd

                            if valor == 0:
                                await cursor.execute("DELETE FROM inventario WHERE id_carta = %s AND id_user = %s", (id, user1,))
                            else:
                                await cursor.execute("UPDATE inventario SET quantidade = quantidade - %s WHERE id_carta = %s AND id_user = %s", (qtd, id, user1,))
                            
                            await cursor.execute("INSERT INTO extrato (remetente, receptor, comando, carta, quantidade) VALUES(%s, %s, %s, %s, %s)", (user1, user2, "trocar", id, qtd,))
                            await cursor.execute("SELECT nome, raridade FROM cartas WHERE id = %s", (id,))
                            carta = await cursor.fetchone()

                            texto += f"\n{raridade_emojis.get(carta[1], '❓')} `{id}`. {carta[0]} ({qtd}x)"
                        
                        texto += f"\n\n{nome1} recebeu:"

                        for id, qtd in pares2:
                            await cursor.execute("SELECT quantidade FROM inventario WHERE id_carta = %s AND id_user = %s", (id, user1,))
                            result = await cursor.fetchone()

                            if result is None:
                                await cursor.execute("INSERT INTO inventario (id_user, id_carta, quantidade) VALUES (%s, %s, %s)", (user1, id, qtd,))
                            else:
                                await cursor.execute("UPDATE inventario SET quantidade = quantidade + %s WHERE id_user = %s AND id_carta = %s", (qtd, user1, id,))

                            Ncards = await carta_user(user2, id, cursor)
                            valor = Ncards - qtd

                            if valor == 0:
                                await cursor.execute("DELETE FROM inventario WHERE id_carta = %s AND id_user = %s", (id, user2,))
                            else:
                                await cursor.execute("UPDATE inventario SET quantidade = quantidade - %s WHERE id_carta = %s AND id_user = %s", (qtd, id, user2,))

                            await cursor.execute("INSERT INTO extrato (remetente, receptor, comando, carta, quantidade) VALUES(%s, %s, %s, %s, %s)", (user2, user1, "trocar", id, qtd,))
                            await cursor.execute("SELECT nome, raridade FROM cartas WHERE id = %s", (id,))
                            carta = await cursor.fetchone()

                            texto += f"\n{raridade_emojis.get(carta[1], '❓')} `{id}`. {carta[0]} ({qtd}x)"

                    await call.answer()

                    media = InputMediaPhoto(
                        media=imagem,
                        caption=texto
                    )
                    
                    await bot.edit_message_media(
                        media=media,          
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id
                    )

                    em_troca.pop(user1, None)
                    em_troca.pop(user2, None)
                
            case _ if data.split('_')[0] == "subcat":
                sub = data.split('_')[1]
                await get_card(sub, bot, call)

            case _ if data.split('_')[0] == "editimgsub":
                from states import Esub
                sub = data.split('_')[1]

                await call.answer()
                await bot.send_message(chat_id, f"Certo, envie uma nova imagem para a subcategoria {sub}.")
                await state.set_state(Esub.foto)
                await bot.delete_message(chat_id, msg_id)

            case _ if data.split('_')[0] == "editnomesub":
                from states import Esub
                sub = data.split('_')[1]

                await call.answer()
                await bot.send_message(chat_id, f"Certo, envie um novo nome para a subcategoria {sub}.")
                await state.set_state(Esub.nome)
                await bot.delete_message(chat_id, msg_id)
            
            case _ if data.split('_')[0] == "editvarsub":
                from states import Esub
                sub = data.split('_')[1]
                action = data.split('_')[2]

                if action == "add":
                    await call.answer()
                    await bot.send_message(chat_id, f"Certo, envie as novas variações desejadas para a subcategoria {sub}, todas separadas por vírgula. Variações com espaço não serão aceitas.")
                    await state.set_state(Esub.addvar)
                    await bot.delete_message(chat_id, msg_id)
                elif action == "remove":
                    async with get_cursor() as cursor:
                        await cursor.execute("SELECT shortner FROM divisoes WHERE subcategoria = %s", (sub,))
                        haveshortner = await cursor.fetchone()
                        
                        if not haveshortner[0]:
                            await call.answer(f"⚙️ Oops, essa sub não tem nenhuma variação.")
                            return
                        else:
                            await call.answer()               
                            atualshortner = haveshortner[0]
                            await state.update_data(atualshortner=atualshortner)
                            await bot.send_message(chat_id, f"Certo, envie as variações que deseja remover da subcategoria {sub}, todas separadas por vírgula.")
                            await state.set_state(Esub.removevar)
                            await bot.delete_message(chat_id, msg_id)
                else:
                    ações = InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(text="📌 ADICIONAR", callback_data=f"editvarsub_{sub}_add"),
                            InlineKeyboardButton(text="📌 REMOVER", callback_data=f"editvarsub_{sub}_remove")
                        ]
                    ])

                    await call.answer()
                    texto = f"🍑 Certo, ADM @{call.from_user.username}! Escolha se deseja adicionar ou remover variações de nome da sub {sub}."
                    await bot.edit_message_text(
                        text=texto,
                        chat_id=chat_id,
                        message_id=msg_id,
                        reply_markup=ações
                    )
            
            case _ if data.split('_')[0] == "editnometag":
                from states import Etag
                tag = data.split('_')[1]

                await call.answer()
                await bot.send_message(chat_id, f"Certo, envie um novo nome para a tag {tag}.")
                await state.set_state(Etag.nome)
                await bot.delete_message(chat_id, msg_id)
            
            case _ if data.split('_')[0] == "editimgtag":
                from states import Etag
                tag = data.split('_')[1]

                await call.answer()
                await bot.send_message(chat_id, f"Certo, envie uma nova imagem para a tag {tag}.")
                await state.set_state(Etag.foto)
                await bot.delete_message(chat_id, msg_id)
            
            case _ if data.split('_')[0] == "editnomecard":
                from states import Ecard
                card = data.split('_')[1]

                await call.answer()
                await bot.send_message(chat_id, f"Certo, envie um novo nome para o card `{card}`.")
                await state.set_state(Ecard.nome)
                await bot.delete_message(chat_id, msg_id)

            case _ if data.split('_')[0] == "editimgcard":
                from states import Ecard
                card = data.split('_')[1]

                await call.answer()
                await bot.send_message(chat_id, f"Certo, envie uma nova imagem para o card `{card}`.")
                await state.set_state(Ecard.img)
                await bot.delete_message(chat_id, msg_id)
            
            case _ if data.split('_')[0] == "editsubcard":
                from states import Ecard
                card = data.split('_')[1]

                await call.answer()
                await bot.send_message(chat_id, f"Certo, envie uma nova subcategoria para o card `{card}`.")
                await state.set_state(Ecard.sub)
                await bot.delete_message(chat_id, msg_id)
            
            case _ if data.split('_')[0] == "editrarecard":
                from states import Ecard
                card = data.split('_')[1]

                await call.answer()
                await bot.send_message(chat_id, f"Certo, envie uma nova raridade para o card {card}. Você pode enviar em números de 1 a 3 (sendo 1 a mais rara), ou digitar os nomes.")
                await state.set_state(Ecard.rare)
                await bot.delete_message(chat_id, msg_id)

            case _ if data.split('_')[0] == "addsubcard":
                from states import Ecard
                card = data.split('_')[1]

                await call.answer()
                await bot.send_message(chat_id, f"Certo, envie a subcategoria extra que o card {card} deve fazer parte.")
                await state.set_state(Ecard.multisub)
                await bot.delete_message(chat_id, msg_id)
            
            case _ if data.split('_')[0] == "linkar":
                matriz = data.split('_')[1]
                laranja = user_id

                async with get_cursor() as cursor:
                    await cursor.execute("INSERT INTO laranjas (matriz, laranja) VALUES (%s, %s)", (matriz, laranja,))
                
                texto = "Conta conectada com sucesso! 🐛"
                await bot.edit_message_text(
                    text=texto,
                    chat_id=chat_id,
                    message_id=msg_id
                )

            case _ if data.split('_')[0] == "wl":
                cat = data.split('_')[1]
                tlid = data.split('_')[2]

                user = await bot.get_chat(tlid)
                nome = f"{user.first_name} {user.last_name or ''}".strip()
                nome = f"[{nome}](tg://user?id={tlid})"

                if cat == "GERAL":
                    wl = await get_wl(tlid)
                    Ncards = len(wl)

                    texto = f"🧺 Wishlist de {nome}:\n✨ {Ncards} frutinhas desejadas.\n"

                    texto1 = ""
                    texto2 = ""
                    texto3 = ""

                    for carta in wl:
                        dados = await exist_card(carta[0], call)
                        qtd = await carta_user(tlid, dados[0])

                        if qtd == None:
                            qtd = 0
                            
                        match dados[2]:
                            case 1:
                                texto1 += f"\n{raridade_emojis.get(dados[2], '❓')} `{dados[0]}`. {dados[1]} — {dados[5]} ({qtd}x)"
                            case 2:
                                texto2 += f"\n{raridade_emojis.get(dados[2], '❓')} `{dados[0]}`. {dados[1]} — {dados[5]} ({qtd}x)"
                            case 3:
                                texto3 += f"\n{raridade_emojis.get(dados[2], '❓')} `{dados[0]}`. {dados[1]} — {dados[5]} ({qtd}x)"
                    texto += texto1 + texto2 + texto3
                        
                    await bot.edit_message_text(
                        text=texto,
                        chat_id=chat_id,
                        message_id=msg_id
                    )
                else:
                    wl = await get_wl(tlid, cat)
                    if wl:
                        Ncards = len(wl)
                        texto = f"🧺 Wishlist de {nome}:\n{categoria_emojis.get(cat, '❓')} {Ncards} frutinhas desejadas.\n"
                        
                        texto1 = ""
                        texto2 = ""
                        texto3 = ""
        
                        for carta in wl:
                            dados = await exist_card(carta[0], call)
                            qtd = await carta_user(tlid, dados[0])

                            if qtd == None:
                                qtd = 0
                                
                            match dados[2]:
                                case 1:
                                    texto1 += f"\n{raridade_emojis.get(dados[2], '❓')} `{dados[0]}`. {dados[1]} — {dados[5]} ({qtd}x)"
                                case 2:
                                    texto2 += f"\n{raridade_emojis.get(dados[2], '❓')} `{dados[0]}`. {dados[1]} — {dados[5]} ({qtd}x)"
                                case 3:
                                    texto3 += f"\n{raridade_emojis.get(dados[2], '❓')} `{dados[0]}`. {dados[1]} — {dados[5]} ({qtd}x)"
                        texto += texto1 + texto2 + texto3
                        
                        await bot.edit_message_text(
                            text=texto,
                            chat_id=chat_id,
                            message_id=msg_id
                        )
                    else:
                        await call.answer(f"{categoria_emojis.get(cat, '❓')} Oops, parece que você ainda não desejou nada nessa categoria.")
                        return
                    
            case _ if data.split('_')[0] == "confirmreset":
                from admins import confirmreset
                if await is_admin(user_id, call):
                    tlid = data.split('_')[1]
                    user = await bot.get_chat(tlid)
                    username = user.username
                    adm = call.from_user.username

                    await call.answer()
                    msg = await bot.send_message(chat_id, f"⚙️ Aguarde, estamos apagando os dados do habitante @{username}.")
                    await bot.delete_message(chat_id, msg_id)
                    await confirmreset(msg, bot, tlid, chat_id, username, adm)
            
            case "cancelreset":
                if await is_admin(user_id, call):
                    await call.answer()
                    await bot.send_message(chat_id, "⚙️ Certo, tentativa de reset cancelada. O habitante continua com todos os seus itens e cards.")
                    await bot.delete_message(chat_id, msg_id)

            case _ if data.split('_')[0] == "confirmban":
                from admins import confirmban
                if await is_admin(user_id, call):
                    tlid = data.split('_')[1]
                    user = await bot.get_chat(tlid)
                    username = user.username
                    adm = call.from_user.username

                    await call.answer()
                    msg = await bot.send_message(chat_id, f"⚙️ Aguarde, estamos varrendo @{username} para fora da Vila Tutti-Frutti.")
                    await bot.delete_message(chat_id, msg_id)
                    await confirmban(msg, bot, tlid, chat_id, username, adm)
            
            case "cancelban":
                if await is_admin(user_id, call):
                    await call.answer()
                    await bot.send_message(chat_id, "⚙️ Certo, tentativa de expulsão cancelada. O habitante continua na Vila Tutti-Frutti.")
                    await bot.delete_message(chat_id, msg_id)
            
            case _ if data.split('_')[0] == "confirmdesban":
                from admins import confirmdesban
                if await is_admin(user_id, call):
                    tlid = data.split('_')[1]
                    user = await bot.get_chat(tlid)
                    username = user.username
                    adm = call.from_user.username

                    await call.answer()
                    msg = await bot.send_message(chat_id, f"⚙️ Aguarde, estamos trazendo @{username} de volta à Vila Tutti-Frutti.")
                    await bot.delete_message(chat_id, msg_id)
                    await confirmdesban(msg, bot, tlid, chat_id, username, adm)
            
            case "canceldesban":
                if await is_admin(user_id, call):
                    await call.answer()
                    await bot.send_message(chat_id, "⚙️ Certo, tentativa de retorno cancelada.")
                    await bot.delete_message(chat_id, msg_id)

            case _ if data.split('_')[0] == "casar":
                _, opt, pessoa1, pessoa2 = data.split('_')

                user1 = await bot.get_chat(pessoa1)
                username1 = user1.username

                user2 = await bot.get_chat(pessoa2)
                username2 = user2.username

                if opt == "rcs":
                    await bot.send_message(pessoa1, f"🥀 Poxa, parece que seus sentimentos por @{username2} não são recíprocos! Mas não desanime, nossa vila é cheia de amor, você pode encontrar outro alguém especial por aí.")
                    await bot.send_message(pessoa2, f"Você escolheu não aceitar o pedido de @{username1}, quem sabe alguém mais especial cruze seu caminho! 🌥️")
                    await bot.delete_message(chat_id, msg_id)
                else:
                    async with get_cursor() as cursor:
                        await cursor.execute("UPDATE usuarios SET parceiro = %s WHERE username = %s", (username2, username1,))
                        await cursor.execute("UPDATE usuarios SET parceiro = %s WHERE username = %s", (username1, username2,))

                    texto = f"💍 Felicidades ao novo casal da Vila Tutti-Frutti!\nAgora @{username1} e @{username2} estão oficialmente juntos! Que tenham uma relação cheia de frutos. 💞"
                    await bot.send_message(pessoa1, texto)
                    await bot.send_message(pessoa2, texto)
                    await bot.delete_message(chat_id, msg_id)

            case _ if data.split('_')[0] == "loja":
                opt = data.split('_')[1]
                
                match opt:
                    case "giros":
                        texto = "🪴 Cada colheita custa 1.000 sementes, envie a quantidade que deseja comprar.\n\nExemplo: 10 (gastará 10.000 sementes)."
                        await bot.edit_message_caption(
                            caption=texto,
                            chat_id=chat_id,
                            message_id=msg_id
                        )
                        await state.set_state(Loja.giros)

                    case "vip":
                        async with get_cursor() as cursor:
                            await cursor.execute("SELECT vip FROM usuarios WHERE telegram_id = %s", (user_id,))
                            isvip = await cursor.fetchone()
                        
                        if isvip[0] == 0:
                            texto = "🎟️ Torne-se um jardineiro VIP da vila por apenas 150.000 sementes.\n\n🌺 Benefícios:\nGiros diários e recompensas duplicadas.\nAcesso exclusivo para jogos e recompensas semanais.\n\nEnvie /confirmar para comprar ou /cancelar."
                            await bot.edit_message_caption(
                                caption=texto,
                                chat_id=chat_id,
                                message_id=msg_id
                            )
                            await state.set_state(Loja.vip)
                        else:
                            await call.answer("🎟️ Você já é um jardineiro VIP.")
                            return
                        
                    case "caixinha":
                        async with get_cursor() as cursor:
                            await cursor.execute("SELECT sementes FROM usuarios WHERE telegram_id = %s", (user_id,))
                            sementes = await cursor.fetchone()
                        
                        if sementes[0] < 10000:
                            await call.answer("🗳️ Você não tem sementes suficientes para caixinha.")
                            return
                        else:
                            
                            texto = "🗳️ Aumente suas chances com a Caixinha Surpresa por apenas 10.000 sementes.\n\nEnvie 5 IDs de frutinhas que você deseja aumentar a sorte de encontrar (30%), enquanto uma delas virá obrigatoriamente!\n15 frutinhas serão sorteadas da categoria de sua preferência.\n\n🦋 Caso queira prosseguir, escolha uma das categorias abaixo."
                            await bot.edit_message_caption(
                                caption=texto,
                                chat_id=chat_id,
                                message_id=msg_id,
                                reply_markup=await painel_categorias("caixinha")
                            )

                    case "divorcio":
                        async with get_cursor() as cursor:
                            await cursor.execute("SELECT parceiro FROM usuarios WHERE telegram_id = %s", (user_id,))
                            casado = await cursor.fetchone()

                            if not casado[0]:
                                await call.answer("🔖 Oops, você não é casado.")
                                return
                            else:
                                parceiro = casado[0]
                                texto = f"🌥️ Até mesmo as uniões mais bonitas chegam ao fim... Tem certeza que deseja se separar de @{parceiro} por 2.500 sementes e disponibilizar seu coração para outra pessoa?\n\nEnvie /confirmar se deseja finalizar a ação ou /cancelar."
                                await bot.edit_message_caption(
                                    caption=texto,
                                    chat_id=chat_id,
                                    message_id=msg_id
                                )
                                await state.update_data(parceiro=parceiro)
                                await state.set_state(Loja.divorcio)
                    
                    case "perfil":
                        texto = f"🪵 Temos perfis temáticos de eventos passados para que você use-os permanentemente no seu perfil!\n\nConsulte o nosso catálogo aqui (link) e veja se gosta de algum!\nPara comprar, envie o comando correspondente.\n\n🍄 Cada perfil custa 10.000 sementes e você pode equipar usando o mesmo comando de compra!\n\nExemplo: /perfilnatal (primeira vez usando fará sua compra)\n/perfilnatal (segunda vez usando o equipará em seu perfil)."
                        await bot.edit_message_caption(
                            caption=texto,
                            chat_id=chat_id,
                            message_id=msg_id
                        )

            case _ if data.split('_')[0] == "filt":
                _, raridade, cat, att_data, user_id, página, totalcards, pag = data.split('_')
                raridade = int(raridade)
                página = int(página)
                total_pag = math.ceil(int(totalcards) / 20)

                rare1 = "✅" if att_data == "atv" and raridade == 1 else "🥇"
                rare2 = "✅" if att_data == "atv" and raridade == 2 else "🥈"
                rare3 = "✅" if att_data == "atv" and raridade == 3 else "🥉"

                if pag == "prox":
                    página += 1
                    if página > total_pag:
                        await call.answer("🍂 Você já está na última página.")
                        return
                elif pag == "ant":
                    página -= 1
                    if página < 1:
                        await call.answer("🍂 Você já está na primeira página.")
                        return
                else:
                    página = 1

                async with get_cursor() as cursor:
                    offset = (página - 1) * 20
                    if att_data == "atv":
                        if cat == "Nenhuma":
                            await cursor.execute("SELECT c.id, c.nome, c.raridade, COALESCE(i.quantidade, 0) FROM cartas c INNER JOIN inventario i ON c.id = i.id_carta WHERE i.id_user = %s AND c.raridade = %s LIMIT 20 OFFSET %s", (user_id, raridade, offset,))
                            inventario = await cursor.fetchall()
                            await cursor.execute("SELECT SUM(quantidade) FROM inventario i INNER JOIN cartas c ON i.id_carta = c.id WHERE i.id_user = %s AND c.raridade = %s", (user_id, raridade,))
                            result = await cursor.fetchone()
                            Ncards = result[0] if result else 0
                            await cursor.execute("SELECT COUNT(id_user) FROM inventario i INNER JOIN cartas c ON i.id_carta = c.id WHERE i.id_user = %s AND c.raridade = %s", (user_id, raridade,))
                            cards = await cursor.fetchone()
                            totalcards = cards[0]
                        else:
                            cursor.execute("SELECT c.id, c.nome, c.raridade, COALESCE(i.quantidade, 0) FROM cartas c INNER JOIN inventario i ON c.id = i.id_carta WHERE i.id_user = %s AND c.raridade = %s AND c.categoria = %s LIMIT 20 OFFSET %s", (user_id, raridade, cat, offset,))
                            inventario = await cursor.fetchall()
                            await cursor.execute("SELECT SUM(quantidade) FROM inventario i INNER JOIN cartas c ON i.id_carta = c.id WHERE i.id_user = %s AND c.raridade = %s AND c.categoria = %s", (user_id, raridade, cat,))
                            result = await cursor.fetchone()
                            Ncards = result[0] if result else 0
                            await cursor.execute("SELECT COUNT(id_user) FROM inventario i INNER JOIN cartas c ON i.id_carta = c.id WHERE i.id_user = %s AND c.raridade = %s AND c.categoria = %s", (user_id, raridade, cat,))
                            cards = await cursor.fetchone()
                            totalcards = cards[0]
                        
                        att_data = "atv"
                    else:
                        att_data = "dtv"

                        if cat == "Nenhuma":
                            await cursor.execute("SELECT c.id, c.nome, c.raridade, COALESCE(i.quantidade, 0) FROM cartas c INNER JOIN inventario i ON c.id = i.id_carta WHERE i.id_user = %s ORDER BY c.raridade ASC LIMIT 20 OFFSET %s", (user_id, offset,))
                            inventario = await cursor.fetchall()
                            await cursor.execute("SELECT SUM(quantidade) FROM inventario i WHERE i.id_user = %s", (user_id,))
                            result = await cursor.fetchone()
                            Ncards = result[0] if result else 0
                            await cursor.execute("SELECT COUNT(id_user) FROM inventario i INNER JOIN cartas c ON i.id_carta = c.id WHERE i.id_user = %s", (user_id,))
                            cards = await cursor.fetchone()
                            totalcards = cards[0]
                        else:
                            await cursor.execute("SELECT c.id, c.nome, c.raridade, COALESCE(i.quantidade, 0) FROM cartas c INNER JOIN inventario i ON c.id = i.id_carta WHERE i.id_user = %s AND c.categoria = %s ORDER BY c.raridade ASC LIMIT 20 OFFSET %s", (user_id, cat, offset,))
                            inventario = await cursor.fetchall()
                            await cursor.execute("SELECT SUM(quantidade) FROM inventario i INNER JOIN cartas c ON i.id_carta = c.id WHERE i.id_user = %s AND c.categoria = %s", (user_id, cat,))
                            result = await cursor.fetchone()
                            Ncards = result[0] if result else 0
                            await cursor.execute("SELECT COUNT(id_user) FROM inventario i INNER JOIN cartas c ON i.id_carta = c.id WHERE i.id_user = %s AND c.categoria = %s", (user_id, cat,))
                            cards = await cursor.fetchone()
                            totalcards = cards[0]
                
                épica = InlineKeyboardButton(text=rare1, callback_data=f'filt_1_{cat}_{'dtv' if raridade == 1 else 'atv'}_{user_id}_{página}_{totalcards}_none')
                rara = InlineKeyboardButton(text=rare2, callback_data=f'filt_2_{cat}_{'dtv' if raridade == 2 else 'atv'}_{user_id}_{página}_{totalcards}_none')
                comum = InlineKeyboardButton(text=rare3, callback_data=f'filt_3_{cat}_{'dtv' if raridade == 3 else 'atv'}_{user_id}_{página}_{totalcards}_none')

                ant = InlineKeyboardButton(text="⬅️", callback_data=f"filt_{raridade}_{cat}_{att_data}_{user_id}_{página}_{totalcards}_ant")
                prox = InlineKeyboardButton(text="➡️", callback_data=f"filt_{raridade}_{cat}_{att_data}_{user_id}_{página}_{totalcards}_prox")
                
                if not inventario:
                    await call.answer("🍂 Não existem frutinhas dentro dessa filtragem.")
                    return
                
                await call.answer()

                lista_cartas = "\n".join([f"{raridade_emojis.get(raridade, '❓')} `{id}`. {nome} (`{quantidade}`x) {get_emoji(quantidade)}" 
                                        for id, nome, raridade, quantidade in inventario])

                filt = InlineKeyboardMarkup(inline_keyboard=[
                    [épica, rara, comum],
                    [ant, prox]
                ])

                total_pag = math.ceil(int(totalcards) / 20)

                user = await bot.get_chat(user_id)
                nome = f"{user.first_name} {user.last_name or ''}".strip()
                nome = f"[{nome}](tg://user?id={user_id})"

                inventario_filtrado = f"🧺 Você tem {Ncards} frutinhas na sua cestinha, {nome}: \n💌 Página {página} de {total_pag}. \n\n{lista_cartas}\n"
                inventario_filtrado += "\u200B"
                inventario_filtrado += "  "

                await bot.edit_message_text(
                    text=inventario_filtrado,
                    chat_id=chat_id,
                    message_id=msg_id,
                    reply_markup=filt
                )
            
            case _ if data.split('_')[0] == "allberry":
                _, action, cat, Ncards, pag, total_pag = data.split('_')

                if action == "prox":    
                    pag = 2
                    offset = 10
                    nmr = 10

                    allberryopt = InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(text="⬅️", callback_data=f"allberry_ant_{cat}_{Ncards}_{pag}_{total_pag}")
                        ]
                    ])
                else:
                    nmr = 0
                    pag = 1
                    offset = 0
                    
                    allberryopt = InlineKeyboardMarkup(inline_keyboard=[
                        [  
                            InlineKeyboardButton(text="➡️", callback_data=f"allberry_prox_{cat}_{Ncards}_{pag}_{total_pag}")
                        ]
                    ])
                
                async with get_cursor() as cursor:
                    await cursor.execute("""
                        SELECT c.subcategoria, SUM(i.quantidade)
                        FROM cartas c
                        LEFT JOIN inventario i ON c.id = i.id_carta
                        WHERE c.categoria = %s
                        GROUP BY c.subcategoria
                        ORDER BY SUM(i.quantidade) DESC
                        LIMIT 10 OFFSET %s
                    """, (cat, offset,))
                    allberry = await cursor.fetchall()

                    if not allberry:
                        await call.answer(f"🍂 Oops, não há mais páginas para {cat}.")
                        return
                    else:
                        texto = f"{categoria_emojis.get(cat, '❓')} Olá, ADM @{call.from_user.username}! Aqui estão as subcategorias mais giradas da categoria {cat}.\n💌 Página {pag} de {total_pag}.\n"
                        
                        for row in allberry:
                            nmr += 1
                            sub = row[0]
                            quantidade = row[1] or 0
                            texto += f"\n{nmr}. {sub} ({quantidade}x)"

                        texto += f"\n\n🍁 {Ncards} cards foram girados no total."
                        texto += "\u200B"
                        texto += "  "

                        await bot.edit_message_text(
                            text=texto,
                            chat_id=chat_id,
                            message_id=msg_id,
                            reply_markup=allberryopt
                        )
            
            case "regdepositar":
                async with get_cursor() as cursor:
                    await cursor.execute("SELECT adm, operaçao, data, destinatario, quantidade FROM gerencia WHERE operaçao = %s OR operaçao = %s ORDER BY data DESC", ("depositar", "depositarall",))
                    result = await cursor.fetchall()

                texto = "🍁 Abaixo estão listadas as últimas operações de /depositar e /depositarall da semana, da mais recente à mais antiga:\n"
                n = 0

                for adm, operaçao, data, destinatario, quantidade in result:
                    if destinatario == 100:
                        destinatario = "todos os habitantes"
                    else:
                        user = await bot.get_chat(destinatario)
                        destinatario = f"@{user.username}"
                    
                    data = data.strftime("%d/%m/%Y")
                    texto +=f"\n— {data}\n/{operaçao} {quantidade} colheitas para {destinatario}.\n🍂 Operador: @{adm}\n"
                    n += 1
                
                if n == 0:
                    await call.answer("🍂 Oops, não há registros desse comando.")
                else:
                    await call.answer()
                    await bot.send_message(chat_id, texto)
                    await bot.delete_message(chat_id, msg_id)
            
            case "regfermentar":
                async with get_cursor() as cursor:
                    await cursor.execute("SELECT adm, operaçao, data, destinatario, quantidade FROM gerencia WHERE operaçao = %s OR operaçao = %s ORDER BY data DESC", ("fermentar", "fermentarall",))
                    result = await cursor.fetchall()

                texto = "🍁 Abaixo estão listadas as últimas operações de /fermentar e /fermentarall da semana, da mais recente à mais antiga:\n"
                n = 0

                for adm, operaçao, data, destinatario, quantidade in result:
                    if destinatario == 100:
                        destinatario = "todos os habitantes"
                    else:
                        user = await bot.get_chat(destinatario)
                        destinatario = f"@{user.username}"
                    
                    data = data.strftime("%d/%m/%Y")
                    texto +=f"\n— {data}\n/{operaçao} {quantidade} sementes para {destinatario}.\n🍂 Operador: @{adm}\n"
                    n += 1
                
                if n == 0:
                    await call.answer("🍂 Oops, não há registros desse comando.")
                else:
                    await call.answer()
                    await bot.send_message(chat_id, texto)
                    await bot.delete_message(chat_id, msg_id)

            case "regpres":
                async with get_cursor() as cursor:
                    await cursor.execute("SELECT adm, operaçao, data, destinatario, quantidade, card FROM gerencia WHERE operaçao = %s OR operaçao = %s ORDER BY data DESC", ("presentear", "remover",))
                    result = await cursor.fetchall()

                texto = "🍁 Abaixo estão listadas as últimas operações de /presentear da semana, da mais recente à mais antiga:\n"
                n = 0

                for adm, operaçao, data, destinatario, quantidade, card in result:
                    user = await bot.get_chat(destinatario)
                    destinatario = f"@{user.username}"
                    data = data.strftime("%d/%m/%Y")
                    texto +=f"\n— {data}\n/{operaçao} card `{card}` para {destinatario} ({quantidade}x).\n🍂 Operador: @{adm}\n"
                    n += 1
                
                if n == 0:
                    await call.answer("🍂 Oops, não há registros desse comando.")
                else:
                    await call.answer()
                    await bot.send_message(chat_id, texto)
                    await bot.delete_message(chat_id, msg_id)
            
            case "regresetdb":
                async with get_cursor() as cursor:
                    await cursor.execute("SELECT adm, operaçao, data, destinatario FROM gerencia WHERE operaçao = %s OR operaçao = %s ORDER BY data DESC", ("reset", "desban",))
                    result = await cursor.fetchall()

                texto = "🍁 Abaixo estão listadas as últimas operações de /reset e /desban da semana, da mais recente à mais antiga:\n"
                n = 0

                for adm, operaçao, data, destinatario in result:
                    user = await bot.get_chat(destinatario)
                    destinatario = f"@{user.username}"
                    data = data.strftime("%d/%m/%Y")
                    texto +=f"\n— {data}\n/{operaçao} {destinatario}.\n🍂 Operador: @{adm}\n"
                    n += 1
                
                if n == 0:
                    await call.answer("🍂 Oops, não há registros desse comando.")
                else:
                    await call.answer()
                    await bot.send_message(chat_id, texto)
                    await bot.delete_message(chat_id, msg_id)


    except telebot.apihelper.ApiException as e:
        print(f"Erro ao processar o comando: {e}")
        if e.result_json['description'] == 'Bad Request: TOPIC_CLOSED':
            await msg.reply("⚙️ Oops, não foi possível processar o comando... o tópico está fechado.")
        else:
            await msg.reply("⚙️ Desculpe, ocorreu um erro ao processar o comando.")