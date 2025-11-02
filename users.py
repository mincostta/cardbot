import inspect
import asyncio
import re
import math
import random
import os
import requests
import time

from ftplib import FTP
from dotenv import load_dotenv
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, BufferedInputFile
from aiogram.filters import StateFilter

from states import Receita
from conn import get_cursor
from utils import is_admin, exist_sub, exist_card, exist_tag, painel_categorias, carta_user, get_emoji, get_wl, midiaesp, up_bunny

# -------------------------------------------
# INÍCIO DA DEFINIÇÃO DE EMOJIS E NOMES

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

raridades = {
    1: "épica",
    2: "rara",
    3: "comum"
}

load_dotenv()
FRUITMIX = int(os.getenv("FRUITMIX"))
MORANGEEK = int(os.getenv("MORANGEEK"))
STREAMBERRY = int(os.getenv("STREAMBERRY"))
ASIAFARM = int(os.getenv("ASIAFARM"))

users = Router()
TOKEN = os.getenv("TOKEN")

# FIM DA DEFINIÇÃO DE EMOJIS E NOMES

# -------------------------------------------
# COMANDO PARA COLHER UMA CARTA

async def colher(bot, msg):
    user_id = msg.from_user.id
    action = inspect.currentframe().f_code.co_name

    async with get_cursor() as cursor:
        await cursor.execute("SELECT giros FROM usuarios WHERE telegram_id = %s", (user_id,))
        result = await cursor.fetchone()
        giros = int(result[0])

        if giros == 0:
            await msg.reply("Infelizmente você está sem giros no momento! Seu pomar sempre renova às 12:00 e às 00:00, volte mais tarde para colher. 🍃")
            return
        elif giros == 1:
            giros = giros - 1
            texto = f"Está na hora de colher! Explore uma das categorias abaixo. \n\n🧺 Você está na sua última colheita."
        else:
            giros = giros - 1
            texto = f"Está na hora de colher! Explore uma das categorias abaixo. \n\n🧺 Você pode fazer mais {giros} colheitas."
        
        await cursor.execute("UPDATE usuarios SET giros = %s WHERE telegram_id = %s", (giros, user_id,))

    imagem = "assets\\colher.png"
    imagem = FSInputFile(imagem)

    await bot.send_photo(
        chat_id=msg.chat.id,
        photo=imagem,
        caption=texto,
        reply_to_message_id=msg.message_id,
        reply_markup=await painel_categorias(action)
    )

# -------------------------------------------
# COMANDO SAQUE PARA COLHER VÁRIAS CARTAS

async def saque(bot, msg):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    saque = msg.text.split()

    if len(saque) < 3:
        await msg.reply("⚙️ Oops, parece que falta algo... Exemplo: /safra categoria quantidade.")
        return
    else:
        quantidade = saque[2]
        cat = saque[1].upper()

    if cat not in ("MORANGEEK", "ASIAFARM", "STREAMBERRY", "FRUITMIX"):
        await msg.reply("⚙️ Oops, essa categoria não existe.")
        return
    
    try:
        quantidade = int(quantidade)
    except ValueError:
        await msg.reply("⚙️ Oops, parece que você não informou um número válido.")
        return

    async with get_cursor() as cursor:
        await cursor.execute("SELECT giros FROM usuarios WHERE telegram_id = %s", (user_id,))
        result = await cursor.fetchone()
        giros = int(result[0])

        if giros == 0:
            await msg.reply("Infelizmente você está sem giros no momento! Seu pomar sempre renova às 12:00 e às 00:00, volte mais tarde para colher. 🍃")
            return
        elif giros < quantidade:
            await msg.reply(f"Oops, você não tem materiais o suficiente para completar essa safra. \n\n🌾 Você possui {giros} colheitas.")
            return
        else:
            giros = giros - quantidade

            user = await bot.get_chat(user_id)
            nome = f"{user.first_name} {user.last_name or ''}".strip()

            if quantidade <= 15:
                nome = f"[{nome}](tg://user?id={user_id})"

            texto = f"🌾 Parabéns, {nome}! Com {quantidade} colheitas, sua safra rendeu:\n"
            
            chances = [20, 30, 50]
            texto2 = ""
            texto3 = ""
            for i in range(quantidade):
                raridade_escolhida = random.choices([1, 2, 3], weights=chances, k=1)[0]
                await cursor.execute("SELECT id, raridade, nome, subcategoria FROM cartas WHERE categoria = %s AND raridade = %s ORDER BY RAND() LIMIT 1", (cat, raridade_escolhida,))
                result = await cursor.fetchone()

                if result:
                    carta = result[0]
                    raridade = result[1]
                    nome = result[2]
                    sub = result[3]
                else:
                    await cursor.execute("SELECT id, raridade, nome, subcategoria FROM cartas WHERE categoria = %s AND raridade = 2 ORDER BY RAND() LIMIT 1", (cat,))
                    result = await cursor.fetchone()
                    carta = result[0]
                    raridade = result[1]
                    nome = result[2]
                    sub = result[3]

                Ncards = await carta_user(user_id, carta, cursor)

                if Ncards == None:
                    Ncards = 1
                    await cursor.execute("INSERT INTO inventario (id_user, id_carta, quantidade) VALUES (%s, %s, %s)", (user_id, carta, 1))      
                else:
                    Ncards += 1
                    await cursor.execute("UPDATE inventario SET quantidade = %s WHERE id_user = %s AND id_carta = %s", (Ncards, user_id, carta,))

                if raridade == 1:
                    texto += f"\n{raridade_emojis.get(raridade, '❓')} `{carta}`. {nome} — {sub} (`{Ncards}`x)."
                elif raridade == 2:
                    texto2 += f"\n{raridade_emojis.get(raridade, '❓')} `{carta}`. {nome} — {sub} (`{Ncards}`x)."
                else:
                    texto3 += f"\n{raridade_emojis.get(raridade, '❓')} `{carta}`. {nome} — {sub} (`{Ncards}`x)."
            
            await cursor.execute("UPDATE usuarios SET giros = %s WHERE telegram_id = %s", (giros, user_id,))
            texto += texto2
            texto += texto3

    if quantidade <= 15:
        await msg.reply(texto)
    else:
        texto = texto.replace("`", "")
        caminho = "safra.txt"
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto)
        
        arquivo = FSInputFile(caminho)
        await bot.send_document(chat_id, document=arquivo, caption=f"🌾 Essas foram as {quantidade} frutinhas que você conseguiu em sua safra!", reply_to_message_id=msg.message_id)
        os.remove(caminho)

# -------------------------------------------
# COMANDO COLHEITA PARA VISUALIZAR UMA SUBCATEGORIA

async def colheita(bot, msg):
    id_user  = msg.from_user.id
    colheita = msg.text.split(' ', 1)

    if len(colheita) < 2:
        await msg.reply("⚙️ Por favor, forneça uma subcategoria para pesquisar. Exemplo: /colheita subcategoria.")
        return

    sub = colheita[1]
    result = await exist_sub(sub, msg)
    
    if result:
        categoria = result[0]
        subcategoria = result[1]
        imagem = result[2]

        async with get_cursor() as cursor:
            await cursor.execute("SELECT c.id, c.nome, c.raridade, COALESCE(i.quantidade, 0) FROM cartas c LEFT JOIN inventario i ON c.id = i.id_carta AND i.id_user = %s WHERE c.subcategoria = %s OR EXISTS (SELECT 1 FROM multisub m WHERE m.id = c.id AND m.subcategoria = %s) ORDER BY c.raridade ASC", (id_user, subcategoria, subcategoria,))
            cartas = await cursor.fetchall()

        Ncards = len(cartas)
        total = sum(card[3] for card in cartas)

        lista_cartas = "\n".join([f"{raridade_emojis.get(raridade, '❓')} `{id}`. {nome} (`{quantidade}`x) {get_emoji(quantidade)}" 
                                for id, nome, raridade, quantidade in cartas])

        nome_user = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
        nome_user = f"[{nome_user}](tg://user?id={id_user})"

        try:
            caption = f"🧺 Esta é a sua colheita de {subcategoria}, {nome_user}.\n{categoria_emojis.get(categoria, '❓')} {Ncards} frutinhas no total, {total} em sua plantação. \n\n{lista_cartas} \n\n🍄 Para consultar suas frutinhas, utilize /buscar."
            await bot.send_photo(
                chat_id=msg.chat.id,
                photo=f"{imagem}?nocache={int(time.time())}",
                caption=caption,
                reply_to_message_id=msg.message_id
            )
        except Exception as e:
            await msg.reply(f"⚙️ Erro ao enviar a imagem: {str(e)}")
            return
    else:
        return

# -------------------------------------------
# COMANDO VAR PARA VER VARIAÇÕES DE NOME

async def var(msg):
    busca = msg.text.split(' ', 1)
    if len(busca) < 2:
        await msg.reply("⚙️ Por favor, forneça uma subcategoria para pesquisar. Exemplo: /var sub.")
        return

    busca = busca[1]
    result = await exist_sub(busca, msg)

    if result:
        sub = result[1]
        async with get_cursor() as cursor:
            await cursor.execute("SELECT shortner FROM divisoes WHERE subcategoria = %s", (sub,))
            haveshortner = await cursor.fetchone()

        shortners = haveshortner[0] if haveshortner and haveshortner[0] else None

        if shortners != None:
            shortners = shortners.split(',')
            await msg.reply(f"🍑 Habitante, você pode pesquisar a colheita {sub} pelas seguintes variações: {', '.join(shortners)}.")
        else:
            await msg.reply(f"🍑 Infelizmente a colheita {sub} ainda não tem nenhuma variação.")

# -------------------------------------------
# COMANDO BUSCAR PARA VISUALIZAR UMA TAG

async def tag(bot, msg):
    busca = msg.text.split(' ', 1)
    if len(busca) < 2:
        await msg.reply("⚙️ Por favor, forneça uma tag para pesquisar. Exemplo: /tag nome.")
        return

    busca = busca[1]
    result = await exist_tag(busca)
    id = msg.from_user.id

    if result:
        nome = result[0]
        imagem = result[1]

        async with get_cursor() as cursor:
            await cursor.execute("SELECT c.id, c.nome, c.raridade, COALESCE(i.quantidade, 0) FROM cartas c LEFT JOIN inventario i ON c.id = i.id_carta AND i.id_user = %s WHERE c.tag = %s ORDER BY c.raridade ASC", (id, busca,))
            cartas = await cursor.fetchall()

        Ncards = len(cartas)
        total = sum(card[3] for card in cartas)

        lista_cartas = "\n".join([f"{raridade_emojis.get(raridade, '❓')} `{id}`. {nome} (`{quantidade}`x) {get_emoji(quantidade)}" 
                                for id, nome, raridade, quantidade in cartas])

        try:
            caption = f"🏷️ {nome} \n🍉 {Ncards} frutinhas no total, {total} em sua plantação. \n\n{lista_cartas} \n\n🍄 Para consultar suas frutinhas, utilize /buscar."
            await bot.send_photo(
                chat_id=msg.chat.id,
                photo=f"{imagem}?nocache={int(time.time())}",
                caption=caption,
                reply_to_message_id=msg.message_id
            )
        except Exception as e:
            await msg.reply(f"⚙️ Erro ao enviar a imagem: {str(e)}")
            return
    else:
        return

# -------------------------------------------
# COMANDO BUSCAR PARA VISUALIZAR UMA CARTA

async def buscar(bot, msg):
    busca = msg.text.split(' ', 1)

    if len(busca) < 2:
        await msg.reply("⚙️ Por favor, forneça um card para pesquisar. Exemplo: /buscar id ou nome.")
        return

    busca = busca[1]
    result = await exist_card(busca, msg)

    id_user = msg.from_user.id

    if result:
        quantidade = await carta_user(id_user, busca)

        if quantidade == None:
            quantidade = 0

        id, nome, raridade, midia, categoria, subcategoria, tag, _ = result

        nome_user = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
        nome_user = f"[{nome_user}](tg://user?id={id_user})"

        async with get_cursor() as cursor:
            await cursor.execute("SELECT subcategoria FROM multisub WHERE id = %s", (id,))
            multi = await cursor.fetchall()

        subs = subcategoria
        if multi:
            for sub in multi:
                subs += f", {sub[0]}"

        esp = await midiaesp(id, id_user)

        if esp:
            midia = esp[0]
            tipo = esp[1]

        if tag == None:
            caption = f"{nome_user}, encontrei sua frutinha! \n\n{raridade_emojis.get(raridade, '❓')} `{id}`. {nome} {get_emoji(quantidade)}\n{categoria_emojis.get(categoria, '❓')} {subs} \n\n🧺 Você possui {quantidade} unidades."
        else:
            caption = f"{nome_user}, encontrei sua frutinha! \n\n{raridade_emojis.get(raridade, '❓')} `{id}`. {nome} {get_emoji(quantidade)}\n{categoria_emojis.get(categoria, '❓')} {subs} \n🏷️ {tag} \n\n🧺 Você possui {quantidade} unidades."
        try:  
            if not esp or tipo == "foto":
                await bot.send_photo(
                    chat_id=msg.chat.id,
                    photo=f"{midia}?nocache={int(time.time())}",
                    caption=caption,
                    reply_to_message_id=msg.message_id
                )
            else:
                await bot.send_video(chat_id=msg.chat.id, video=f"{midia}?nocache={int(time.time())}", caption=caption, reply_to_message_id=msg.message_id)
        except Exception as e:
            await msg.reply(f"⚙️ Erro ao enviar a imagem: {str(e)}")
            return

# -------------------------------------------
# COMANDO CESTA PARA VISUALIZAR O INVENTÁRIO

async def cesta(msg):
    user_id = msg.from_user.id
    cesta = msg.text.split(' ', 1)

    async with get_cursor() as cursor:
        if len(cesta) < 2:
            await cursor.execute("SELECT COUNT(id_user) FROM inventario WHERE id_user = %s", (user_id,))
            cards = await cursor.fetchone()
            await cursor.execute("SELECT c.id, c.nome, c.raridade, COALESCE(i.quantidade, 0) FROM cartas c INNER JOIN inventario i ON c.id = i.id_carta WHERE i.id_user = %s ORDER BY c.raridade ASC LIMIT 20", (user_id,))
            inventario = await cursor.fetchall()
            cat = "Nenhuma"
            await cursor.execute("SELECT SUM(quantidade) FROM inventario WHERE id_user = %s", (user_id,))
            result = await cursor.fetchone()
            Ncards = result[0] if result else 0
        else: 
            cat = cesta[1].upper()
            if cat in ["MORANGEEK", "ASIAFARM", "FRUITMIX", "STREAMBERRY"]:
                await cursor.execute("SELECT COUNT(id_user) FROM inventario i INNER JOIN cartas c ON i.id_carta = c.id WHERE i.id_user = %s AND c.categoria = %s", (user_id, cat,))
                cards = await cursor.fetchone()
                await cursor.execute("SELECT c.id, c.nome, c.raridade, COALESCE(i.quantidade, 0) FROM cartas c INNER JOIN inventario i ON c.id = i.id_carta WHERE i.id_user = %s AND c.categoria = %s ORDER BY c.raridade ASC LIMIT 20", (user_id, cat,))
                inventario = await cursor.fetchall()
                await cursor.execute("SELECT SUM(quantidade) FROM inventario i INNER JOIN cartas c ON i.id_carta = c.id WHERE i.id_user = %s AND c.categoria = %s", (user_id, cat,))
                result = await cursor.fetchone()
                Ncards = result[0] if result else 0
            else:
                await msg.reply(f"⚙️ Oops, a categoria {cat} não existe.")
                return

        if cards[0] == 0 and len(cesta) < 2:
            await msg.reply("⚙️ Oops, você ainda não tem nenhuma carta... faça sua primeira colheita e depois retorne aqui!")
            return
        elif cards[0] == 0 and len(cesta) >= 2:
            await msg.reply(f"⚙️ Oops, você ainda não tem nenhuma carta na categoria {cat}... faça sua primeira colheita e depois retorne aqui!")
            return
        else:
            totalcards = cards[0]
            página = 1

            filt = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🥇", callback_data=f"filt_1_{cat}_atv_{user_id}_1_{totalcards}_none"),
                    InlineKeyboardButton(text="🥈", callback_data=f"filt_2_{cat}_atv_{user_id}_1_{totalcards}_none"),
                    InlineKeyboardButton(text="🥉", callback_data=f"filt_3_{cat}_atv_{user_id}_1_{totalcards}_none"),
                ],
                [
                    InlineKeyboardButton(text="⬅️", callback_data=f"filt_0_{cat}_dtv_{user_id}_1_{totalcards}_ant"),
                    InlineKeyboardButton(text="➡️", callback_data=f"filt_0_{cat}_dtv_{user_id}_1_{totalcards}_prox"),
                ]
            ])

            lista_cartas = "\n".join([f"{raridade_emojis.get(raridade, '❓')} `{id}`. {nome} (`{quantidade}`x) {get_emoji(quantidade)}" 
                                        for id, nome, raridade, quantidade in inventario])
  
            nome = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
            nome = f"[{nome}](tg://user?id={user_id})"
            total_pag = math.ceil(totalcards / 20)
            
            await msg.reply(f"🧺 Você tem {Ncards} frutinhas na sua cestinha, {nome}: \n💌 Página {página} de {total_pag}. \n\n{lista_cartas}\n\u200B", parse_mode="Markdown", reply_markup=filt)
    
# -------------------------------------------
# COMANDO REGAR PARA RESGATAR RECOMPENSA DIÁRIA

async def regar(msg):
    user_id = msg.from_user.id

    async with get_cursor() as cursor:
        await cursor.execute("SELECT vip, ultimo_daily FROM usuarios WHERE telegram_id = %s", (user_id,))
        result = await cursor.fetchone()

        vip, ultimo_daily = result
        hoje = datetime.today().date()

        if ultimo_daily == hoje:
            await msg.reply("Você já regou as plantinhas hoje, volte amanhã! 🪴")
            return
        
        else:
            if vip == 1:
                sementes = 500
                giros = 10

                await cursor.execute("""
                UPDATE usuarios 
                SET sementes = sementes + %s, giros = LEAST(giros + %s, 2000), ultimo_daily = %s 
                WHERE telegram_id = %s
            """, (sementes, giros, hoje, user_id))
                
            else:
                sementes = 250
                giros = 5

                await cursor.execute("""
                UPDATE usuarios 
                SET sementes = sementes + %s, giros = LEAST(giros + %s, 1000), ultimo_daily = %s 
                WHERE telegram_id = %s
            """, (sementes, giros, hoje, user_id))

        await msg.reply(f"Após regar as flores do senhor Floriano, ele te recompensou. Parabéns, você acaba de ganhar {giros} colheitas e {sementes} sementes! 🫘")

# -------------------------------------------
# COMANDO TOP PARA VER RANKING DE UMA CARTA

async def top(bot, msg):
    busca = msg.text.split()

    if len(busca) < 2:
        await msg.reply("⚙️ Por favor, forneça um card para visualizar o ranking. Exemplo: /top ID.")
        return
    elif len(busca) > 2:
        await msg.reply("⚙️ Forneça somente um ID para visualizar o ranking. Exemplo: /top ID.")
        return
    else:
        try:
            card = int(busca[1])
        except ValueError:
            await msg.reply("⚙️ Oops, só é possível ver um ranking com base no ID da carta.")
            return
        
        card = await exist_card(card, msg)
        if not card:
            return
        else:
            id = card[0]
            nome = card[1]
            midia = card[3]
            categoria = card[4]
        
        async with get_cursor() as cursor:
            await cursor.execute("SELECT i.id_user, i.quantidade, (SELECT SUM(quantidade) FROM inventario WHERE id_carta = %s) AS total_cartas FROM inventario i JOIN usuarios u ON i.id_user = u.telegram_id WHERE u.top = 1 AND i.id_carta = %s ORDER BY i.quantidade DESC LIMIT 5", (id, id,))
            ranking = await cursor.fetchall()

        if not ranking:
            await msg.reply(f"⚙️ Oops, ninguém possui essa carta no inventário. Não foi possível gerar o ranking.")
            return
        else:
            total_cartas = ranking[0][2]
            top1 = ranking[0][0]

            esp = await midiaesp(id, top1)

            if esp:
                midia = esp[0]
                tipo = esp[1]

            users = await asyncio.gather(
                *[bot.get_chat(row[0]) for row in ranking]
            )

            texto = f"{categoria_emojis.get(categoria, '❓')} Os melhores colocados da frutinha `{id}`. {nome}:\n\n"

            for pos, row in enumerate(ranking):
                try:
                    user = users[pos]
                    nome_user = f"{user.first_name} {user.last_name or ''}".strip() if user else "Usuário desconhecido"
                except Exception:
                    nome_user = "Usuário desconhecido"

                quantidade = row[1]

                match pos:
                    case 0:
                        texto += f"🥇 {nome_user} — (`{quantidade}`x) {get_emoji(quantidade)}\n"
                    case 1:
                        texto += f"🥈 {nome_user} — (`{quantidade}`x) {get_emoji(quantidade)}\n"
                    case 2:
                        texto += f"🥉 {nome_user} — (`{quantidade}`x) {get_emoji(quantidade)}\n\n"
                    case _:
                        texto += f"`{pos + 1}`. {nome_user} — (`{quantidade}`x)\n"
                

            texto += f"\nExistem {total_cartas} unidades dessa frutinha na Vila Tutti-Frutti!"

            if not esp or tipo == "foto":
                await bot.send_photo(
                    chat_id=msg.chat.id,
                    photo=f"{midia}?nocache={int(time.time())}",
                    caption=texto,
                    reply_to_message_id=msg.message_id
                )
            else:
                await bot.send_video(
                    chat_id=msg.chat.id,
                    video=f"{midia}?nocache={int(time.time())}",
                    caption=texto,
                    reply_to_message_id=msg.message_id
                )

# -------------------------------------------
# COMANDO TOPREMOVE PARA ESCONDER SUA POSIÇÃO NOS RANKINGS

async def topremove(telegram_id, msg):
    async with get_cursor() as cursor:
        await cursor.execute("SELECT top FROM usuarios WHERE telegram_id = %s", (telegram_id,))
        result = await cursor.fetchone()

        if result[0] != 1:
            await msg.reply("⚙️ Oops, sua colocação nos rankings já está oculta, não se preocupe.")
        else:
            await cursor.execute("UPDATE usuarios SET top = 0 WHERE telegram_id = %s", (telegram_id,))
            await msg.reply("🏅 Certo, sua colocação no ranking foi escondida! Caso deseje retornar, utilize /topadd.")

# -------------------------------------------
# COMANDO TOPADD PARA VOLTAR A APARECER NOS RANKINGS

async def topadd(telegram_id, msg):
    async with get_cursor() as cursor:
        await cursor.execute("SELECT top FROM usuarios WHERE telegram_id = %s", (telegram_id,))
        result = await cursor.fetchone()

        if result[0] != 0:
            await msg.reply("⚙️ Oops, sua colocação nos rankings já está aparecendo, não se preocupe.")
        else:
            nome = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
            nome = f"[{nome}](tg://user?id={telegram_id})"
            await cursor.execute("UPDATE usuarios SET top = 1 WHERE telegram_id = %s", (telegram_id,))
            await msg.reply(f"🏅 Sua colocação no ranking pode ser visualizada novamente, {nome}!")

# -------------------------------------------
# COMANDO STATUS PARA VER INFORMAÇÕES DO JOGADOR

async def status(telegram_id, msg):
    if not msg.reply_to_message:
        status = msg.text.split()

        if len(status) < 2:
            async with get_cursor() as cursor:
                await cursor.execute("SELECT id, giros, sementes, (SELECT SUM(quantidade) FROM inventario WHERE id_user = %s) AS Ncards FROM usuarios WHERE telegram_id = %s", (telegram_id, telegram_id,))
                result = await cursor.fetchone()

            nome = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
            nome = f"[{nome}](tg://user?id={telegram_id})"

            await msg.reply(f"{nome}, essas são suas informações:\n\n🏷️ ID: `{result[0]}` \n🧃 Giros: {result[1]} \n🌾 Sementes: {result[2]} \n🍎 Frutinhas: {result[3] if result[3] != None else 0}")
        elif len(status) >= 2:
            if await is_admin(telegram_id, msg):
                if len(status) > 2:
                    await msg.reply("⚙️ Oops, você só pode escolher um usuário por vez para checar informações.")
                    return
                else:
                    async with get_cursor() as cursor:
                        try:
                            status = int(status[1])
                            await cursor.execute("SELECT u.id, u.giros, u.sementes, (SELECT SUM(quantidade) FROM inventario WHERE id_user = u.telegram_id) AS Ncards FROM usuarios u WHERE id = %s", (status,))
                            result = await cursor.fetchone()
                            user = f"`{status}`"
                        except ValueError:
                            username = status[1].lstrip('@')
                            await cursor.execute("SELECT u.id, u.giros, u.sementes, (SELECT SUM(quantidade) FROM inventario WHERE id_user = u.telegram_id) AS Ncards FROM usuarios u WHERE username = %s", (username,))
                            result = await cursor.fetchone()
                            user = f"@{username}"
                    
                    if result:
                        await msg.reply(f"Essas são as informações do habitante {user}:\n\n🏷️ ID: `{result[0]}` \n🧃 Giros: {result[1]} \n🌾 Sementes: {result[2]} \n🍎 Frutinhas: {result[3] if result[3] != None else 0}")
                    else:
                        await msg.reply(f"⚙️ Oops, parece que essa pessoa não é habitante da Vila Tutti-Frutti.")
    else:
        if await is_admin(telegram_id, msg):
            async with get_cursor() as cursor:
                await cursor.execute("SELECT u.id, u.giros, u.sementes, (SELECT SUM(quantidade) FROM inventario WHERE id_user = u.telegram_id) AS Ncards FROM usuarios u WHERE telegram_id = %s", (msg.reply_to_message.from_user.id,))
                result = await cursor.fetchone()

                if result:
                    await msg.reply(f"Essas são as informações do habitante @{msg.reply_to_message.from_user.username}:\n\n🏷️ ID: `{result[0]}` \n🧃 Giros: {result[1]} \n🌾 Sementes: {result[2]} \n🍎 Frutinhas: {result[3] if result[3] != None else 0}")
                else:
                    await msg.reply(f"⚙️ Oops, parece que essa pessoa não é habitante da Vila Tutti-Frutti.")

# -------------------------------------------
# COMANDO PARA TROCAR CARTAS

async def trocar(telegram_id, msg, bot):
    if not msg.reply_to_message:
        await msg.reply("⚙️ Oops, você precisa marcar a mensagem de quem fará a troca contigo.")
        return
    
    from states import em_troca
    if telegram_id in em_troca:
        msg_id = em_troca[telegram_id]["msg_id"]
        chat_id = str(msg.chat.id).replace("-100", "")
        link = f"https://t.me/c/{chat_id}/{msg_id}"
        
        await msg.reply(f"🍃 Você já está em uma [troca]({link}), por favor, finalize antes de tentar novamente.")
        return
    
    if msg.reply_to_message.from_user.id in em_troca:
        msg_id = em_troca[msg.reply_to_message.from_user.id]["msg_id"]
        chat_id = str(msg.chat.id).replace("-100", "")
        link = f"https://t.me/c/{chat_id}/{msg_id}"
        
        await msg.reply(f"🍃 @{msg.reply_to_message.from_user.username} já está em uma [troca]({link}), por favor, finalize antes de tentar novamente.")
        return
    
    entrada = msg.text[len("/trocar"):].strip()

    if "-" not in entrada:
        await msg.reply("⚙️ Oops, você precisa obrigatoriamente usar um hífen (-). Exemplo: /trocar 1001 1 - 1002 1.")
        return
    
    cartas = entrada.split("-")

    if len(cartas) < 2:
        await msg.reply("⚙️ Oops, você precisa informar as cartas que deseja trocar.")
        return
    else:
        oferta1 = cartas[0].strip().split()
        oferta2 = cartas[1].strip().split()
        imagem = "assets\\trocar.jpg"
        imagem = FSInputFile(imagem)

        if len(oferta1) %2 != 0 or len(oferta2) %2 != 0:
            await msg.reply("⚙️ Oops, parece que você esqueceu algum ID ou quantidade.")
            return
        else:
            try:   
                pares1 = [(int(oferta1[i]), int(oferta1[i + 1])) for i in range(0, len(oferta1), 2)]
                pares2 = [(int(oferta2[i]), int(oferta2[i + 1])) for i in range(0, len(oferta2), 2)]

                if len(pares1) > 5 or len(pares2) > 5:
                    await msg.reply("⚙️ Oops, você só pode trocar 5 IDs por vez.")
                    return

                nome1 = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
                nome1 = f"[{nome1}](tg://user?id={msg.from_user.id})"

                user2 = msg.reply_to_message.from_user
                nome2 = f"{user2.first_name} {user2.last_name or ''}".strip()
                nome2 = f"[{nome2}](tg://user?id={user2.id})"

                texto = f"🌻 {nome1} iniciou uma troca com {nome2}:\n\n{nome1} oferece:"

                async with get_cursor() as cursor:
                    sementes1 = 0
                    for id, quantidade in pares1:
                        isvalid = await exist_card(id, msg)
                        if isvalid:
                            Ncards = await carta_user(telegram_id, id, cursor)

                            if Ncards == None:
                                await msg.reply(f"🍃 Oops, você não possui a frutinha `{isvalid[0]}`.")
                                return
                            elif Ncards < quantidade:
                                await msg.reply(f"🍃 Oops, você só tem {Ncards} unidades da frutinha `{isvalid[0]}`.")
                                return
                            else:
                                id, nome, raridade, _, _, _, _, _ = isvalid

                                match raridade:
                                    case 1:
                                        sementes1 += 1000 * quantidade
                                    case 2:
                                        sementes1 += 500 * quantidade
                                    case 3:
                                        sementes1 += 250 * quantidade
                            
                                texto += f"\n{raridade_emojis.get(raridade, '❓')} `{id}`. {nome} ({quantidade}x)"
                        else:
                            return
                        
                    texto += f"\n\n{nome2} oferece:"
                    sementes2 = 0
                    for id, quantidade in pares2:
                        isvalid = await exist_card(id, msg)
                        if isvalid:
                            Ncards = await carta_user(user2.id, id, cursor)

                            if Ncards == None:
                                await msg.reply(f"🍃 Oops, {nome2} não possui a frutinha `{isvalid[0]}`.")
                                return
                            elif Ncards < quantidade:
                                await msg.reply(f"🍃 Oops, {nome2} só tem {Ncards} unidades da frutinha `{isvalid[0]}`.")
                                return
                            else:
                                id, nome, raridade, _, _, _, _, _ = isvalid

                                match raridade:
                                    case 1:
                                        sementes2 += 1000 * quantidade
                                    case 2:
                                        sementes2 += 500 * quantidade
                                    case 3:
                                        sementes2 += 250 * quantidade

                                texto += (f"\n{raridade_emojis.get(raridade, '❓')} `{id}`. {nome} ({quantidade}x)")
                        else:
                            return
                        
                if sementes1 != sementes2:
                    await msg.reply(f"🍃 Oops, verifique se sua troca é justa e tente novamente!")
                    return
                else:
                    opcoes = InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(text="ACEITAR 🍏", callback_data=f"troca_confirm"),
                            InlineKeyboardButton(text="RECUSAR 🍎", callback_data=f"troca_neg")
                        ]
                    ])

                    trocabtn = await bot.send_photo (
                        chat_id=msg.chat.id,
                        photo=imagem,
                        caption=texto,
                        reply_to_message_id=msg.message_id,
                        reply_markup=opcoes
                    )
                    
                    em_troca[telegram_id] = {"user1": telegram_id, "user2": user2.id, "msg_id": trocabtn.message_id, "pares1": pares1, "pares2": pares2}
                    em_troca[user2.id] = {"user1": telegram_id, "user2": user2.id, "msg_id": trocabtn.message_id, "pares1": pares1, "pares2": pares2}
                    
            except ValueError:
                await msg.reply("⚙️ Oops, só são aceitos IDs e quantidades numéricas.")
                return

# -------------------------------------------
# COMANDO PARA DOAR CARTAS

async def doar(telegram_id, msg):
    if not msg.reply_to_message:
        await msg.reply("⚙️ Oops, você precisa marcar o destinatário da doação.")
        return
        
    from states import em_troca
    if telegram_id in em_troca:
        msg_id = em_troca[telegram_id]["msg_id"]
        chat_id = str(msg.chat.id).replace("-100", "")
        link = f"https://t.me/c/{chat_id}/{msg_id}"
        
        await msg.reply(f"🍃 Você está em uma [troca]({link}) no momento, por favor, finalize antes de tentar fazer doações.")
        return
    
    if msg.reply_to_message.from_user.id in em_troca:
        msg_id = em_troca[msg.reply_to_message.from_user.id]["msg_id"]
        chat_id = str(msg.chat.id).replace("-100", "")
        link = f"https://t.me/c/{chat_id}/{msg_id}"
        
        await msg.reply(f"🍃 @{msg.reply_to_message.from_user.username} está em uma [troca]({link}) no momento, por favor, finalize antes de tentar novamente.")
        return

    entrada = msg.text.replace(",", " ")
    doações = entrada.split()[1:]

    if len(doações) < 1:
        await msg.reply("⚙️ Oops, você precisa escolher pelo menos uma carta para doar.")
        return
    elif len(doações) %2 != 0:
        await msg.reply("⚙️ Oops, parece que você esqueceu alguma coisa. Tem certeza de que forneceu todos os IDs e quantidades necessárias?")
        return
    else:
        try:
            pares = [(int(doações[i]), int(doações[i + 1])) for i in range(0, len(doações), 2)]
            cartas_doadas = 0
            user2 = msg.reply_to_message.from_user.id

            async with get_cursor() as cursor:
                for carta_id, quantidade in pares:
                    inv = await carta_user(telegram_id, carta_id, cursor)
                    if inv != 0 and inv != None:
                        if quantidade <= 0:
                            continue

                        quantidade = min(quantidade, inv)
                        valor = inv - quantidade

                        if valor > 0:
                            await cursor.execute("UPDATE inventario SET quantidade = %s WHERE id_user = %s AND id_carta = %s", (valor, telegram_id, carta_id,))
                        else:
                            await cursor.execute("DELETE FROM inventario WHERE id_user = %s AND id_carta = %s", (telegram_id, carta_id,))

                        cartas_doadas += quantidade

                        inv2 = await carta_user(user2, carta_id, cursor)
                        
                        if inv2 == None or inv2 == 0:
                            await cursor.execute("INSERT INTO inventario (id_user, id_carta, quantidade) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE quantidade = quantidade + %s", (user2, carta_id, quantidade, quantidade,))      
                        else:
                            await cursor.execute("UPDATE inventario SET quantidade = quantidade + %s WHERE id_user = %s AND id_carta = %s", (quantidade, user2, carta_id,))

                        await cursor.execute("INSERT INTO extrato (remetente, receptor, comando, carta, quantidade) VALUES(%s, %s, %s, %s, %s)", (telegram_id, msg.reply_to_message.from_user.id, "doar", carta_id, quantidade,))

                if cartas_doadas > 0:
                    if cartas_doadas > 1:
                        await msg.reply(f"🍏 Suas frutinhas foram doadas com sucesso.")
                    elif cartas_doadas == 1: 
                        await msg.reply(f"🍏 Sua frutinha foi doada com sucesso.")
                else:
                    await msg.reply("⚙️ Oops, parece que você tentou doar cartas que não existem na sua cesta.")
        except ValueError:
            await msg.reply("⚙️ Oops, você só pode doar cartas com base no ID.")

# -------------------------------------------
# COMANDO PARA DOAR SEMENTES

async def doarsemente(telegram_id, msg):
    if not msg.reply_to_message:
        await msg.reply("⚙️ Oops, você precisa marcar o destinatário da doação.")
        return
    
    entrada = msg.text.replace(",", " ")
    doações = entrada.split()[1:]

    if len(doações) < 1:
        await msg.reply("⚙️ Oops, você precisa informar o número de sementes para doar.")
        return
    elif len(doações) > 1:
        await msg.reply("⚙️ Oops, parece que você inseriu informações demais no comando.")
        return
    else:
        try:
            qnt = int(doações[0])

            async with get_cursor() as cursor:
                await cursor.execute("SELECT sementes FROM usuarios WHERE telegram_id = %s", (telegram_id,))
                result = await cursor.fetchone()
                sementes = result[0]

                if sementes < qnt:
                    if sementes != 0:   
                        await msg.reply(f"⚙️ Oops, você tem apenas {sementes} sementes.")
                        return
                    else:
                        await msg.reply(f"⚙️ Oops, você não tem nenhuma semente.")
                        return
                else:
                    await cursor.execute("UPDATE usuarios SET sementes = sementes - %s WHERE telegram_id = %s", (qnt, telegram_id,))
                    await cursor.execute("UPDATE usuarios SET sementes = sementes + %s WHERE telegram_id = %s", (qnt, msg.reply_to_message.from_user.id,))
                    await cursor.execute("INSERT INTO extrato (remetente, receptor, comando, quantidade) VALUES(%s, %s, %s, %s)", (telegram_id, msg.reply_to_message.from_user.id, "doars", qnt,))

            if qnt > 1:
                await msg.reply("🍏 Suas sementes foram doadas com sucesso.")
            else:
                await msg.reply("🍏 Sua semente foi doada com sucesso.")
        except ValueError:
            await msg.reply("⚙️ Oops, você só pode doar sementes informando a quantidade.")

# -------------------------------------------
# COMANDO PARA DOAR COLHEITAS

async def doarcolheita(telegram_id, msg):
    if not msg.reply_to_message:
        await msg.reply("⚙️ Oops, você precisa marcar o destinatário da doação.")
        return
    
    entrada = msg.text.replace(",", " ")
    doações = entrada.split()[1:]

    if len(doações) < 1:
        await msg.reply("⚙️ Oops, você precisa informar o número de colheitas para doar.")
        return
    elif len(doações) > 1:
        await msg.reply("⚙️ Oops, parece que você inseriu informações demais no comando.")
        return
    else:
        try:
            qnt = int(doações[0])

            async with get_cursor() as cursor:
                await cursor.execute("SELECT giros FROM usuarios WHERE telegram_id = %s", (telegram_id,))
                result = await cursor.fetchone()
                giros = result[0]

                if giros < qnt:
                    if giros != 0:   
                        await msg.reply(f"⚙️ Oops, você tem apenas {giros} colheitas.")
                        return
                    else:
                        await msg.reply(f"⚙️ Oops, você não tem nenhuma colheita.")
                        return
                else:
                    await cursor.execute("UPDATE usuarios SET giros = giros - %s WHERE telegram_id = %s", (qnt, telegram_id,))
                    await cursor.execute("UPDATE usuarios SET giros = giros + %s WHERE telegram_id = %s", (qnt, msg.reply_to_message.from_user.id,))
                    await cursor.execute("INSERT INTO extrato (remetente, receptor, comando, quantidade) VALUES(%s, %s, %s, %s)", (telegram_id, msg.reply_to_message.from_user.id, "doarc", qnt,))

            if qnt > 1:
                await msg.reply("🍏 Suas colheitas foram doadas com sucesso.")
            else:
                await msg.reply("🍏 Sua colheita foi doada com sucesso.")
        except ValueError:
            await msg.reply("⚙️ Oops, você só pode doar colheitas informando a quantidade.")

# -------------------------------------------
# COMANDO PARA DOAR TODO O INVENTÁRIO

async def doarinv(telegram_id, msg):
    if not msg.reply_to_message:
        await msg.reply("⚙️ Oops, você precisa marcar o destinatário da doação.")
        return

    from states import em_troca
    if telegram_id in em_troca:
        msg_id = em_troca[telegram_id]["msg_id"]
        chat_id = str(msg.chat.id).replace("-100", "")
        link = f"https://t.me/c/{chat_id}/{msg_id}"
        
        await msg.reply(f"🍃 Você está em uma [troca]({link}) no momento, por favor, finalize antes de tentar fazer doações.")
        return
    
    if msg.reply_to_message.from_user.id in em_troca:
        msg_id = em_troca[msg.reply_to_message.from_user.id]["msg_id"]
        chat_id = str(msg.chat.id).replace("-100", "")
        link = f"https://t.me/c/{chat_id}/{msg_id}"
        
        await msg.reply(f"🍃 @{msg.reply_to_message.from_user.username} está em uma [troca]({link}) no momento, por favor, finalize antes de tentar novamente.")
        return
    
    dest = msg.reply_to_message.from_user.id

    async with get_cursor() as cursor:
        await cursor.execute("SELECT id_carta, quantidade FROM inventario WHERE id_user = %s", (telegram_id,))
        inv = await cursor.fetchall()

        if inv:
            Ncards = sum(carta[1] for carta in inv)
            doarinv = []
            for carta, quantidade in inv:
                inv2 = await carta_user(dest, carta, cursor)
                doarinv.append((carta, quantidade))

                if inv2:
                    await cursor.execute("UPDATE inventario SET quantidade = quantidade + %s WHERE id_user = %s AND id_carta = %s", (quantidade, dest, carta,))
                else:
                    await cursor.execute("INSERT INTO inventario (id_user, id_carta, quantidade) VALUES(%s, %s, %s)", (dest, carta, quantidade,))
            cartas = ", ".join([f"`{id}` {qtd}" for id, qtd in doarinv])
            await cursor.execute("DELETE FROM inventario WHERE id_user = %s", (telegram_id,))
            await cursor.execute("INSERT INTO extrato (remetente, receptor, comando, quantidade, cartas) VALUES(%s, %s, %s, %s, %s)", (telegram_id, dest, "doarinv", Ncards, cartas,))
            await msg.reply(f"🍏 Todas as {Ncards} frutinhas da sua cestinha foram doadas com sucesso!")
        else:
            await msg.reply("⚙️ Oops, parece que sua cestinha ainda está vazia.")
            return
        
# -------------------------------------------
# COMANDO PARA DOAR UMA CATEGORIA INTEIRA

async def doarcat(telegram_id, msg):
    entrada = msg.text.split(' ', 1)

    if not msg.reply_to_message:
        await msg.reply("⚙️ Oops, você precisa marcar o destinatário da doação.")
        return
    elif len(entrada) < 2:
        await msg.reply("⚙️ Oops, parece que você não informou a categoria.")
        return
    else:
        from states import em_troca
        if telegram_id in em_troca:
            msg_id = em_troca[telegram_id]["msg_id"]
            chat_id = str(msg.chat.id).replace("-100", "")
            link = f"https://t.me/c/{chat_id}/{msg_id}"
            
            await msg.reply(f"🍃 Você está em uma [troca]({link}) no momento, por favor, finalize antes de tentar fazer doações.")
            return
        
        if msg.reply_to_message.from_user.id in em_troca:
            msg_id = em_troca[msg.reply_to_message.from_user.id]["msg_id"]
            chat_id = str(msg.chat.id).replace("-100", "")
            link = f"https://t.me/c/{chat_id}/{msg_id}"
            
            await msg.reply(f"🍃 @{msg.reply_to_message.from_user.username} está em uma [troca]({link}) no momento, por favor, finalize antes de tentar novamente.")
            return
        
        busca = entrada[1]
        if busca.upper() in ("MORANGEEK", "ASIAFARM", "STREAMBERRY", "FRUITMIX"):
            cat = busca.upper()
        else:
            await msg.reply("⚙️ Oops, essa categoria não existe.")
            return
    
    dest = msg.reply_to_message.from_user.id

    async with get_cursor() as cursor:
        await cursor.execute("SELECT c.id, i.quantidade FROM cartas c RIGHT JOIN inventario i ON c.id = i.id_carta AND i.id_user = %s WHERE c.categoria = %s", (telegram_id, cat,))
        inv = await cursor.fetchall()

        if inv:
            Ncards = sum(carta[1] for carta in inv)

            doarcat = []
            for carta, quantidade in inv:
                inv2 = await carta_user(dest, carta, cursor)
                await cursor.execute("DELETE FROM inventario WHERE id_user = %s AND id_carta = %s", (telegram_id, carta,))
                doarcat.append((carta, quantidade))

                if inv2:
                    await cursor.execute("UPDATE inventario SET quantidade = quantidade + %s WHERE id_user = %s AND id_carta = %s", (quantidade, dest, carta,))
                else:
                    await cursor.execute("INSERT INTO inventario (id_user, id_carta, quantidade) VALUES(%s, %s, %s)", (dest, carta, quantidade,))
            cartas = ", ".join([f"`{id}` {qtd}" for id, qtd in doarcat])
            await cursor.execute("INSERT INTO extrato (remetente, receptor, comando, quantidade, cartas) VALUES(%s, %s, %s, %s, %s)", (telegram_id, dest, f"doarcat,{cat}", Ncards, cartas,))        
            await msg.reply(f"🍏 Todas as suas {Ncards} frutinhas da categoria {cat} foram doadas com sucesso!")
        else:
            await msg.reply(f"⚙️ Oops, parece que você não tem nenhuma frutinha da categoria {cat}.")
            return
    
# -------------------------------------------
# COMANDO PARA DOAR UMA SUB INTEIRA

async def doarcol(telegram_id, msg):
    entrada = msg.text.split(' ', 1)

    if not msg.reply_to_message:
        await msg.reply("⚙️ Oops, você precisa marcar o destinatário da doação.")
        return
    elif len(entrada) < 2:
        await msg.reply("⚙️ Oops, parece que você não informou a colheita.")
        return
    else:
        from states import em_troca
        if telegram_id in em_troca:
            msg_id = em_troca[telegram_id]["msg_id"]
            chat_id = str(msg.chat.id).replace("-100", "")
            link = f"https://t.me/c/{chat_id}/{msg_id}"
            
            await msg.reply(f"🍃 Você está em uma [troca]({link}) no momento, por favor, finalize antes de tentar fazer doações.")
            return
        
        if msg.reply_to_message.from_user.id in em_troca:
            msg_id = em_troca[msg.reply_to_message.from_user.id]["msg_id"]
            chat_id = str(msg.chat.id).replace("-100", "")
            link = f"https://t.me/c/{chat_id}/{msg_id}"
            
            await msg.reply(f"🍃 @{msg.reply_to_message.from_user.username} está em uma [troca]({link}) no momento, por favor, finalize antes de tentar novamente.")
            return
    
        busca = entrada[1]
    
    dest = msg.reply_to_message.from_user.id
    sub = await exist_sub(busca, msg)

    if sub:
        async with get_cursor() as cursor:
            await cursor.execute("SELECT c.id, i.quantidade FROM cartas c RIGHT JOIN inventario i ON c.id = i.id_carta AND i.id_user = %s WHERE c.subcategoria = %s", (telegram_id, sub[1],))
            inv = await cursor.fetchall()

            if inv:
                Ncards = sum(carta[1] for carta in inv)

                doarcol = []
                for carta, quantidade in inv:
                    inv2 = await carta_user(dest, carta, cursor)
                    await cursor.execute("DELETE FROM inventario WHERE id_user = %s AND id_carta = %s", (telegram_id, carta,))
                    doarcol.append((carta, quantidade))
                    
                    if inv2:
                        await cursor.execute("UPDATE inventario SET quantidade = quantidade + %s WHERE id_user = %s AND id_carta = %s", (quantidade, dest, carta,))
                    else:
                        await cursor.execute("INSERT INTO inventario (id_user, id_carta, quantidade) VALUES(%s, %s, %s)", (dest, carta, quantidade,))
                cartas = ", ".join([f"`{id}` {qtd}" for id, qtd in doarcol])
                await cursor.execute("INSERT INTO extrato (remetente, receptor, comando, quantidade, cartas) VALUES(%s, %s, %s, %s, %s)", (telegram_id, dest, f"doarcol,{sub[1]}", Ncards, cartas,))        
                await msg.reply(f"🍏 Todas as suas {Ncards} frutinhas da coleção {sub[1]} foram doadas com sucesso!")
            else:
                await msg.reply(f"⚙️ Oops, parece que você não tem nenhuma frutinha da colheita {sub[1]}.")
                return
    else:
        return

# -------------------------------------------
# COMANDO PARA DOAR UMA TAG INTEIRA

async def doartag(telegram_id, msg):
    entrada = msg.text.split(' ', 1)

    if not msg.reply_to_message:
        await msg.reply("⚙️ Oops, você precisa marcar o destinatário da doação.")
        return
    elif len(entrada) < 2:
        await msg.reply("⚙️ Oops, parece que você não informou a tag.")
        return
    else:
        from states import em_troca
        if telegram_id in em_troca:
            msg_id = em_troca[telegram_id]["msg_id"]
            chat_id = str(msg.chat.id).replace("-100", "")
            link = f"https://t.me/c/{chat_id}/{msg_id}"
            
            await msg.reply(f"🍃 Você está em uma [troca]({link}) no momento, por favor, finalize antes de tentar fazer doações.")
            return
        
        if msg.reply_to_message.from_user.id in em_troca:
            msg_id = em_troca[msg.reply_to_message.from_user.id]["msg_id"]
            chat_id = str(msg.chat.id).replace("-100", "")
            link = f"https://t.me/c/{chat_id}/{msg_id}"
            
            await msg.reply(f"🍃 @{msg.reply_to_message.from_user.username} está em uma [troca]({link}) no momento, por favor, finalize antes de tentar novamente.")
            return
        busca = entrada[1]
    
    dest = msg.reply_to_message.from_user.id
    tag = await exist_tag(busca)

    if tag:
        async with get_cursor() as cursor:
            await cursor.execute("SELECT c.id, i.quantidade FROM cartas c RIGHT JOIN inventario i ON c.id = i.id_carta AND i.id_user = %s WHERE c.tag = %s", (telegram_id, tag[0],))
            inv = await cursor.fetchall()

            if inv:
                Ncards = sum(carta[1] for carta in inv)
                doartag = []

                for carta, quantidade in inv:
                    inv2 = await carta_user(dest, carta, cursor)
                    await cursor.execute("DELETE FROM inventario WHERE id_user = %s AND id_carta = %s", (telegram_id, carta,))
                    doartag.append((carta, quantidade))

                    if inv2:
                        await cursor.execute("UPDATE inventario SET quantidade = quantidade + %s WHERE id_user = %s AND id_carta = %s", (quantidade, dest, carta,))
                    else:
                        await cursor.execute("INSERT INTO inventario (id_user, id_carta, quantidade) VALUES(%s, %s, %s)", (dest, carta, quantidade,))
                cartas = ", ".join([f"`{id}` {qtd}" for id, qtd in doartag])
                await cursor.execute("INSERT INTO extrato (remetente, receptor, comando, quantidade, cartas) VALUES(%s, %s, %s, %s, %s)", (telegram_id, dest, f"doartag,{tag[0]}", Ncards, cartas,))        
                await msg.reply(f"🍏 Todas as suas {Ncards} frutinhas da tag {tag[0]} foram doadas com sucesso!")
            else:
                await msg.reply(f"⚙️ Oops, parece que você não tem nenhuma frutinha da tag {tag[0]}.")
                return
    else:
        await msg.reply(f"⚙️ Oops, parece que essa tag não existe.")
        return
    
# -------------------------------------------
# COMANDO PARA DOAR WISHLIST

async def doarwish(telegram_id, msg):
    if not msg.reply_to_message:
        await msg.reply("⚙️ Oops, você precisa marcar o destinatário da doação.")
        return
    else:
        from states import em_troca
        if telegram_id in em_troca:
            msg_id = em_troca[telegram_id]["msg_id"]
            chat_id = str(msg.chat.id).replace("-100", "")
            link = f"https://t.me/c/{chat_id}/{msg_id}"
            
            await msg.reply(f"🍃 Você está em uma [troca]({link}) no momento, por favor, finalize antes de tentar fazer doações.")
            return
        
        if msg.reply_to_message.from_user.id in em_troca:
            msg_id = em_troca[msg.reply_to_message.from_user.id]["msg_id"]
            chat_id = str(msg.chat.id).replace("-100", "")
            link = f"https://t.me/c/{chat_id}/{msg_id}"
            
            await msg.reply(f"🍃 @{msg.reply_to_message.from_user.username} está em uma [troca]({link}) no momento, por favor, finalize antes de tentar novamente.")
            return
    
        dest = msg.reply_to_message.from_user.id
        entrada = msg.text.split()

        if len(entrada) < 2:
            wl = await get_wl(dest)
            cat = False
        else:
            cat = entrada[1].upper()

            if cat in ("MORANGEEK", "ASIAFARM", "STREAMBERRY", "FRUITMIX"):
                wl = await get_wl(dest, cat)
            else:
                await msg.reply("⚙️ Oops, essa categoria não existe.")
                return
    
    if wl:
        Ncards = 0
        async with get_cursor() as cursor:
            doarw = []
            for carta in wl:
                inv = await carta_user(telegram_id, carta[0], cursor)
                inv2 = await carta_user(dest, carta[0], cursor)

                if inv:
                    await cursor.execute("DELETE FROM inventario WHERE id_carta = %s AND id_user = %s", (carta[0], telegram_id,))
                    Ncards += inv
                    doarw.append((carta[0], inv))

                    if inv2:
                        await cursor.execute("UPDATE inventario SET quantidade = quantidade + %s WHERE id_user = %s AND id_carta = %s", (inv, dest, carta[0],))
                    else:
                        await cursor.execute("INSERT INTO inventario (id_user, id_carta, quantidade) VALUES (%s, %s, %s)", (dest, carta[0], inv,))
                else:
                    continue
            
            if Ncards > 0:
                cartas = ", ".join([f"`{id}` {qtd}" for id, qtd in doarw])
                await cursor.execute("INSERT INTO extrato (remetente, receptor, comando, quantidade, cartas) VALUES(%s, %s, %s, %s, %s)", (telegram_id, dest, "doarw", Ncards, cartas,))        
                
                if cat:
                    await msg.reply(f"🍏 Um total de {Ncards} frutinhas da wishlist {cat} de @{msg.reply_to_message.from_user.username} foram doadas com sucesso!")
                else:
                    await msg.reply(f"🍏 Um total de {Ncards} frutinhas da wishlist de @{msg.reply_to_message.from_user.username} foram doadas com sucesso!")
            else:
                await msg.reply(f"⚙️ Oops, parece que você não tem nenhuma carta da wishlist de @{msg.reply_to_message.from_user.username}.")
    else:
        await msg.reply(f"⚙️ Oops, parece que a wishlist de @{msg.reply_to_message.from_user.username} ainda está vazia.")
        return

# -------------------------------------------
# COMANDO DESCARTAR PARA VENDER CARTAS

async def descartar(telegram_id, msg):
    entrada = msg.text.replace(",", " ")
    vendas = entrada.split()[1:]

    if len(vendas) < 1:
        await msg.reply("⚙️ Oops, você precisa escolher pelo menos uma carta para descartar.")
        return
    elif len(vendas) %2 != 0:
        await msg.reply("⚙️ Oops, parece que você esqueceu alguma coisa. Tem certeza de que forneceu todos os IDs e quantidades necessárias?")
        return
    else:
        try:
            pares = [(int(vendas[i]), int(vendas[i + 1])) for i in range(0, len(vendas), 2)]
            cartas_vendidas = 0
            listavendas = []
            sementes = 0

            async with get_cursor() as cursor:
                for carta_id, quantidade in pares:
                    inv = await carta_user(telegram_id, carta_id, cursor)
                    if inv != 0 and inv != None:
                        if quantidade <= 0:
                            continue

                        await cursor.execute("SELECT raridade FROM cartas WHERE id = %s", (carta_id,))
                        raridade = await cursor.fetchone()

                        quantidade = min(quantidade, inv)
                        valor = inv - quantidade

                        if valor > 0:
                            await cursor.execute("UPDATE inventario SET quantidade = %s WHERE id_user = %s AND id_carta = %s", (valor, telegram_id, carta_id,))
                        else:
                            await cursor.execute("DELETE FROM inventario WHERE id_user = %s AND id_carta = %s", (telegram_id, carta_id,))

                        match raridade[0]:
                            case 1:
                                sementes += 1000 * quantidade
                            case 2:
                                sementes += 500 * quantidade
                            case 3:
                                sementes += 250 * quantidade

                        cartas_vendidas += quantidade
                        listavendas.append(f"{carta_id} ({quantidade}x)")

                if cartas_vendidas > 0:
                    await cursor.execute("UPDATE usuarios SET sementes = sementes + %s WHERE telegram_id = %s", (sementes, telegram_id,))

                    if cartas_vendidas > 1:
                        await msg.reply(f"Um passarinho faminto comeu suas seguintes frutinhas: {', '.join(listavendas)}! Mas não se preocupe, ele te recompensou com {sementes} sementes. 🦜")
                    elif cartas_vendidas == 1: 
                        await msg.reply(f"Um passarinho faminto comeu sua frutinha: {listavendas[0].split()[0]}! Mas não se preocupe, ele te recompensou com {sementes} sementes. 🦜")
                else:
                    await msg.reply("⚙️ Oops, parece que você tentou descartar cartas que não existem na sua cesta.")
        except ValueError:
            await msg.reply("⚙️ Oops, você só pode descartar cartas com base no ID.")

# -------------------------------------------
# COMANDO DESCARTAR SUBCATEGORIA PARA VENDER CARTAS

async def descartarsub(telegram_id, msg):
    venda = msg.text.split(' ', 1)

    if len(venda) < 2:
        await msg.reply("⚙️ Oops, você precisa escolher pelo menos uma subcategoria para descartar.")
    else:
        sub = venda[1]
        result = await exist_sub(sub, msg)

        if result:
            sub = result[1]
            sementes = 0
            async with get_cursor() as cursor:
                await cursor.execute("SELECT c.id, c.raridade, i.quantidade FROM cartas c INNER JOIN inventario i ON c.id = i.id_carta AND i.id_user = %s WHERE c.subcategoria = %s", (telegram_id, sub,))
                descarte = await cursor.fetchall()

                if descarte:
                    for id, raridade, quantidade in descarte:
                        await cursor.execute("DELETE FROM inventario WHERE id_user = %s AND id_carta = %s", (telegram_id, id,))

                        match raridade:
                            case 1:
                                sementes += 1000 * quantidade
                            case 2:
                                sementes += 500 * quantidade
                            case 3:
                                sementes += 250 * quantidade

                    await cursor.execute("UPDATE usuarios SET sementes = sementes + %s WHERE telegram_id = %s", (sementes, telegram_id,))
                    await msg.reply(f"Um passarinho faminto comeu toda sua colheita {sub}! Mas não se preocupe, ele te recompensou com {sementes} sementes. 🦜")
                else:
                    await msg.reply("⚙️ Oops, parece que não há nada dessa colheita na sua cesta para vender.")

# -------------------------------------------
# COMANDO DESCARTAR CATEGORIA PARA VENDER CARTAS

async def descartarcat(telegram_id, msg):
    venda = msg.text.split()

    if len(venda) < 2:
        await msg.reply("⚙️ Oops, você precisa escolher pelo menos uma categoria para descartar.")
    else:
        cat = venda[1].upper()
        if cat in ("MORANGEEK", "ASIAFARM", "STREAMBERRY", "FRUITMIX"):
            sementes = 0
            async with get_cursor() as cursor:
                await cursor.execute("SELECT c.id, c.raridade, i.quantidade FROM cartas c INNER JOIN inventario i ON c.id = i.id_carta AND i.id_user = %s WHERE c.categoria = %s", (telegram_id, cat,))
                descarte = await cursor.fetchall()

                if descarte:
                    for id, raridade, quantidade in descarte:
                        await cursor.execute("DELETE FROM inventario WHERE id_user = %s AND id_carta = %s", (telegram_id, id,))

                        match raridade:
                            case 1:
                                sementes += 1000 * quantidade
                            case 2:
                                sementes += 500 * quantidade
                            case 3:
                                sementes += 250 * quantidade
                                
                    await cursor.execute("UPDATE usuarios SET sementes = sementes + %s WHERE telegram_id = %s", (sementes, telegram_id,))
                    await msg.reply(f"Um passarinho faminto comeu toda sua colheita {cat}! Mas não se preocupe, ele te recompensou com {sementes} sementes. 🦜")
                else:
                    await msg.reply("⚙️ Oops, parece que não há nada dessa categoria na sua cesta para vender.")
        else:
            await msg.reply("⚙️ Oops, essa categoria não existe.")

# -------------------------------------------
# COMANDO CHECKFRUIT PARA CONSULTAR CARTAS

async def checkfruit(telegram_id, msg):
    if not msg.reply_to_message:
        await msg.reply("⚙️ Oops, parece que não há nenhuma mensagem marcada.")
        return

    busca = msg.reply_to_message.text or msg.reply_to_message.caption  
    ids = re.findall(r'\d+', busca)

    if not ids:
        await msg.reply("⚙️ Oops, parece que não há nenhum ID na mensagem marcada.")
        return
    
    async with get_cursor() as cursor:
        texto = "🔎 Checando os itens na sua cestinha...\n"
        cartas = 0
        for id in ids:
            quantidade = await carta_user(telegram_id, id, cursor)

            if quantidade == None:
                quantidade = 0
            
            await cursor.execute("SELECT nome, raridade FROM cartas WHERE id = %s", (id,))
            result = await cursor.fetchone()

            if result:
                cartas += 1
                nome = result[0]
                raridade = result[1]
                texto += f"\n{raridade_emojis.get(raridade, '❓')} `{id}`. {nome} ({quantidade}x)"
            else:
                continue
    
    if cartas >= 1:
        await msg.reply(texto)
    else:
        await msg.reply("⚙️ Oops, parece que nenhum desses IDs é válido.")

# -------------------------------------------
# COMANDO SABOREAR PARA RECOMPENSA DE COL COMPLETA

async def saborear(telegram_id, msg):
    busca = msg.text.split(' ', 1)

    if len(busca) < 2:
        await msg.reply("⚙️ Oops, parece que você não forneceu uma subcategoria para saborear.")
        return

    buscasub = busca[1]
    result = await exist_sub(buscasub, msg)

    if result:
        cat = result[0]
        sub = result[1]

        async with get_cursor() as cursor:
            await cursor.execute("SELECT subcategoria FROM saboreados WHERE id_user = %s AND subcategoria = %s", (telegram_id, sub,))
            saboreou = await cursor.fetchone()

            if saboreou:
                await msg.reply(f"⚙️ Oops, parece que você já saboreou a subcategoria {sub}.")
                return
            else:
                await cursor.execute("SELECT COUNT(*) FROM cartas WHERE subcategoria = %s", (sub,))
                scontagem = await cursor.fetchone()
                Ncards = scontagem[0]

                await cursor.execute("SELECT COUNT(*) FROM cartas c JOIN inventario i ON c.id = i.id_carta WHERE c.subcategoria = %s AND i.id_user = %s", (sub, telegram_id,))
                ucontagem = await cursor.fetchone()
                Ucards = ucontagem[0]

                if Ncards == Ucards:
                    await cursor.execute("INSERT INTO saboreados (id_user, subcategoria, categoria) VALUES (%s, %s, %s)", (telegram_id, sub, cat,))
                    await cursor.execute("SELECT vip FROM usuarios WHERE telegram_id = %s", (telegram_id,))
                    isvip = await cursor.fetchone()
                    vip = isvip[0]
                    
                    if vip == 0:
                        sementes = 100
                    else:
                        sementes = 250

                    await cursor.execute("UPDATE usuarios SET sementes = sementes + %s WHERE telegram_id = %s", (sementes, telegram_id,))
                    await msg.reply(f"Agora que sua colheita está completa, você pode saborear dessas frutinhas! A terra te recompensou com {sementes} sementes. 🎋")
                else:
                    await msg.reply(f"⚙️ Oops, parece que ainda faltam algumas frutinhas para completar sua colheita.")

# -------------------------------------------
# COMANDO LOJINHA PARA COMPRAR COISAS

async def lojinha(bot, msg):
    texto = "🍊 Boas-vindas à lojinha da Laranjinha!\n\nGaste suas sementes e compre melhorias para sua colheita!"

    imagem = "assets\\loja.png"
    imagem = FSInputFile(imagem)

    lojaopts = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="GIROS 🌾", callback_data=f'loja_giros'),
                InlineKeyboardButton(text="VIP 🌿", callback_data=f'loja_vip')
            ],
            [
                InlineKeyboardButton(text="CAIXINHA 📦", callback_data='loja_caixinha'),
                InlineKeyboardButton(text="DIVORCIAR 🔖", callback_data=f'loja_divorcio')
            ],
            [
                InlineKeyboardButton(text="PERFIL PERSONALIZADO 🪵", callback_data='loja_perfil')
            ]
        ]
    )

    await bot.send_photo(
        chat_id=msg.chat.id,
        photo=imagem,
        caption=texto,
        reply_to_message_id=msg.message_id,
        reply_markup=lojaopts
    )

# -------------------------------------------
# COMANDO CASAR PARA CASAR-SE COM ALGUÉM

async def casar(telegram_id, msg, bot):
    casamento = msg.text.split()

    if len(casamento) < 2:
        await msg.reply("⚙️ Oops, parece que você não informou ao cartório quem será pedido em casamento.")
    elif len(casamento) >= 2:
        if len(casamento) > 2:
            await msg.reply("⚙️ Oops, você só pode se casar com uma pessoa.")
            return
        else:
            try:
                casamento = int(casamento[1])
                await msg.reply("⚙️ Oops, o casamento só pode ser efetuado com base em username. Exemplo: /casar @user.")
                return
            except ValueError:
                async with get_cursor() as cursor:
                    username = casamento[1].lstrip('@')
                    user = f"@{username}"
                
                    if username == msg.from_user.username:
                        await msg.reply("⚙️ Oops, você não pode casar consigo mesmo.")
                        return

                    await cursor.execute("SELECT parceiro FROM usuarios WHERE telegram_id = %s", (telegram_id,))
                    casado1 = await cursor.fetchone()

                    await cursor.execute("SELECT parceiro, telegram_id FROM usuarios WHERE username = %s", (username,))
                    casado2 = await cursor.fetchone()
                
                if not casado2:
                    await msg.reply(f"⚙️ Oops, parece que essa pessoa não é habitante da Vila Tutti-Frutti.")
                elif not casado1[0] and not casado2[0]:
                    casaropts = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(text="ACEITAR 💐", callback_data=f'casar_acpt_{telegram_id}_{casado2[1]}'),
                                InlineKeyboardButton(text="RECUSAR 💔", callback_data=f'casar_rcs_{telegram_id}_{casado2[1]}')
                            ]
                        ]
                    )

                    await bot.send_message(casado2[1], f"💌 O amor está no ar! \n@{msg.from_user.username} acabou de se declarar e te pediu em casamento, você aceita?", reply_markup=casaropts)
                    await msg.reply(f"Você está prestes a declarar seu amor por {user}! 💐\n\n— Seu pedido de casamento foi enviado, agora é só esperar pela resposta.")
                elif casado1[0]:
                    await msg.reply(f"💌 Aqui na Vila Tutti-Frutti, seu coração tem lugar para só uma pessoa... e você já é casado com @{casado1[0]}!")
                elif casado2[0]:
                    await msg.reply(f"💔 Infelizmente {user} já tem um parceiro e não pode corresponder ao seu amor.")
                else:
                    await msg.reply("⚙️ Oops, por algum motivo não foi possível realizar seu casamento.")
    else:
        await msg.reply("⚙️ Oops, parece que você não informou ao cartório quem será pedido em casamento.")

# -------------------------------------------
# COMANDO PARA ALTERAÇÃO DE WISHLIST

async def wish(telegram_id, msg, bot):
    entrada = msg.text.replace(",", " ")
    cards = entrada.split()[1:]

    if len(cards) < 1:
        await wishlist(telegram_id, msg)
        return
    else:
        chatid = msg.chat.id
        chat = await bot.get_chat(chatid)

        if chat.type != "private":
            await msg.reply("⚙️ Oops, você só pode editar a wishlist em chat privado.")
            return
    
    async with get_cursor() as cursor:
        novos = []
        removidos = []

        try:
            for id in cards:
                card = int(id)
                result = await exist_card(card, msg)

                if result:
                    cat = result[4]
                    await cursor.execute("SELECT COUNT(*) FROM wishlists WHERE id_user = %s AND categoria = %s", (telegram_id, cat,))
                    Ncards = await cursor.fetchone()
                    await cursor.execute("SELECT id_carta FROM wishlists WHERE id_user = %s AND id_carta = %s", (telegram_id, card,))
                    iswish = await cursor.fetchone()

                    if not iswish:
                        if Ncards[0] < 20:
                            novos.append(id)
                        else:
                            await msg.reply(f"⚙️ Oops, você já atingiu o limite de 20 cartas da categoria {cat} na sua wishlist.")
                            return
                    else:
                        removidos.append(id)
                else:
                    return
        except ValueError:
            await msg.reply(f"⚙️ Oops, você só pode adicionar cards à wishlist com base no ID.")
            return
        
        texto = "🔖 Certo, sua wishlist foi alterada com sucesso! "

        if novos:
            texto += f"Cards adicionados à lista: {', '.join(novos)}. "
            for id in novos:
                await cursor.execute("SELECT categoria FROM cartas WHERE id = %s", (id,))
                cat = await cursor.fetchone()
                await cursor.execute("INSERT INTO wishlists (id_user, id_carta, categoria) VALUES (%s, %s, %s)", (telegram_id, id, cat[0]))

        elif removidos:
            texto += f"Cards removidos: {', '.join(removidos)}."
            for id in removidos:
                await cursor.execute("DELETE FROM wishlists WHERE id_user = %s AND id_carta = %s", (telegram_id, id,))

        else:
            await msg.reply("⚙️ Oops, parece que ocorreu algum erro ao tentar alterar sua wishlist.")
            return

        await msg.reply(texto)

# -------------------------------------------
# COMANDO PARA VISUALIZAÇÃO DE WISHLIST

async def wishlist(telegram_id, msg):
    if msg.chat.id == FRUITMIX:
        cat = True
        wl = await get_wl(telegram_id, "FRUITMIX")
        emoji = "🫐"
    elif msg.chat.id == STREAMBERRY:
        cat = True
        wl = await get_wl(telegram_id, "STREAMBERRY")
        emoji = "🍋"
    elif msg.chat.id == MORANGEEK:
        cat = True
        wl = await get_wl(telegram_id, "MORANGEEK")
        emoji = "🍏"
    elif msg.chat.id == ASIAFARM:
        cat = True
        wl = await get_wl(telegram_id, "ASIAFARM")
        emoji = "🍇"
    else:
        cat = False

    nome = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
    nome = f"[{nome}](tg://user?id={telegram_id})"
    
    if cat:
        if wl:
            Ncards = len(wl)
            texto = f"🧺 Wishlist de {nome}:\n{emoji} {Ncards} frutinhas desejadas.\n"

            texto1 = ""
            texto2 = ""
            texto3 = ""

            for carta in wl:
                dados = await exist_card(carta[0], msg)
                qtd = await carta_user(telegram_id, dados[0])

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
            await msg.reply(texto)
        else:
            await msg.reply("⚙️ Oops, parece que você ainda não tem nenhuma carta em sua wishlist.")
    else:
        async with get_cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM wishlists WHERE id_user = %s", (telegram_id,))
            Ncards = await cursor.fetchone()
        
        if Ncards[0] != 0:
            categorias = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="🍇", callback_data=f'wl_ASIAFARM_{telegram_id}'),
                        InlineKeyboardButton(text="🍋", callback_data=f'wl_STREAMBERRY_{telegram_id}')
                    ],
                    [
                        InlineKeyboardButton(text="🫐", callback_data=f'wl_FRUITMIX_{telegram_id}'),
                        InlineKeyboardButton(text="🍏", callback_data=f'wl_MORANGEEK_{telegram_id}')
                    ],
                    [
                        InlineKeyboardButton(text="🍓", callback_data=f'wl_GERAL_{telegram_id}')
                    ]
                ]
            )

            await msg.reply(f"🧺 Wishlist de {nome}:\n✨ {Ncards[0]} frutinhas desejadas.\n\nSelecione uma categoria:", reply_markup=categorias)
        else:
            await msg.reply("⚙️ Oops, parece que você ainda não tem nenhuma carta em sua wishlist.")

# -------------------------------------------
# COMANDO PARA VISUALIZAÇÃO DE EXTRATO (ENTRADAS)

async def berryin(telegram_id, msg):
    berryin = msg.text.split()

    if not msg.reply_to_message:
        if len(berryin) == 1:
            async with get_cursor() as cursor:
                await cursor.execute("SELECT remetente, comando, quantidade, carta, data, DATE_FORMAT(hora, '%%H:%%i') AS hora, cartas, hora AS hr FROM extrato WHERE receptor = %s ORDER BY data DESC, hr DESC", (telegram_id,))
                extrato = await cursor.fetchall()

                if extrato:
                    nome = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
                    nome = f"[{nome}](tg://user?id={telegram_id})"

                    texto = f"🧋 {nome}, aqui está o histórico de transações recebidas dos últimos 7 dias:\n"
                    
                    for remetente, comando, quantidade, carta, data, hora, cartas, _ in extrato:
                        await cursor.execute("SELECT id, username FROM usuarios WHERE telegram_id = %s", (remetente,))
                        remetente = await cursor.fetchone()
                        
                        if comando == "doar":
                            texto += f"\n🥥 Frutinha `{carta}` ({quantidade}x)\n"
                        elif comando == "doars":
                            texto += f"\n🥥 Sementes ({quantidade}x)\n"
                        elif comando == "doarc":
                            texto += f"\n🥥 Colheitas ({quantidade}x)\n"
                        elif comando == "doarinv":
                            texto += f"\n🥥 Cestinha cheia ({quantidade}x)\n{cartas}\n"
                        elif comando.startswith("doarcol"):
                            col = comando.split(",")
                            texto += f"\n🥥 Colheita {col[1]} ({quantidade}x)\n{cartas}\n"
                        elif comando.startswith("doarcat"):
                            cat = comando.split(",")
                            texto += f"\n🥥 Categoria {cat[1]} ({quantidade}x)\n{cartas}\n"
                        elif comando.startswith("doartag"):
                            tag = comando.split(",")
                            texto += f"\n🥥 Tag {tag[1]} ({quantidade}x)\n{cartas}\n"
                        elif comando == "doarw":
                            texto += f"\n🥥 Wishlist ({quantidade}x)\n{cartas}\n"
                        elif comando == "trocar":
                            texto += f"\n🥥 Troca | Frutinha `{carta}` ({quantidade}x)\n"

                        data = data.strftime("%d/%m/%Y")
                        texto += f"⏱️ {data} {hora}\n🧺 Enviado por @{remetente[1]} (ID: `{remetente[0]}`)\n"
                else:
                    await msg.reply("⚙️ Oops, parece que você não recebeu nada nos últimos sete dias.")
                    return
            await msg.reply(texto)
        
        elif len(berryin) == 2:
            if await is_admin(telegram_id, msg):
                async with get_cursor() as cursor:
                    try:
                        user = int(berryin[1])
                        await cursor.execute("SELECT username, telegram_id FROM usuarios WHERE id = %s", (user,))
                        hab = await cursor.fetchone()

                        if hab:
                            await cursor.execute("SELECT remetente, comando, quantidade, carta, data, DATE_FORMAT(hora, '%%H:%%i') AS hora, cartas, hora AS hr FROM extrato WHERE receptor = %s ORDER BY data DESC, hr DESC", (hab[1],))
                            extrato = await cursor.fetchall()
                            user = f"@{hab[0]}"
                        else:
                            await msg.reply("⚙️ Oops, o username procurado não é habitante da Vila Tutti-Frutti.")
                            return
                        
                    except ValueError:
                        username = berryin[1].lstrip('@')
                        await cursor.execute("SELECT telegram_id FROM usuarios WHERE username = %s", (username,))
                        tlid = await cursor.fetchone()

                        if tlid:
                            await cursor.execute("SELECT remetente, comando, quantidade, carta, data, DATE_FORMAT(hora, '%%H:%%i') AS hora, cartas, hora AS hr FROM extrato WHERE receptor = %s ORDER BY data DESC, hr DESC", (tlid[0],))
                            extrato = await cursor.fetchall()
                            user = f"@{username}"
                        else:
                            await msg.reply("⚙️ Oops, o username procurado não é habitante da Vila Tutti-Frutti.")
                            return
                    
                    if extrato:
                        nome = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
                        nome = f"[{nome}](tg://user?id={telegram_id})"

                        texto = f"🧋 {nome}, aqui está o histórico de transações recebidas por {user} nos últimos 7 dias:\n"
                        
                        for remetente, comando, quantidade, carta, data, hora, cartas, _ in extrato:
                            await cursor.execute("SELECT id, username FROM usuarios WHERE telegram_id = %s", (remetente,))
                            remetente = await cursor.fetchone()
                            
                            if comando == "doar":
                                texto += f"\n🥥 Frutinha `{carta}` ({quantidade}x)\n"
                            elif comando == "doars":
                                texto += f"\n🥥 Sementes ({quantidade}x)\n"
                            elif comando == "doarc":
                                texto += f"\n🥥 Colheitas ({quantidade}x)\n"
                            elif comando == "doarinv":
                                texto += f"\n🥥 Cestinha cheia ({quantidade}x)\n{cartas}\n"
                            elif comando.startswith("doarcol"):
                                col = comando.split(",")
                                texto += f"\n🥥 Colheita {col[1]} ({quantidade}x)\n{cartas}\n"
                            elif comando.startswith("doarcat"):
                                cat = comando.split(",")
                                texto += f"\n🥥 Categoria {cat[1]} ({quantidade}x)\n{cartas}\n"
                            elif comando.startswith("doartag"):
                                tag = comando.split(",")
                                texto += f"\n🥥 Tag {tag[1]} ({quantidade}x)\n{cartas}\n"
                            elif comando == "doarw":
                                texto += f"\n🥥 Wishlist ({quantidade}x)\n{cartas}\n"
                            elif comando == "trocar":
                                texto += f"\n🥥 Troca | Frutinha `{carta}` ({quantidade}x)\n"

                            data = data.strftime("%d/%m/%Y")
                            texto += f"⏱️ {data} {hora}\n🧺 Enviado por @{remetente[1]} (ID: `{remetente[0]}`)\n"
                    else:
                        await msg.reply("⚙️ Oops, parece que esse habitante não recebeu nada nos últimos 7 dias.")
                        return
                await msg.reply(texto)
        else:
            await msg.reply("⚙️ Oops, parece que você não está usando o comando corretamente.")
    else:
        if await is_admin(telegram_id, msg):
            async with get_cursor() as cursor:
                await cursor.execute("SELECT remetente, comando, quantidade, carta, data, DATE_FORMAT(hora, '%%H:%%i') AS hora, cartas, hora as hr FROM extrato WHERE receptor = %s ORDER BY data DESC, hr DESC", (msg.reply_to_message.from_user.id,))
                extrato = await cursor.fetchall()

                if extrato:
                    nome = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
                    nome = f"[{nome}](tg://user?id={telegram_id})"

                    texto = f"🧋 {nome}, aqui está o histórico de transações recebidas por @{msg.reply_to_message.from_user.username} nos últimos 7 dias:\n"
                    
                    for remetente, comando, quantidade, carta, data, hora, cartas, _ in extrato:
                        await cursor.execute("SELECT id, username FROM usuarios WHERE telegram_id = %s", (remetente,))
                        remetente = await cursor.fetchone()
                            
                        if comando == "doar":
                            texto += f"\n🥥 Frutinha `{carta}` ({quantidade}x)\n"
                        elif comando == "doars":
                            texto += f"\n🥥 Sementes ({quantidade}x)\n"
                        elif comando == "doarc":
                            texto += f"\n🥥 Colheitas ({quantidade}x)\n"
                        elif comando == "doarinv":
                            texto += f"\n🥥 Cestinha cheia ({quantidade}x)\n{cartas}\n"
                        elif comando.startswith("doarcol"):
                            col = comando.split(",")
                            texto += f"\n🥥 Colheita {col[1]} ({quantidade}x)\n{cartas}\n"
                        elif comando.startswith("doarcat"):
                            cat = comando.split(",")
                            texto += f"\n🥥 Categoria {cat[1]} ({quantidade}x)\n{cartas}\n"
                        elif comando.startswith("doartag"):
                            tag = comando.split(",")
                            texto += f"\n🥥 Tag {tag[1]} ({quantidade}x)\n{cartas}\n"
                        elif comando == "doarw":
                            texto += f"\n🥥 Wishlist ({quantidade}x)\n{cartas}\n"
                        elif comando == "trocar":
                            texto += f"\n🥥 Troca | Frutinha `{carta}` ({quantidade}x)\n"

                        data = data.strftime("%d/%m/%Y")
                        texto += f"⏱️ {data} {hora}\n🧺 Enviado por @{remetente[1]} (ID: `{remetente[0]}`)\n"
                else:
                    await msg.reply("⚙️ Oops, parece que esse habitante não recebeu nada nos últimos 7 dias.")
                    return
            await msg.reply(texto)

# -------------------------------------------
# COMANDO PARA VISUALIZAÇÃO DE EXTRATO (SAÍDAS)

async def berryout(telegram_id, msg):
    berryout = msg.text.split()

    if not msg.reply_to_message:
        if len(berryout) == 1:
            async with get_cursor() as cursor:
                await cursor.execute("SELECT receptor, comando, quantidade, carta, data, DATE_FORMAT(hora, '%%H:%%i') AS hora, cartas, hora AS hr FROM extrato WHERE remetente = %s ORDER BY data DESC, hr DESC", (telegram_id,))
                extrato = await cursor.fetchall()

                if extrato:
                    nome = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
                    nome = f"[{nome}](tg://user?id={telegram_id})"

                    texto = f"🧋 {nome}, aqui está o histórico de transações enviadas dos últimos 7 dias:\n"
                    
                    for receptor, comando, quantidade, carta, data, hora, cartas, _ in extrato:
                        await cursor.execute("SELECT id, username FROM usuarios WHERE telegram_id = %s", (receptor,))
                        receptor = await cursor.fetchone()
                        
                        if comando == "doar":
                            texto += f"\n🥥 Frutinha `{carta}` ({quantidade}x)\n"
                        elif comando == "doars":
                            texto += f"\n🥥 Sementes ({quantidade}x)\n"
                        elif comando == "doarc":
                            texto += f"\n🥥 Colheitas ({quantidade}x)\n"
                        elif comando == "doarinv":
                            texto += f"\n🥥 Cestinha cheia ({quantidade}x)\n{cartas}\n"
                        elif comando.startswith("doarcol"):
                            col = comando.split(",")
                            texto += f"\n🥥 Colheita {col[1]} ({quantidade}x)\n{cartas}\n"
                        elif comando.startswith("doarcat"):
                            cat = comando.split(",")
                            texto += f"\n🥥 Categoria {cat[1]} ({quantidade}x)\n{cartas}\n"
                        elif comando.startswith("doartag"):
                            tag = comando.split(",")
                            texto += f"\n🥥 Tag {tag[1]} ({quantidade}x)\n{cartas}\n"
                        elif comando == "doarw":
                            texto += f"\n🥥 Wishlist ({quantidade}x)\n{cartas}\n"
                        elif comando == "trocar":
                            texto += f"\n🥥 Troca | Frutinha `{carta}` ({quantidade}x)\n"

                        data = data.strftime("%d/%m/%Y")
                        texto += f"⏱️ {data} {hora}\n🧺 Enviado para @{receptor[1]} (ID: `{receptor[0]}`)\n"
                else:
                    await msg.reply("⚙️ Oops, parece que você não enviou nada nos últimos sete dias.")
                    return
            await msg.reply(texto)
        
        elif len(berryout) == 2:
            if await is_admin(telegram_id, msg):
                async with get_cursor() as cursor:
                    try:
                        user = int(berryout[1])
                        await cursor.execute("SELECT username, telegram_id FROM usuarios WHERE id = %s", (user,))
                        hab = await cursor.fetchone()

                        if hab:
                            await cursor.execute("SELECT receptor, comando, quantidade, carta, data, DATE_FORMAT(hora, '%%H:%%i') AS hora, cartas, hora AS hr FROM extrato WHERE remetente = %s ORDER BY data DESC, hr DESC", (hab[1],))
                            extrato = await cursor.fetchall()
                            user = f"@{hab[0]}"
                        else:
                            await msg.reply("⚙️ Oops, o username procurado não é habitante da Vila Tutti-Frutti.")
                            return
                        
                    except ValueError:
                        username = berryout[1].lstrip('@')
                        await cursor.execute("SELECT telegram_id FROM usuarios WHERE username = %s", (username,))
                        tlid = await cursor.fetchone()

                        if tlid:
                            await cursor.execute("SELECT receptor, comando, quantidade, carta, data, DATE_FORMAT(hora, '%%H:%%i') AS hora, cartas, hora AS hr FROM extrato WHERE remetente = %s ORDER BY data DESC, hr DESC", (tlid[0],))
                            extrato = await cursor.fetchall()
                            user = f"@{username}"
                        else:
                            await msg.reply("⚙️ Oops, o username procurado não é habitante da Vila Tutti-Frutti.")
                            return
                    
                    if extrato:
                        nome = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
                        nome = f"[{nome}](tg://user?id={telegram_id})"

                        texto = f"🧋 {nome}, aqui está o histórico de transações enviadas por {user} nos últimos 7 dias:\n"
                        
                        for receptor, comando, quantidade, carta, data, hora, cartas, _ in extrato:
                            await cursor.execute("SELECT id, username FROM usuarios WHERE telegram_id = %s", (receptor,))
                            receptor = await cursor.fetchone()
                            
                            if comando == "doar":
                                texto += f"\n🥥 Frutinha `{carta}` ({quantidade}x)\n"
                            elif comando == "doars":
                                texto += f"\n🥥 Sementes ({quantidade}x)\n"
                            elif comando == "doarc":
                                texto += f"\n🥥 Colheitas ({quantidade}x)\n"
                            elif comando == "doarinv":
                                texto += f"\n🥥 Cestinha cheia ({quantidade}x)\n{cartas}\n"
                            elif comando.startswith("doarcol"):
                                col = comando.split(",")
                                texto += f"\n🥥 Colheita {col[1]} ({quantidade}x)\n{cartas}\n"
                            elif comando.startswith("doarcat"):
                                cat = comando.split(",")
                                texto += f"\n🥥 Categoria {cat[1]} ({quantidade}x)\n{cartas}\n"
                            elif comando.startswith("doartag"):
                                tag = comando.split(",")
                                texto += f"\n🥥 Tag {tag[1]} ({quantidade}x)\n{cartas}\n"
                            elif comando == "doarw":
                                texto += f"\n🥥 Wishlist ({quantidade}x)\n{cartas}\n"
                            elif comando == "trocar":
                                texto += f"\n🥥 Troca | Frutinha `{carta}` ({quantidade}x)\n"

                            data = data.strftime("%d/%m/%Y")
                            texto += f"⏱️ {data} {hora}\n🧺 Enviado para @{receptor[1]} (ID: `{receptor[0]}`)\n"
                    else:
                        await msg.reply("⚙️ Oops, parece que esse habitante não enviou nada nos últimos 7 dias.")
                        return
                await msg.reply(texto)
        else:
            await msg.reply("⚙️ Oops, parece que você não está usando o comando corretamente.")
    else:
        if await is_admin(telegram_id, msg):
            async with get_cursor() as cursor:
                await cursor.execute("SELECT receptor, comando, quantidade, carta, data, DATE_FORMAT(hora, '%%H:%%i') AS hora, cartas, hora AS hr FROM extrato WHERE remetente = %s ORDER BY data DESC, hr DESC", (msg.reply_to_message.from_user.id,))
                extrato = await cursor.fetchall()

                if extrato:
                    nome = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
                    nome = f"[{nome}](tg://user?id={telegram_id})"

                    texto = f"🧋 {nome}, aqui está o histórico de transações enviadas por @{msg.reply_to_message.from_user.username} nos últimos 7 dias:\n"
                    
                    for receptor, comando, quantidade, carta, data, hora, cartas, _ in extrato:
                        await cursor.execute("SELECT id, username FROM usuarios WHERE telegram_id = %s", (receptor,))
                        receptor = await cursor.fetchone()
                            
                        if comando == "doar":
                            texto += f"\n🥥 Frutinha `{carta}` ({quantidade}x)\n"
                        elif comando == "doars":
                            texto += f"\n🥥 Sementes ({quantidade}x)\n"
                        elif comando == "doarc":
                            texto += f"\n🥥 Colheitas ({quantidade}x)\n"
                        elif comando == "doarinv":
                            texto += f"\n🥥 Cestinha cheia ({quantidade}x)\n{cartas}\n"
                        elif comando.startswith("doarcol"):
                            col = comando.split(",")
                            texto += f"\n🥥 Colheita {col[1]} ({quantidade}x)\n{cartas}\n"
                        elif comando.startswith("doarcat"):
                            cat = comando.split(",")
                            texto += f"\n🥥 Categoria {cat[1]} ({quantidade}x)\n{cartas}\n"
                        elif comando.startswith("doartag"):
                            tag = comando.split(",")
                            texto += f"\n🥥 Tag {tag[1]} ({quantidade}x)\n{cartas}\n"
                        elif comando == "doarw":
                            texto += f"\n🥥 Wishlist ({quantidade}x)\n{cartas}\n"
                        elif comando == "trocar":
                            texto += f"\n🥥 Troca | Frutinha `{carta}` ({quantidade}x)\n"

                        data = data.strftime("%d/%m/%Y")
                        texto += f"⏱️ {data} {hora}\n🧺 Enviado por @{receptor[1]} (ID: `{receptor[0]}`)\n"
                else:
                    await msg.reply("⚙️ Oops, parece que esse habitante não enviou nada nos últimos 7 dias.")
                    return
            await msg.reply(texto)

# -------------------------------------------
# COMANDO PARA INTERLIGAR CONTAS

async def laranja(telegram_id, msg, bot):
    if not msg.reply_to_message:
        entrada = msg.text.split()
        if len(entrada) != 2:
            await msg.reply("⚙️ Oops, parece que o comando não está correto. Exemplo: /laranja ID.")
            return
        
        async with get_cursor() as cursor:
            try:
                user = int(entrada[1])
                await cursor.execute("SELECT telegram_id FROM usuarios WHERE id = %s", (user,))
                tlid = await cursor.fetchone()
            except ValueError:
                user = entrada[1].lstrip('@')
                await cursor.execute("SELECT telegram_id FROM usuarios WHERE username = %s", (user,))
                tlid = await cursor.fetchone()
            
            if tlid:
                await cursor.execute("SELECT COUNT(*) FROM laranjas WHERE laranja = %s", (tlid[0],))
                islaranja = await cursor.fetchone()

                if islaranja[0] == 0:
                    await cursor.execute("SELECT COUNT(*) FROM laranjas WHERE matriz = %s", (tlid[0],))
                    ismatriz = await cursor.fetchone()

                    if ismatriz[0] == 0:
                        await cursor.execute("SELECT COUNT(*) FROM laranjas WHERE laranja = %s", (telegram_id,))
                        islaranja = await cursor.fetchone()

                        if islaranja[0] == 0:
                            await cursor.execute("SELECT COUNT(*) FROM laranjas WHERE matriz = %s", (telegram_id,))
                            qtd = await cursor.fetchone()

                            await cursor.execute("SELECT vip FROM usuarios WHERE telegram_id = %s", (telegram_id,))
                            isvip = await cursor.fetchone()
                        else:
                            await msg.reply("⚙️ Oops, parece que o seu perfil já é laranja de alguém.")
                            return
                    else:
                        await msg.reply("⚙️ Oops, parece que esse usuário tem laranjas linkadas. Laranjas não podem linkar laranjas.")
                        return
                else:
                    await msg.reply("⚙️ Oops, parece que esse usuário já é laranja de algum habitante.")
                    return
            else:
                await msg.reply("⚙️ Oops, parece que essa pessoa não é habitante da Vila Tutti-Frutti.")
                return
    else:
        async with get_cursor() as cursor:
            await cursor.execute("SELECT telegram_id FROM usuarios WHERE telegram_id = %s", (msg.reply_to_message.from_user.id,))
            tlid = await cursor.fetchone()
            
            if tlid:
                await cursor.execute("SELECT COUNT(*) FROM laranjas WHERE laranja = %s", (tlid[0],))
                islaranja = await cursor.fetchone()

                if islaranja[0] == 0:
                    await cursor.execute("SELECT COUNT(*) FROM laranjas WHERE matriz = %s", (tlid[0],))
                    ismatriz = await cursor.fetchone()

                    if ismatriz[0] == 0:
                        await cursor.execute("SELECT COUNT(*) FROM laranjas WHERE laranja = %s", (telegram_id,))
                        islaranja = await cursor.fetchone()

                        if islaranja[0] == 0:
                            await cursor.execute("SELECT COUNT(*) FROM laranjas WHERE matriz = %s", (telegram_id,))
                            qtd = await cursor.fetchone()

                            await cursor.execute("SELECT vip FROM usuarios WHERE telegram_id = %s", (telegram_id,))
                            isvip = await cursor.fetchone()
                        else:
                            await msg.reply("⚙️ Oops, parece que o seu perfil já é laranja de alguém.")
                            return
                    else:
                        await msg.reply("⚙️ Oops, parece que esse usuário tem laranjas linkadas. Laranjas não podem linkar laranjas.")
                        return
                else:
                    await msg.reply("⚙️ Oops, parece que esse usuário já é laranja de algum habitante.")
                    return
            else:
                await msg.reply("⚙️ Oops, parece que essa pessoa não é habitante da Vila Tutti-Frutti.")
                return
            
    if isvip[0] == 1:
        limite = 25
    else:
        limite = 15

    if qtd[0] > limite:
        await msg.reply(f"⚙️ Oops, você já atingiu o limite de {limite} laranjas.")
        return
    else:
        opts = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="CONECTAR 🍏", callback_data=f"linkar_{telegram_id}"),
                InlineKeyboardButton(text="CANCELAR 🍎", callback_data=f"cancelar")
            ]
        ])
        await bot.send_message(tlid[0], f"🍃 Tem certeza que deseja conectar sua conta com @{msg.from_user.username}?", reply_markup=opts)

# -------------------------------------------
# COMANDO PARA COLETAR LARANJAS

async def recolher(telegram_id, msg):
    async with get_cursor() as cursor:
        await cursor.execute("SELECT laranja FROM laranjas WHERE matriz = %s", (telegram_id,))
        laranjas = await cursor.fetchall()

        sementes = 0
        giros = 0
        if laranjas:
            for laranja in laranjas:
                await cursor.execute("SELECT sementes, giros FROM usuarios WHERE telegram_id = %s", (laranja,))
                coleta = await cursor.fetchone()

                await cursor.execute("UPDATE usuarios SET sementes = sementes + %s, giros = giros + %s WHERE telegram_id = %s", (coleta[0], coleta[1], telegram_id,))
                sementes += coleta[0]
                giros += coleta[1]

                await cursor.execute("UPDATE usuarios SET sementes = 0, giros = 0 WHERE telegram_id = %s", (laranja,))
            
            if sementes == 0 and giros == 0:
                await msg.reply("⚙️ Oops, suas laranjas não tem nada para recolher.")
                return
            else:
                texto = "🌳 Ao recolher de suas laranjas, você conseguiu:\n"

                if giros > 0:
                    texto += f"\n🧃 {giros} giros"
                
                if sementes > 0:
                    texto += f"\n🌾 {sementes} sementes"

                await msg.reply(texto)
        else:
            await msg.reply("⚙️ Oops, você não tem nenhuma laranja para recolher.")
            return

# -------------------------------------------
# COMANDO PARA DESLINKAR CONTAS

async def desvinc(telegram_id, msg):
    if not msg.reply_to_message:
        entrada = msg.text.split()
        if len(entrada) != 2:
            await msg.reply("⚙️ Oops, parece que o comando não está correto. Exemplo: /desvincular ID.")
            return
        
        async with get_cursor() as cursor:
            try:
                user = int(entrada[1])
                await cursor.execute("SELECT telegram_id FROM usuarios WHERE id = %s", (user,))
                tlid = await cursor.fetchone()
            except ValueError:
                user = entrada[1].lstrip('@')
                await cursor.execute("SELECT telegram_id FROM usuarios WHERE username = %s", (user,))
                tlid = await cursor.fetchone()
            
            if tlid:
                await cursor.execute("SELECT COUNT(*) FROM laranjas WHERE laranja = %s AND matriz = %s", (tlid[0], telegram_id,))
                laranja = await cursor.fetchone()

                if laranja[0] == 0:
                    await msg.reply("⚙️ Oops, você não está linkado a esse habitante.")
                    return
                else:
                    await cursor.execute("DELETE FROM laranjas WHERE laranja = %s AND matriz = %s", (tlid[0], telegram_id,))
            else:
                await msg.reply("⚙️ Oops, parece que essa pessoa não é habitante da Vila Tutti-Frutti.")
                return
    else:
        async with get_cursor() as cursor:
            await cursor.execute("SELECT telegram_id FROM usuarios WHERE telegram_id = %s", (msg.reply_to_message.from_user.id,))
            tlid = await cursor.fetchone()
            
            if tlid:
                await cursor.execute("SELECT COUNT(*) FROM laranjas WHERE laranja = %s AND matriz = %s", (tlid[0], telegram_id,))
                laranja = await cursor.fetchone()

                if laranja[0] == 0:
                    await msg.reply("⚙️ Oops, você não está linkado a esse habitante.")
                    return
                else:
                    await cursor.execute("DELETE FROM laranjas WHERE laranja = %s AND matriz = %s", (tlid[0], telegram_id,))
            else:
                await msg.reply("⚙️ Oops, parece que essa pessoa não é habitante da Vila Tutti-Frutti.")
                return
    await msg.reply("Conta desvinculada com sucesso! 🐛")

# -------------------------------------------
# COMANDO PARA VISUALIZAR LARANJAS

async def laranjas(telegram_id, msg):
    async with get_cursor() as cursor:
        await cursor.execute("SELECT laranja FROM laranjas WHERE matriz = %s", (telegram_id,))
        laranjas = await cursor.fetchall()

        if laranjas:
            Nlaranjas = len(laranjas)
            if Nlaranjas > 1:
                texto = f"🍊 Você possui {len(laranjas)} laranjas:\n"
            else:
                texto = f"🍊 Você possui uma laranja:\n"

            for laranja in laranjas:
                await cursor.execute("SELECT username, sementes, giros FROM usuarios WHERE telegram_id = %s", (laranja,))
                dados = await cursor.fetchone()

                texto += f"\n🐛 @{dados[0]}\n🧃 Giros: {dados[1]}\n🌾 Sementes: {dados[2]}\n"
            await msg.reply(texto)
        else:
            await msg.reply("⚙️ Oops, parece que você ainda não tem nenhuma laranja.")
            return

# -------------------------------------------
# COMANDO PARA DEFINIR MÍDIA ESPECIAL

async def midia(telegram_id, msg, bot):
    if not msg.reply_to_message:
        await msg.reply("⚙️ Oops, parece que você não marcou nenhum vídeo ou foto.")
    else:
        if not msg.reply_to_message.photo and not msg.reply_to_message.video:
            await msg.reply("⚙️ Oops, parece que a mensagem marcada não é uma foto ou um vídeo.")
            return
    
        entrada = msg.text.split()
        if len(entrada) < 2:
            await msg.reply("⚙️ Oops, parece que você não informou o card. Exemplo: /midia ID.")
            return
        elif len(entrada) > 2:
            await msg.reply("⚙️ Oops, você só pode colocar mídia em um card por vez. Exemplo: /midia ID.")
            return
        else:
            try:
                card = int(entrada[1])
                exists = await exist_card(card, msg)
                
                if exists:
                    if msg.reply_to_message.video:
                        midia = msg.reply_to_message.video
                        tamanho = midia.file_size / (1024 * 1024)
                        duração = midia.duration
                        largura = midia.width
                        altura = midia.height
                        proporção = round(largura / altura, 2)

                        if tamanho >= 6:
                            await msg.reply("🍎 Seu vídeo excede o limite de 5MB, você pode tentar comprimir e enviar novamente!")
                            return
                        elif duração > 30:
                            await msg.reply(f"🍎 Seu vídeo para a frutinha `{card}` excede 30 segundos, tente novamente com um vídeo mais curto!")
                            return
                        elif midia.mime_type != "video/mp4":
                            await msg.reply(f"🍎 Seu vídeo não está no formato mp4, tente converter e enviar novamente!")
                            return
                        elif proporção not in [1.0, 0.75]:
                            await msg.reply(f"🍎 Seu vídeo está no formato incorreto, confira se o tamanho é 1:1 ou 3:4 e envie novamente!")
                            return
                        else:
                            tipo = "video"
                    else:
                        midia = msg.reply_to_message.photo[-1]
                        tamanho = midia.file_size / (1024 * 1024)
                        largura = midia.width
                        altura = midia.height
                        proporção = round(largura / altura, 2)

                        if tamanho >= 6:
                            await msg.reply("🍎 Sua foto excede o limite de 5MB, você pode tentar comprimir e enviar novamente!")
                            return
                        elif proporção not in [1.0, 0.75]:
                            await msg.reply(f"🍎 Sua foto está no formato incorreto, confira se o tamanho é 1:1 ou 3:4 e envie novamente!")
                            return
                        else:
                            tipo = "foto"

                    async with get_cursor() as cursor:
                        await cursor.execute("SELECT quantidade FROM inventario WHERE id_user = %s AND id_carta = %s", (telegram_id, card,))
                        contagem = await cursor.fetchone()

                        if contagem[0] < 100:
                            await msg.reply(f"🍎 Oops, parece que você ainda não tem 100 unidades da frutinha `{card}`.")
                            return
                        else:
                            await msg.reply("🍏 Mídia enviada para aprovação.")
                            GRUPO = os.getenv("MIDIAS")
                            file_id = midia.file_id

                            opcoes = InlineKeyboardMarkup(inline_keyboard=[
                                [
                                    InlineKeyboardButton(text="APROVAR 🍏", callback_data=f"midia_apv_{telegram_id}_{card}"),
                                    InlineKeyboardButton(text="RECUSAR 🍎", callback_data=f"midia_rec_{telegram_id}_{card}")
                                ]
                            ])
                                    
                            texto = f"🎥 @{msg.from_user.username} enviou uma mídia para a frutinha `{card}`. {exists[1]}."
                                
                            if tipo == "video":
                                await bot.send_video(chat_id=GRUPO, video=file_id, caption=texto, reply_markup=opcoes)
                            else:
                                await bot.send_photo(chat_id=GRUPO, photo=file_id, caption=texto, reply_markup=opcoes)
            except ValueError:
                await msg.reply("⚙️ Oops, só é possível inserir mídia com base no ID do card desejado.")
                return
            
# -------------------------------------------
# CONSTRUTOR DE PERFIL

async def constructor_preset(telegram_id, action, source):
    largura_fotos = 264
    altura_fotos = 352
    y_fotos = 730
    inicio_card1 = 580
    inicio_card2 = 875
    inicio_card3 = 1170

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    async with get_cursor() as cursor:
        await cursor.execute("SELECT presets FROM perfis WHERE id = %s", (telegram_id,))
        presets = await cursor.fetchone()

        if not presets or not presets[0]:
            fundo = Image.new("RGBA", (1617, 1200), (0, 0, 0, 0))
        else:
            response = requests.get(presets[0], headers=headers)
            imgfundo = BytesIO(response.content)
            fundo = Image.open(imgfundo).convert("RGBA")

        match action:
            case "card1":
                await cursor.execute("SELECT imagem FROM cartas WHERE id = %s", (source,))
                img1 = await cursor.fetchone()
                response = requests.get(img1[0], headers=headers)
                imgc1 = BytesIO(response.content)
                card1img = Image.open(imgc1).resize((largura_fotos, altura_fotos))
                fundo.paste(card1img, (inicio_card1, y_fotos))
            case "card2":
                await cursor.execute("SELECT imagem FROM cartas WHERE id = %s", (source,))
                img2 = await cursor.fetchone()
                response = requests.get(img2[0], headers=headers)
                imgc2 = BytesIO(response.content)
                card2img = Image.open(imgc2).resize((largura_fotos, altura_fotos))
                fundo.paste(card2img, (inicio_card2, y_fotos))
            case "card3":
                await cursor.execute("SELECT imagem FROM cartas WHERE id = %s", (source,))
                img3 = await cursor.fetchone()
                largura_fotos = 264
                response = requests.get(img3[0], headers=headers)
                imgc3 = BytesIO(response.content)
                card3img = Image.open(imgc3).resize((largura_fotos, altura_fotos))
                fundo.paste(card3img, (inicio_card3, y_fotos))

        buffered = BytesIO()
        fundo.save(buffered, format="PNG")
        buffered.seek(0)

        USER = os.getenv("BUNNYUSER")
        SENHA = os.getenv("BUNNYSENHA")

        try:
            ftp = FTP()
            ftp.connect('br.storage.bunnycdn.com', 21)
            ftp.login(user=USER, passwd=SENHA)
            ftp.set_pasv(True)
            
            nome = f"{telegram_id}_perfil.png"
            ftp.storbinary(f"STOR midias/perfis/{nome}", buffered)
                            
            upload = f"midias/perfis/{nome}"

            await cursor.execute("UPDATE perfis SET presets = %s WHERE id = %s", (upload, telegram_id,))
            return True
        except Exception as e:
            print(f"ERRO: {e}")
            return False
        finally:
            buffered.close()
            ftp.quit()

# -------------------------------------------
# COMANDO PARA VISUALIZAR PERFIL

async def perfil(telegram_id, msg, bot):
    base = Image.open("assets\\template_perfil.png").convert("RGBA")

    # IMAGEM DO PERFIL TELEGRAM
    fotos = await bot.get_user_profile_photos(msg.from_user.id, limit=1)

    perfil_img = None
    if fotos.total_count:
        file = await bot.get_file(fotos.photos[0][-1].file_id)
        foto_bytes = await bot.download_file(file.file_path)
        perfil_img = Image.open(foto_bytes).convert("RGBA")
        perfil_img = perfil_img.resize((325, 325))

    async with get_cursor() as cursor:
        await cursor.execute("SELECT presets FROM perfis WHERE id = %s", (telegram_id,))
        presets = await cursor.fetchone()

        if not presets or not presets[0]:
            fundo = Image.new("RGBA", (1617, 1200), (0, 0, 0, 0))
        else:
            USER = os.getenv("BUNNYUSER")
            SENHA = os.getenv("BUNNYSENHA")

            ftp = FTP()
            ftp.connect('br.storage.bunnycdn.com', 21)
            ftp.login(user=USER, passwd=SENHA)
            ftp.set_pasv(True)

            imgfundo = BytesIO()
            ftp.retrbinary(f"RETR {presets[0]}", imgfundo.write)
            imgfundo.seek(0)
            fundo = Image.open(imgfundo).convert("RGBA")
        
        if perfil_img:
            fundo.paste(perfil_img, (187, 218))

        await cursor.execute("SELECT giros, sementes, id, parceiro FROM usuarios WHERE telegram_id = %s", (telegram_id,))
        dados = await cursor.fetchone()
        await cursor.execute("SELECT SUM(quantidade) FROM inventario WHERE id_user = %s", (telegram_id,))
        Ncards = await cursor.fetchone()
        await cursor.execute("SELECT card_fav, sub_fav, bio FROM perfis WHERE id = %s", (telegram_id,))
        esp_perfil = await cursor.fetchone()

        if dados[3]:
            await cursor.execute("SELECT telegram_id FROM usuarios WHERE username = %s", (dados[3],))
            ptlid = await cursor.fetchone()

            partner = await bot.get_chat(ptlid[0])
            texto_partner = f"💌 {partner.first_name}, @{dados[3]}\n\n"
        else:
            texto_partner = "\n"
        
        if not esp_perfil:
            card_fav = None
            sub_fav = None
            bio = None

            texto_bio = ""
            texto_fav = ""

        else:
            card_fav, sub_fav, bio = esp_perfil

            if bio:
                texto_bio = f'"_{bio}_"\n\n'
            else:
                texto_bio = "\n"
            
            if card_fav:
                await cursor.execute("SELECT nome, raridade, subcategoria FROM cartas WHERE id = %s", (card_fav,))
                carta = await cursor.fetchone()

                texto_fav = f"{raridade_emojis.get(carta[1], '❓')} `{card_fav}`. {carta[0]} — {carta[2]}\n"
            else:
                texto_fav = "\n"

    if not Ncards[0]:
        Ncards = 0
    else:
        Ncards = Ncards[0]
    
    img = Image.alpha_composite(fundo, base)

    escrita = ImageDraw.Draw(img)
    fonte_nome = ImageFont.truetype("assets\\fonte_perfil.otf", size=55)
    fonte_dados = ImageFont.truetype("assets\\fonte_perfil.otf", size=50)

    nome = msg.from_user.first_name
    nome = nome[:13]
    nomep = nome.upper()

    # CENTRALIZAÇÃO DO NOME
    bboxn = escrita.textbbox((0, 0), nomep, font=fonte_nome)
    largura_texto = bboxn[2] - bboxn[0]

    inicio_nome = 196
    largura_nome = 310

    x_nome = inicio_nome + (largura_nome - largura_texto) // 2

    # CENTRALIZAÇÃO DOS DADOS
    bboxg = escrita.textbbox((0, 0), str(dados[0]), font=fonte_dados)
    largura_giros = bboxg[2] - bboxg[0]

    bboxc = escrita.textbbox((0, 0), str(Ncards), font=fonte_dados)
    largura_cards = bboxc[2] - bboxc[0]

    bboxs = escrita.textbbox((0, 0), str(dados[1]), font=fonte_dados)
    largura_sementes = bboxs[2] - bboxs[0]

    inicio_dados = 265
    largura_dados = 180

    x_giros = inicio_dados + (largura_dados - largura_giros) // 2
    x_cards = inicio_dados + (largura_dados - largura_cards) // 2
    x_sementes = inicio_dados + (largura_dados - largura_sementes) // 2

    largura_favs = 290
    if sub_fav:
        bboxsub = escrita.textbbox((0, 0), sub_fav.upper(), font=fonte_dados)
        largura_sub = bboxsub[2] - bboxsub[0]

        inicio_sub = 1105
        x_sub = inicio_sub + (largura_favs - largura_sub) // 2

        escrita.text((x_sub, 307), sub_fav.upper(), font=fonte_dados, fill="#594126")
    if card_fav:
        bboxf = escrita.textbbox((0, 0), carta[0].upper(), font=fonte_dados)
        largura_fav = bboxf[2] - bboxf[0]

        inicio_fav = 683
        x_fav = inicio_fav + (largura_favs - largura_fav) // 2

        escrita.text((x_fav, 307), carta[0].upper(), font=fonte_dados, fill="#594126")

    # ESCRITA E POSICIONAMENTO
    escrita.text((x_nome, 620), nomep, font=fonte_nome, fill="#594126")
    escrita.text((x_giros, 785), str(dados[0]), font=fonte_dados, fill="#594126")
    escrita.text((x_cards, 905), str(Ncards), font=fonte_dados, fill="#594126")
    escrita.text((x_sementes, 1020), str(dados[1]), font=fonte_dados, fill="#594126")

    # SALVA PERFIL
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    perfil = BufferedInputFile(buffer.read(), filename="perfil.png")

    
    legenda = f"🍓 `{dados[2]}`. *{nome}*\n{texto_bio}{texto_fav}{texto_partner}🌾 *Colheitas* - {dados[0]} restantes\n🍒 *Frutas* - {Ncards}\n🌱 *Sementes* - {dados[1]}\n\n_Use /receita para aprender como customizar seu perfil._"

    await bot.send_photo(
        chat_id=msg.chat.id,
        photo=f"{perfil}?nocache={int(time.time())}",
        caption=legenda,
        reply_to_message_id=msg.message_id
    )

# -------------------------------------------
# PASSOS PARA CUSTOMIZAR PERFIL

async def receita(msg, state):
    await msg.reply("🍰 Prepare seu perfil seguindo nossa receita:\n\n/setbio — Escolha os ingredientes da sua bio!\n\n/setfav ID — Escolha sua frutinha preferida!\n\n/setcol Nome — Escolha sua colheita favorita!\n\n/card1 ID,\n/card2 ID,\n/card3 ID — Customize seu perfil com as frutinhas de sua preferência, seguindo a ordem!\n\n🏹 Não se esqueça: você pode se casar com outro usuário, e o status aparecerá no perfil.")
    await state.set_state(Receita.settings)

@users.message(StateFilter(Receita.settings)) 
async def receita_process(msg, state):
    entrada = msg.text.split(' ', 1)
    
    if len(entrada) < 2:
        await msg.reply("⚙️ Oops, parece que você esqueceu de informar alguma coisa. Tente novamente!")
        await state.clear()
        return
    else:
        comando = entrada[0]

        async with get_cursor() as cursor:
            await cursor.execute("SELECT id FROM perfis WHERE id = %s", (msg.from_user.id,))
            result = await cursor.fetchone()

            match comando:
                case "/setbio":
                    texto = entrada[1]
                    if result:
                        await cursor.execute("UPDATE perfis SET bio = %s WHERE id = %s", (texto, msg.from_user.id,))
                    else:
                        await cursor.execute("INSERT INTO perfis (id, bio) VALUES (%s, %s)", (msg.from_user.id, texto,))
                    await msg.reply("🔖 Sua bio foi atualizada com sucesso!")
                    await state.clear()
                case "/setfav":
                    try:
                        card = int(entrada[1])
                        exists = await exist_card(card, msg)

                        if exists and result:
                            await cursor.execute("UPDATE perfis SET card_fav = %s WHERE id = %s", (card, msg.from_user.id,))
                            await msg.reply(f"🔖 `{card}`. {exists[1]} foi definida como sua frutinha preferida!")
                            await state.clear()
                        elif exists:
                            await cursor.execute("INSERT INTO perfis (id, card_fav) VALUES (%s, %s)", (msg.from_user.id, card,))
                            await msg.reply(f"🔖 `{card}`. {exists[1]} foi definida como sua frutinha preferida!")
                            await state.clear()
                        else:
                            await state.clear()
                            return
                    except ValueError:
                        await msg.reply("⚙️ Oops, você só pode favoritar um card com base no ID. Tente novamente!")
                        await state.clear()
                        return
                case "/setcol":
                    sub = entrada[1]
                    exists = await exist_sub(sub, msg)

                    if exists:
                        sub = exists[1]

                        if result:
                            await cursor.execute("UPDATE perfis SET sub_fav = %s WHERE id = %s", (sub, msg.from_user.id,))
                        else:
                            await cursor.execute("INSERT INTO perfis (id, sub_fav) VALUES (%s, %s)", (msg.from_user.id, sub,))
                        await state.clear()
                        await msg.reply(f"🔖 A colheita {sub} foi definida como sua favorita!")
                    else:
                        await state.clear()
                        return
                case "/card1":
                    try:
                        card = int(entrada[1])
                        exists = await exist_card(card, msg)

                        if exists and result:
                            await cursor.execute("UPDATE perfis SET card1 = %s WHERE id = %s", (card, msg.from_user.id,))
                            update = await constructor_preset(msg.from_user.id, "card1", card)

                            if update:
                                await msg.reply(f"🔖 Primeiro card atualizado para `{card}`.")
                                await state.clear()
                            else:
                                await msg.reply(f"⚙️ Oops, houve algum erro durante a atualização do seu perfil.")
                                await state.clear()
                        elif exists:
                            await cursor.execute("INSERT INTO perfis (id, card1) VALUES (%s, %s)", (msg.from_user.id, card,))
                            update = await constructor_preset(msg.from_user.id, "card1", card)

                            if update:
                                await msg.reply(f"🔖 Primeiro card atualizado para `{card}`.")
                                await state.clear()
                            else:
                                await msg.reply(f"⚙️ Oops, houve algum erro durante a atualização do seu perfil.")
                                await state.clear()
                        else:
                            await state.clear()
                            return
                    except ValueError:
                        await msg.reply("⚙️ Oops, você só pode escolher cards com base no ID. Tente novamente!")
                        await state.clear()
                        return
                case "/card2":
                    try:
                        card = int(entrada[1])
                        exists = await exist_card(card, msg)

                        if exists and result:
                            await cursor.execute("UPDATE perfis SET card2 = %s WHERE id = %s", (card, msg.from_user.id,))
                            update = await constructor_preset(msg.from_user.id, "card2", card)

                            if update:
                                await msg.reply(f"🔖 Segundo card atualizado para `{card}`.")
                                await state.clear()
                            else:
                                await msg.reply(f"⚙️ Oops, houve algum erro durante a atualização do seu perfil.")
                                await state.clear()
                        elif exists:
                            await cursor.execute("INSERT INTO perfis (id, card2) VALUES (%s, %s)", (msg.from_user.id, card,))
                            update = await constructor_preset(msg.from_user.id, "card2", card)

                            if update:
                                await msg.reply(f"🔖 Segundo card atualizado para `{card}`.")
                                await state.clear()
                            else:
                                await msg.reply(f"⚙️ Oops, houve algum erro durante a atualização do seu perfil.")
                                await state.clear()
                        else:
                            await state.clear()
                            return
                    except ValueError:
                        await msg.reply("⚙️ Oops, você só pode escolher cards com base no ID. Tente novamente!")
                        await state.clear()
                        return
                case "/card3":
                    try:
                        card = int(entrada[1])
                        exists = await exist_card(card, msg)

                        if exists and result:
                            await cursor.execute("UPDATE perfis SET card3 = %s WHERE id = %s", (card, msg.from_user.id,))
                            update = await constructor_preset(msg.from_user.id, "card3", card)

                            if update:
                                await msg.reply(f"🔖 Terceiro card atualizado para `{card}`.")
                                await state.clear()
                            else:
                                await msg.reply(f"⚙️ Oops, houve algum erro durante a atualização do seu perfil.")
                                await state.clear()
                        elif exists:
                            await cursor.execute("INSERT INTO perfis (id, card3) VALUES (%s, %s)", (msg.from_user.id, card,))
                            update = await constructor_preset(msg.from_user.id, "card3", card)

                            if update:
                                await msg.reply(f"🔖 Terceiro card atualizado para `{card}`.")
                                await state.clear()
                            else:
                                await msg.reply(f"⚙️ Oops, houve algum erro durante a atualização do seu perfil.")
                                await state.clear()
                        else:
                            await state.clear()
                            return
                    except ValueError:
                        await msg.reply("⚙️ Oops, você só pode escolher cards com base no ID. Tente novamente!")
                        await state.clear()
                        return