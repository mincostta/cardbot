import os
import inspect
import math

from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import StateFilter
from states import Csub, Esub, Ctag, Etag, Atag, Rtag, Ccard, Ecard

from utils import is_admin, is_banned, painel_categorias, exist_sub_in_cat, exist_card_in_sub, exist_card, exist_tag, exist_sub, carta_user, up_bunny
from conn import get_cursor

raridades = {
    1: "Épica",
    2: "Rara",
    3: "Comum"
}

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

admins = Router()
TOKEN = os.getenv("TOKEN")

# -------------------------------------------
# INÍCIO DAS ETAPAS PARA ADICIONAR SUBCATEGORIA

async def addsub(telegram_id, msg):
    action = inspect.currentframe().f_code.co_name

    if await is_admin(telegram_id, msg):
        await msg.reply(f"🍑 Olá, ADM @{msg.from_user.username}! Dentro de qual categoria a sua sub irá se encaixar?", reply_markup=await painel_categorias(action))

async def resposta_cat(call, bot, state):
    cat = call.data.split('_')[1]
    
    await state.update_data(cat=cat)
    await bot.send_message(call.message.chat.id, f"Certo, categoria {cat}! Qual será o nome da sua subcategoria?")
    await state.set_state(Csub.nome)

@admins.message(StateFilter(Csub.nome))
async def nomearsub(msg, state):
    sub = msg.text

    dados = await state.get_data()
    cat = dados.get('cat')

    if await exist_sub_in_cat(cat, sub):
        await msg.reply(f"⚙️ Oops, a subcategoria {sub} já existe. Operação cancelada.")
        await state.clear()
    else:
        await state.update_data(sub=sub)
        await msg.reply(f"Combinado, o nome será {sub}! Agora selecione uma foto para essa subcategoria.")
        await state.set_state(Csub.foto)

@admins.message(StateFilter(Csub.foto))
async def confirm(msg, bot, state):
    if msg.photo:
        img = await bot.get_file(msg.photo[-1].file_id)
        await state.update_data(img=img)

        dados = await state.get_data()
        cat = dados.get('cat')
        sub = dados.get('sub')

        await msg.reply(f"🍑 Vamos confirmar sua adição. Aqui estão os dados: \n\n📌 Categoria: {cat} \n📌 Subcategoria: {sub} \n\n— E a imagem será a da mensagem mencionada! Digite sim para confirmar, ou cancele o processo.")
        await state.set_state(Csub.confirm)
    else:
        await msg.reply(f"⚙️ Oops, nenhuma imagem foi detectada. Operação cancelada.")
        await state.clear()

@admins.message(StateFilter(Csub.confirm))
async def salvarsub(msg, state):
    if msg.text.lower() == 'sim':
        dados = await state.get_data()
        cat = dados.get('cat')
        sub = dados.get('sub')
        img = dados.get('img')

        path = img.file_path
        url = f"https://api.telegram.org/file/bot{TOKEN}/{path}"

        user = 0
        bunny = await up_bunny(sub, user, url, "jpg")

        if bunny:
            async with get_cursor() as cursor:
                await cursor.execute("INSERT INTO divisoes (categoria, subcategoria, imagem) VALUES (%s, %s, %s)", (cat, sub, bunny,))

            await msg.reply(f"🍑 Ótimo, sua subcategoria {sub} foi criada com sucesso! Para visualizá-la, basta usar o comando /colheita.")
            await state.clear()
        else:
            await msg.reply("⚙️ Oops, houve um erro durante o upload da imagem... tente novamente.")
            await state.clear()
    else:
        await msg.reply("⚙️ Adição de subcategoria cancelada! Não se preocupe, nada foi adicionado.")
        await state.clear()

# FIM DAS ETAPAS PARA ADICIONAR SUBCATEGORIA

# -------------------------------------------
# INÍCIO DAS ETAPAS PARA EDITAR SUBCATEGORIA

async def editsub(telegram_id, msg, state):
    if await is_admin(telegram_id, msg):
        busca = msg.text.split(maxsplit=1)

        if len(busca) < 2:
            await msg.reply("⚙️ Por favor, forneça uma subcategoria para editar. Exemplo: /editsub nome.")
            await state.clear()
            return

        else:
            sub = busca[1]
            result = await exist_sub(sub, msg)

            if result:
                categoria = result[0]
                subcategoria = result[1]
                sub = subcategoria
                await state.update_data(sub=sub)

                opcoes = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="📌 NOME", callback_data=f"editnomesub_{sub}_action"),
                        InlineKeyboardButton(text="📌 IMAGEM", callback_data=f"editimgsub_{sub}_action")
                    ],
                    [
                        InlineKeyboardButton(text="📌 VARIAÇÕES", callback_data=f"editvarsub_{sub}_action")
                    ]
                ])

                await msg.reply(f"{categoria_emojis.get(categoria, '❓')} Olá, ADM @{msg.from_user.username}! Qual edição deseja fazer na subcategoria {sub}?", reply_markup=opcoes)
                await state.set_state(Esub.sub)
            else:
                await state.clear()

@admins.message(StateFilter(Esub.foto))
async def sub_editimg(msg, bot, state):
    if msg.photo:
        img = await bot.get_file(msg.photo[-1].file_id)
        dados = await state.get_data()
        sub = dados.get('sub')

        path = img.file_path
        url = f"https://api.telegram.org/file/bot{TOKEN}/{path}"

        user = 0
        bunny = await up_bunny(sub, user, url, "jpg")

        if bunny:
            async with get_cursor() as cursor:
                await cursor.execute("UPDATE divisoes SET imagem = %s WHERE subcategoria = %s", (bunny, sub,))
            await msg.reply(f"🍑 Certo, a imagem da subcategoria {sub} foi alterada com sucesso!")
            await state.clear()
        else:
            await msg.reply("⚙️ Oops, houve um erro durante o upload da imagem... tente novamente.")
            await state.clear()
    else:
        await msg.reply("⚙️ Oops, nenhuma imagem foi detectada. Operação cancelada.")
        await state.clear()

@admins.message(StateFilter(Esub.nome))
async def sub_editnome(msg, state):
    nome = msg.text
    dados = await state.get_data()
    sub = dados.get('sub')

    async with get_cursor() as cursor:
        if sub != nome:
            await cursor.execute("UPDATE divisoes SET subcategoria = %s WHERE subcategoria = %s", (nome, sub,))
            await msg.reply(f"🍑 Certo, nome da subcategoria {sub} alterado para {nome} com sucesso!")
        else:
            await msg.reply(f"⚙️ Oops, parece que você não mudou absolutamente nada no nome. Operação cancelada.")
    await state.clear()

@admins.message(StateFilter(Esub.addvar))
async def sub_addvar(msg, state):
    if ',' in msg.text:
        vars = [v.strip().lower() for v in msg.text.split(',')]
    else:
        vars = msg.text.split()
        if len(vars) > 1:
            await msg.reply(f"⚙️ Oops, você precisa separar as variações com vírgula. Operação cancelada.")
            await state.clear()
            return
        else:
            var = vars[0]

    dados = await state.get_data()
    sub = dados.get('sub')

    async with get_cursor() as cursor:
        await cursor.execute("SELECT shortner FROM divisoes WHERE subcategoria = %s", (sub,))
        haveshortner = await cursor.fetchone()

        atualshortner = haveshortner[0] if haveshortner and haveshortner[0] else None
        upshortner = atualshortner.split(',') if atualshortner else []

        novos = []
        for var in vars:
            var = var.lower()
            if var not in upshortner:
                upshortner.append(var)
                novos.append(var)

        if novos:
            alt = ','.join(upshortner)
            await cursor.execute("UPDATE divisoes SET shortner = %s WHERE subcategoria = %s", (alt, sub,))
            await msg.reply(f"🍑 Certo, as seguintes variações de nome para a subcategoria {sub} foram adicionadas com sucesso: {', '.join(novos)}.")
            await state.clear()
        else:
            await msg.reply(f"⚙️ Oops, parece que você não mudou absolutamente nada nas variações de nome da sub {sub}. Operação cancelada.")
            await state.clear() 

@admins.message(StateFilter(Esub.removevar))
async def sub_removevar(msg, state):
    if ',' in msg.text:
        vars = [v.strip().lower() for v in msg.text.split(',')]
    else:
        vars = msg.text.split()
        if len(vars) > 1:
            await msg.reply(f"⚙️ Oops, você precisa separar as variações com vírgula. Operação cancelada.")
            await state.clear()
            return
        else:
            var = vars[0]

    dados = await state.get_data()
    sub = dados.get('sub')
    atualshortner = dados.get('atualshortner')

    async with get_cursor() as cursor:
        shortner = atualshortner.split(',')

        removidos = []
        for var in vars:
            var = var.lower()
            if var in shortner:
                shortner.remove(var)
                removidos.append(var)

        if removidos:
            rmv = ','.join(shortner) if shortner else None
            await cursor.execute("UPDATE divisoes SET shortner = %s WHERE subcategoria = %s", (rmv, sub,))
            await msg.reply(f"🍑 Certo, as seguintes variações de nome da subcategoria {sub} foram removidas com sucesso: {', '.join(removidos)}.")
            await state.clear()
        else:
            await msg.reply(f"⚙️ Oops, parece que você não mudou absolutamente nada nas variações de nome da sub {sub}. Operação cancelada.")
            await state.clear() 

# FIM DAS ETAPAS PARA EDITAR SUBCATEGORIA

# -------------------------------------------
# INÍCIO DAS ETAPAS PARA CRIAR TAG

async def criartag(telegram_id, msg, state):
    if await is_admin(telegram_id, msg):
        await msg.reply(f"🍋 Olá, ADM @{msg.from_user.username}! Qual o nome da tag que deseja criar?")
        await state.set_state(Ctag.nome)
    else:
        await state.clear()

@admins.message(StateFilter(Ctag.nome))
async def formatag(msg, state):
    nome = msg.text

    if await exist_tag(nome):
        await msg.reply(f"⚙️ Oops, já existe uma tag com esse nome. Operação cancelada.")
        return
    else:
        await state.update_data(tag=nome)
        await msg.reply(f"Certo, o nome da sua tag será {nome}! Agora, forneça no mínimo dois ID's de cartas para fazerem parte dessa tag.")
        await state.set_state(Ctag.ids)

@admins.message(StateFilter(Ctag.ids))
async def foto_tag(msg, state):
    entradas = msg.text.split()
    ids = msg.text.split()

    if len(ids) < 2:
        await msg.reply("⚙️ Oops, você precisa enviar pelo menos dois ID's. Operação cancelada.")
        await state.clear()
        return
    
    try:
        for entrada in entradas:
            entrada = int(entrada)
    except ValueError:
        await msg.reply("⚙️ Oops, você só pode enviar ID's numéricos. Operação cancelada.")
        return

    ids_validos = []
    for card in ids:
        resultado = await exist_card(card, msg)
        if resultado:
            ids_validos.append(card)
        
    if len(ids_validos) == len(ids):
        await state.update_data(ids=ids_validos)
        await msg.reply(f"Certo, agora defina uma imagem para essa tag.")
        await state.set_state(Ctag.foto)
    else:
        await msg.reply("⚙️ Oops, algum dos seus ID's não existe. Operação cancelada.")
        await state.clear()
        return

@admins.message(StateFilter(Ctag.foto))
async def confirm_tag(msg, bot, state):
    if msg.photo:
        data = await state.get_data()
        ids_validos = data.get("ids", [])
        nome = data.get('tag')

        img = await bot.get_file(msg.photo[-1].file_id)
        await state.update_data(img=img)

        lista_cards = "\n".join([f"— ID. `{card_id}`" for card_id in ids_validos])

        await msg.reply(f"🍋 Vamos confirmar a formação da sua nova tag: \n\n📌 Nome: {nome}\n🃏 Cartas:\n{lista_cards} \n\n— E a imagem será a mencionada por essa mensagem. Digite sim para confirmar ou cancele a operação.")
        await state.set_state(Ctag.salvar)
    else:
        await msg.reply(f"⚙️ Oops, nenhuma imagem foi detectada. Operação cancelada.")
        await state.clear()
        return

@admins.message(StateFilter(Ctag.salvar))
async def salvar_tag(msg, state):
    if msg.text.lower() == 'sim':
        data = await state.get_data()
        ids_validos = data.get("ids", [])
        nome = data.get('tag')
        img = data.get('img')

        path = img.file_path
        url = f"https://api.telegram.org/file/bot{TOKEN}/{path}"

        user = 0
        bunny = await up_bunny(nome, user, url, "jpg")

        ids = tuple(map(int, ids_validos))
        
        if bunny:
            async with get_cursor() as cursor:
                await cursor.execute("INSERT INTO tags (nome, imagem) VALUES (%s, %s)", (nome, bunny,))
                query = "UPDATE cartas SET tag = %s WHERE id IN ({})".format(", ".join(["%s"] * len(ids)))
                await cursor.execute(query, (nome, *ids))

            await msg.reply(f"🍋 Sua tag {nome} foi criada e armazenada com sucesso! Use o comando /tag para visualizar.")
            await state.clear()
        else:
            await msg.reply("⚙️ Oops, houve um erro durante o upload da imagem... tente novamente.")
            await state.clear()
    else:
        await msg.reply("⚙️ Criação de tag cancelada. Não se preocupe, nada foi adicionado.")
        await state.clear()

# FIM DAS ETAPAS PARA CRIAR TAG

# -------------------------------------------
# INÍCIO DAS ETAPAS PARA EDITAR UMA TAG

async def editag(telegram_id, msg, state):
    if await is_admin(telegram_id, msg):
        busca = msg.text.split(maxsplit=1)

        if len(busca) < 2:
            await msg.reply("⚙️ Por favor, forneça uma tag para editar. Exemplo: /editag nome.")
            await state.clear()
            return

        else:
            tag = busca[1]
            result = await exist_tag(tag)

            if result:
                nome = result[0]
                tag = nome
                await state.update_data(tag=tag)

                opcoes = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="📌 NOME", callback_data=f"editnometag_{tag}"),
                        InlineKeyboardButton(text="📌 IMAGEM", callback_data=f"editimgtag_{tag}")
                    ]
                ])

                await msg.reply(f"🍋 Olá, ADM @{msg.from_user.username}! Qual edição deseja fazer na tag {tag}?", reply_markup=opcoes)
                await state.set_state(Etag.tag)
            else:
                await state.clear()

@admins.message(StateFilter(Etag.foto))
async def tag_editimg(msg, bot, state):
    if msg.photo:
        img = await bot.get_file(msg.photo[-1].file_id)
        dados = await state.get_data()
        tag = dados.get('tag')
        
        path = img.file_path
        url = f"https://api.telegram.org/file/bot{TOKEN}/{path}"

        user = 0
        bunny = await up_bunny(tag, user, url, "jpg")

        if bunny:
            async with get_cursor() as cursor:
                await cursor.execute("UPDATE tags SET imagem = %s WHERE nome = %s", (bunny, tag,))
                await msg.reply(f"🍋 Certo, a imagem da tag {tag} foi alterada com sucesso!")
                await state.clear()
        else:
            await msg.reply("⚙️ Oops, houve um erro durante o upload da imagem... tente novamente.")
            await state.clear()
    else:
        await msg.reply("⚙️ Oops, nenhuma imagem foi detectada. Operação cancelada.")
        await state.clear()

@admins.message(StateFilter(Etag.nome))
async def tag_editnome(msg, state):
    nome = msg.text
    dados = await state.get_data()
    tag = dados.get('tag')

    async with get_cursor() as cursor:
        if tag != nome:
            await cursor.execute("UPDATE tags SET nome = %s WHERE nome = %s", (nome, tag,))
            await msg.reply(f"🍋 Certo, nome da tag {tag} alterado para {nome} com sucesso!")
        else:
            await msg.reply(f"⚙️ Oops, parece que você não mudou absolutamente nada no nome. Operação cancelada.")
    await state.clear()

# FIM DAS ETAPAS PARA EDITAR UMA TAG

# -------------------------------------------
# INÍCIO DAS ETAPAS PARA ADICIONAR CARTAS À UMA TAG

async def addtag(telegram_id, msg, state):
    if await is_admin(telegram_id, msg):
        await msg.reply(f"🍋 Olá, ADM @{msg.from_user.username}! Em qual tag suas cartas irão se encaixar?")
        await state.set_state(Atag.tag)
    else:
        await state.clear()

@admins.message(StateFilter(Atag.tag))
async def resposta_tag(msg, state):
    tag = msg.text
    result = await exist_tag(tag)

    if result:
        tag = result[0]
        await state.update_data(tag=tag)
        await msg.reply(f"Certo, tag {tag}. Agora, diga um ou mais ID's para serem incluídos.")
        await state.set_state(Atag.ids)
    else:
        await msg.reply(f"⚙️ Oops, a tag {tag} não existe. Operação cancelada.")
        await state.clear()
    
@admins.message(StateFilter(Atag.ids))
async def confirm_add(msg, state):
    data = await state.get_data()
    tag = data.get('tag')
    ids = msg.text.split()
    ids_validos = []

    for card in ids:
        resultado = await exist_card(card, msg)
        if resultado:
            ids_validos.append(card)

    if len(ids_validos) == len(ids):
        async with get_cursor() as cursor:
            ids = tuple(map(int, ids_validos))
            query = "UPDATE cartas SET tag = %s WHERE id IN ({})".format(", ".join(["%s"] * len(ids)))
            await cursor.execute(query, (tag, *ids))

        await msg.reply(f"🍋 Certo, seus ID's foram incorporados na tag {tag} com sucesso.")
        await state.clear()
    else:
        await msg.reply("⚙️ Oops, algum dos seus ID's não existe. Operação cancelada.")
        await state.clear()
    
# FIM DAS ETAPAS PARA ADICIONAR CARTAS À UMA TAG

# -------------------------------------------
# INÍCIO DAS ETAPAS PARA REMOVER CARTAS DE UMA TAG

async def removetag(telegram_id, msg, state):
    if await is_admin(telegram_id, msg):
        await msg.reply(f"🍋 Olá, ADM @{msg.from_user.username}! De qual tag você deseja tirar cartas?")
        await state.set_state(Rtag.tag)
    else:
        await state.clear()

@admins.message(StateFilter(Rtag.tag))
async def cardsremovetag(msg, state):
    tag = msg.text
    result = await exist_tag(tag)
    if result:
        tag = result[0]
        await state.update_data(tag=tag)
        await msg.reply(f"Certo, tag {tag}. Agora, forneça os IDs das cartas que deseja remover.")
        await state.set_state(Rtag.ids)
    else:
        await msg.reply(f"⚙️ Oops, a tag {tag} não existe. Operação cancelada.")
        await state.clear()

@admins.message(StateFilter(Rtag.ids))
async def idsremovetag(msg, state):
    ids = msg.text.split()
    data = await state.get_data()
    tag = data.get('tag')
    apagados = []

    try:
        ids = [int(i) for i in ids]
        async with get_cursor() as cursor:
            for id in ids:
                await cursor.execute("SELECT id, tag FROM cartas WHERE id = %s AND tag = %s", (id, tag,))
                result = await cursor.fetchone()

                if result:
                    apagados.append(id)
                    await cursor.execute("UPDATE cartas SET tag = NULL WHERE id = %s", (id,))
        
        if len(ids) == len(apagados):
            texto = f"🍋 Certo, os seguintes IDs foram removidos da tag {tag}: {', '.join(map(str, apagados))}."
        elif len(apagados) > 0:
            texto = f"🍋 Oh, ocorreram alguns erros durante o caminho, mas você ainda conseguiu remover algumas cartas da tag {tag}: {', '.join(map(str, apagados))}."
        elif len(apagados) == 0:
            texto = f"⚙️ Todos os IDs fornecidos não pertencem à tag {tag} ou são inexistentes. Operação cancelada."

        await msg.reply(texto)
        await state.clear()
    except ValueError:
        await msg.reply("⚙️ Oops, você só pode enviar ID's numéricos. Operação cancelada.")
        await state.clear()

# FIM DAS ETAPAS PARA REMOVER CARTAS DE UMA TAG

# -------------------------------------------
# INÍCIO DAS ETAPAS PARA ADICIONAR CARTA

async def addcard(telegram_id, msg):
    action = inspect.currentframe().f_code.co_name
    
    if await is_admin(telegram_id, msg):
        await msg.reply(f"🍊 Olá, ADM @{msg.from_user.username}! Dentro de qual categoria sua nova carta irá se encaixar?", reply_markup=await painel_categorias(action))

async def card_cat(call, bot, state):
    cat = call.data.split('_')[1]

    await state.update_data(cat=cat)
    await bot.send_message(call.message.chat.id, f"Certo, categoria {cat}! Qual a subcategoria da sua carta?")
    await state.set_state(Ccard.sub)

@admins.message(StateFilter(Ccard.sub))
async def card_sub(msg, state):
    sub = msg.text

    dados = await state.get_data()
    cat = dados.get('cat')
    result = await exist_sub_in_cat(cat, sub)

    if result:
        sub = result[1]
        await state.update_data(sub=sub)
        await msg.reply(f"Combinado, a subcategoria será {sub}! Agora dê um nome à sua carta.")
        await state.set_state(Ccard.nome)
    else:
        await msg.reply(f"⚙️ Oops, a subcategoria {sub} não existe dentro de {cat}. Operação cancelada.")
        await state.clear()

@admins.message(StateFilter(Ccard.nome))    
async def card_nome(msg, state):
    nome = msg.text
    dados = await state.get_data()
    sub = dados.get('sub')

    card = await exist_card_in_sub(nome, msg, sub)

    if card == False:
        await state.update_data(nome=nome)
        await msg.reply(f"Combinado, o nome da carta será {nome}! Agora escolha a raridade: 1, 2 ou 3 (épica, rara e comum, respectivamente).")
        await state.set_state(Ccard.rare)
    else:
        await state.clear()

@admins.message(StateFilter(Ccard.rare))    
async def card_rarity(msg, state):
    if msg.text:
        try:
            Nraridade = int(msg.text)
            if 1 <= Nraridade <= 3:
                raridade = raridades[Nraridade]
                await state.update_data(raridade=Nraridade)
                await msg.reply(f"Certo, a raridade será {raridade}. Hora de escolher a foto da carta!")
                await state.set_state(Ccard.confirm)
            else:
                await msg.reply("⚙️ Oops, só são aceitos números de 1 a 3. Operação cancelada.")
                await state.clear()
        except ValueError:
            await msg.reply("⚙️ Mensagem inválida. Operação cancelada.")
            await state.clear()
    else:
        await msg.reply("⚙️ Mensagem inválida. Operação cancelada.")
        await state.clear()

@admins.message(StateFilter(Ccard.confirm)) 
async def card_confirm(msg, bot, state):
    if msg.photo:
        dados = await state.get_data()
        cat = dados.get('cat')
        sub = dados.get('sub')
        nome = dados.get('nome')
        Nraridade = dados.get('raridade')
        raridade = raridades[Nraridade]

        img = await bot.get_file(msg.photo[-1].file_id)
        await state.update_data(img=img)

        await msg.reply(f"🍊 Vamos confirmar sua adição de carta. Aqui estão os dados: \n\n📌 Categoria: {cat} \n📌 Subcategoria: {sub} \n📌 Nome: {nome} \n📌 Raridade: {raridade} \n\n— E a imagem será a da mensagem mencionada! Digite sim para confirmar, ou cancele o processo.")
        await state.set_state(Ccard.salvar)
    else:
        await msg.reply(f"⚙️ Oops, nenhuma imagem foi detectada. Operação cancelada.")
        await state.clear()

@admins.message(StateFilter(Ccard.salvar)) 
async def salvarcard(msg, state):
    if msg.text.lower() == 'sim':
        dados = await state.get_data()
        cat = dados.get('cat')
        sub = dados.get('sub')
        nome = dados.get('nome')
        img = dados.get('img')
        Nraridade = dados.get('raridade')

        path = img.file_path
        url = f"https://api.telegram.org/file/bot{TOKEN}/{path}"

        async with get_cursor() as cursor:
            await cursor.execute("SELECT MAX(id) AS ultimo FROM cartas")
            result = await cursor.fetchone()
            id = result[0] + 1

        user = 0
        bunny = await up_bunny(id, user, url, "jpg")

        if bunny:
            async with get_cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO cartas (nome, raridade, imagem, categoria, subcategoria) VALUES (%s, %s, %s, %s, %s)", (nome, Nraridade, bunny, cat, sub,))

            await msg.reply(f"🍊 Ótimo, sua carta {nome} foi criada com sucesso! Para visualizá-la, basta usar o comando /buscar.")
            await state.clear()
        else:
            await msg.reply("⚙️ Oops, houve um erro durante o upload da imagem... tente novamente.")
            await state.clear()
    else:
        await msg.reply("⚙️ Adição de carta cancelada! Não se preocupe, nada foi adicionado.")
        await state.clear()
            
# FIM DAS ETAPAS PARA ADICIONAR CARTA

# -------------------------------------------
# INÍCIO DAS ETAPAS PARA EDITAR CARTA

async def editcard(telegram_id, msg, state):
    if await is_admin(telegram_id, msg):
        busca = msg.text.split()

        if len(busca) < 2:
            await msg.reply("⚙️ Por favor, forneça um card para editar. Exemplo: /editcard ID.")
            return
        elif len(busca) > 2:
            await msg.reply("⚙️ Forneça somente um ID para editar. Exemplo: /editcard ID.")
            return
        else:
            card = busca[1]

            try:
                card = int(card)
                result = await exist_card(card, msg)

                if result:
                    opcoes = InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(text="📌 NOME", callback_data=f"editnomecard_{card}"),
                            InlineKeyboardButton(text="📌 IMAGEM", callback_data=f"editimgcard_{card}")
                        ],
                        [
                            InlineKeyboardButton(text="📌 SUB", callback_data=f"editsubcard_{card}"),
                            InlineKeyboardButton(text="📌 RARIDADE", callback_data=f"editrarecard_{card}")
                        ],
                        [
                            InlineKeyboardButton(text="📌 MULTI SUB", callback_data=f"addsubcard_{card}")
                        ]
                    ])

                    await state.update_data(card=card)
                    await msg.reply(f"🍊 Olá, ADM @{msg.from_user.username}! Qual edição deseja fazer no card `{card}`?", reply_markup=opcoes)
                    await state.set_state(Ecard.card)
                else:
                    return
            except ValueError:
                await msg.reply("⚙️ Oops, só é possível editar uma carta com base no seu ID.")
                await state.clear()
    else:
        return

@admins.message(StateFilter(Ecard.nome)) 
async def card_editnome(msg, state):
    dados = await state.get_data()
    card = dados.get('card')
    nome = msg.text

    async with get_cursor() as cursor:
        await cursor.execute("SELECT nome FROM cartas WHERE id = %s", (card,))
        result = await cursor.fetchone()

        if nome != result[0]:
            await cursor.execute("UPDATE cartas SET nome = %s WHERE id = %s", (nome, card,))
            await msg.reply(f"🍊 Certo, nome da carta `{card}` alterado para {nome} com sucesso!")
            await state.clear()
        else:
            await msg.reply(f"⚙️ Oops, parece que você não mudou absolutamente nada no nome. Operação cancelada.")
            await state.clear()

@admins.message(StateFilter(Ecard.img)) 
async def card_editimg(msg, bot, state):
    if msg.photo:
        img = await bot.get_file(msg.photo[-1].file_id)
        dados = await state.get_data()
        card = dados.get('card')

        path = img.file_path
        url = f"https://api.telegram.org/file/bot{TOKEN}/{path}"

        user = 0
        bunny = await up_bunny(id, user, url, "jpg")

        if bunny:
            async with get_cursor() as cursor:
                await cursor.execute("UPDATE cartas SET imagem = %s WHERE id = %s", (bunny, card,))
                await msg.reply(f"🍊 Certo, imagem do card `{card}` alterada com sucesso!")
                await state.clear()
        else:
            await msg.reply("⚙️ Oops, houve um erro durante o upload da imagem... tente novamente.")
            await state.clear()
    else:
        await msg.reply("⚙️ Oops, nenhuma imagem foi detectada. Operação cancelada.")
        await state.clear()

@admins.message(StateFilter(Ecard.sub))
async def card_editsub(msg, state):
    dados = await state.get_data()
    card = dados.get('card')
    sub = msg.text

    result = await exist_sub(sub, msg)

    if result:
        sub = result[1]
        cat = result[0]
        async with get_cursor() as cursor:
            await cursor.execute("SELECT subcategoria, categoria FROM cartas WHERE id = %s", (card,))
            result = await cursor.fetchone()

            if sub != result[0]:
                if cat == result[1]:
                    await cursor.execute("UPDATE cartas SET subcategoria = %s WHERE id = %s", (sub, card,))
                    await msg.reply(f"🍊 Certo, subcategoria da carta `{card}` alterada para {sub} com sucesso!")
                    await state.clear()
                else:
                    await cursor.execute("UPDATE cartas SET categoria = %s, subcategoria = %s WHERE id = %s", (cat, sub, card,))
                    await msg.reply(f"🍊 Certo, subcategoria da carta `{card}` alterada para {sub} com sucesso!")
                    await state.clear()
            else:
                await msg.reply(f"⚙️ Oops, parece que você não mudou a subcategoria da carta. Operação cancelada.")
                await state.clear()

@admins.message(StateFilter(Ecard.rare))
async def card_editrarity(msg, state):
    dados = await state.get_data()
    card = dados.get('card')
    raridade = msg.text

    try:
        raridade = int(raridade)
        if raridade > 3 or raridade < 1:
            await msg.reply("⚙️ Oops, só são aceitos números de 1 a 3. Operação cancelada.")
            await state.clear()
            return
    except ValueError:
        raridade = raridade.capitalize()

        if raridade in ["Épica", "Rara", "Comum"]:
            raridades_inv = {v: k for k, v in raridades.items()}
            raridade = raridades_inv[raridade]
        else:
            await msg.reply("⚙️ Oops, você precisa escolher entre Épica, Rara ou Comum. Operação cancelada.")
            await state.clear()
            return

    async with get_cursor() as cursor:
        await cursor.execute("SELECT raridade FROM cartas WHERE id = %s", (card,))
        result = await cursor.fetchone()

        if result[0] != raridade:
            await cursor.execute("UPDATE cartas SET raridade = %s WHERE id = %s", (raridade, card,))
            raridade = raridades[raridade]
            await msg.reply(f"🍊 Certo, raridade da carta `{card}` alterada para {raridade} com sucesso!")
        else:
            await msg.reply(f"⚙️ Oops, parece que você não mudou absolutamente nada na raridade. Operação cancelada.")
        await state.clear()

@admins.message(StateFilter(Ecard.multisub))
async def card_multisub(msg, state):
    dados = await state.get_data()
    card = dados.get('card')
    sub = msg.text

    result = await exist_sub(sub, msg)

    if result:
        sub = result[1]
        cat = result[0]

        async with get_cursor() as cursor:
            await cursor.execute("SELECT subcategoria, categoria FROM cartas WHERE id = %s", (card,))
            result = await cursor.fetchone()

            if sub != result[0]:
                await cursor.execute("SELECT subcategoria FROM multisub WHERE id = %s AND subcategoria = %s", (card, sub,))
                multi = await cursor.fetchone()

                if multi:
                    await msg.reply("⚙️ Oops, seu card já está incluído nessa subcategoria.")
                    await state.clear()
                else:
                    await cursor.execute("INSERT INTO multisub (id, subcategoria, categoria) VALUES (%s, %s, %s)", (card, sub, cat,))
                    await msg.reply(f"🍊 Certo, a carta `{card}` agora faz parte da subcategoria {sub}!")
                    await state.clear()
            else:
                await msg.reply(f"⚙️ Oops, seu card já está incluído nessa subcategoria.")
                await state.clear()

# FIM DAS ETAPAS PARA EDITAR CARTA

# -------------------------------------------
# COMANDO PARA VER O USERNAME DE UM USUÁRIO

async def checar(telegram_id, bot, msg):
    if await is_admin(telegram_id, msg):
        busca = msg.text.split()

        if len(busca) < 2:
            await msg.reply("⚙️ Por favor, forneça o ID de um habitante para checar. Exemplo: /checar ID.")
            return
        elif len(busca) > 2:
            await msg.reply("⚙️ Forneça somente um ID de um habitante para checar. Exemplo: /checar ID.")
            return
        else:
            checar = busca[1]

            try:
                id = int(checar)

                async with get_cursor() as cursor:
                    await cursor.execute("SELECT telegram_id, username FROM usuarios WHERE id = %s", (id,))
                    checagem = await cursor.fetchone()

                    if checagem:
                        user = await bot.get_chat(checagem[0])
                        username = user.username

                        if username != checagem[1]:
                            await cursor.execute("UPDATE usuarios SET username = %s WHERE username = %s", (username, checagem[1],))
                        
                        await msg.reply(f"🍪 Olá, ADM @{msg.from_user.username}, o ID {id} pertence ao usuário @{username}!")
                    else:
                        await msg.reply("⚙️ Oops, não foi possível encontrar ninguém na Vila Tutti-Fruti com esse ID.")
            except ValueError:
                await msg.reply("⚙️ Oops, só são aceitos ID's numéricos para checagem.")

# -------------------------------------------
# INÍCIO DAS ETAPAS PARA RESETAR UM USUÁRIO

async def reset(telegram_id, bot, msg):
    if await is_admin(telegram_id, msg):
        reset = msg.text.split()        

        if len(reset) < 2:
            await msg.reply("⚙️ Por favor, forneça um ID ou @ de habitante para banir. Exemplo: /reset ID.")
            return
        elif len(reset) > 2:
            await msg.reply("⚙️ Forneça somente um ID ou @ de habitante. Exemplo: /reset ID.")
            return
        else:
            reset = reset[1]
            chat_id = msg.chat.id

            async with get_cursor() as cursor:
                try:
                    iduser = int(reset)
                    await cursor.execute("SELECT id, telegram_id FROM usuarios WHERE id = %s", (iduser,))
                    result = await cursor.fetchone()

                    if not result:
                        await msg.reply("⚙️ Oops, não foi possível encontrar ninguém na Vila Tutti-Fruti com esse ID.")
                        return
                    else:
                        id, telegram_id = result
                        user = await bot.get_chat_member(chat_id, telegram_id)
                        iduser = id
                        tlid = result[1]

                        username = f"{user.user.username}" if user.user.username else "Nenhum username."
                        if username != "Nenhum username.":
                            usernamelink = f"[@{username}](https://t.me/{username})"
                        else:
                            usernamelink = username

                except ValueError:
                    username = reset.lstrip("@")

                    await cursor.execute("SELECT id, telegram_id, username FROM usuarios WHERE username = %s", (username,))
                    result = await cursor.fetchone()

                    if await is_banned(result[1], msg, username) != False:
                        await msg.reply(f"⚙️ Habitante [@{username}](https://t.me/{username}) está expulso da Vila Tutti-Frutti.")
                        return
                    if not result:
                        await msg.reply("⚙️ Oops, não foi possível encontrar ninguém na Vila Tutti-Fruti com esse username.")
                        return
                    else:
                        id, telegram_id, username = result
                        iduser = result[0]
                        tlid = result[1]

                        usernamelink = f"[@{username}](https://t.me/{username})"
    
            resetbtns = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="CONFIRMAR 🌿", callback_data=f"confirmreset_{tlid}"),
                    InlineKeyboardButton(text="CANCELAR ❌", callback_data="cancelreset")
                ]
            ])

            await msg.reply(f"🌿 Você está prestes a resetar o usuário {usernamelink}, apagando todas as frutinhas, sementes e colheitas. Tem certeza disso?", reply_markup=resetbtns)
    else:
        return

async def confirmreset(msg, bot, tlid, chat_id, username, adm):
    async with get_cursor() as cursor:
        await cursor.execute("DELETE FROM usuarios WHERE telegram_id = %s", (tlid,))
        await cursor.execute("INSERT INTO gerencia (adm, operaçao, destinatario) VALUES (%s, %s, %s)", (adm, "reset", tlid,))

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg.message_id,
        text=f"🌿 O habitante @{username} foi resetado com sucesso. Todas as suas frutinhas, sementes e pertences num geral foram descartadas. Ainda assim, é possível recomeçar seu legado na Vila Tutti-Frutti usando /start!"
    )
    
# FIM DAS ETAPAS PARA RESETAR UM USUÁRIO

# -------------------------------------------
# INÍCIO DAS ETAPAS PARA BANIR UM USUÁRIO

async def ban(telegram_id, bot, msg):
    if await is_admin(telegram_id, msg):
        ban = msg.text.split()        

        if len(ban) < 2:
            await msg.reply("⚙️ Por favor, forneça um ID ou @ de habitante para banir. Exemplo: /ban ID.")
            return
        elif len(ban) > 2:
            await msg.reply("⚙️ Forneça somente um ID ou @ de habitante. Exemplo: /ban ID.")
            return
        else:
            ban = ban[1]
            chat_id = msg.chat.id

            async with get_cursor() as cursor:
                try:
                    iduser = int(ban)
                    await cursor.execute("SELECT id, telegram_id FROM usuarios WHERE id = %s", (iduser,))
                    result = await cursor.fetchone()

                    if not result:
                        await msg.reply("⚙️ Oops, parece que esse ID de usuário não existe ou já está banido.")
                        return
                    else:
                        id, telegram_id = result
                        user = await bot.get_chat_member(chat_id, telegram_id)
                        iduser = id
                        tlid = result[1]

                        nome = user.user.first_name or "Nenhum nome."
                        if nome != "Nenhum nome.":
                            nome = f"[{nome}](tg://user?id={telegram_id})"

                        username = f"{user.user.username}" if user.user.username else "Nenhum username."
                        if username != "Nenhum username.":
                            usernamelink = f"[@{username}](https://t.me/{username})"
                        else:
                            usernamelink = username

                except ValueError:
                    username = ban.lstrip("@")

                    await cursor.execute("SELECT id, telegram_id, username FROM usuarios WHERE username = %s", (username,))
                    result = await cursor.fetchone()

                    if result and await is_banned(result[1], msg, username) != False:
                        await msg.reply(f"⚙️ Habitante [@{username}](https://t.me/{username}) já está expulso.")
                        return
                    if not result:
                        await msg.reply("⚙️ Oops, não foi possível encontrar ninguém na Vila Tutti-Fruti com esse username.")
                        return
                    else:
                        id, telegram_id, username = result
                        iduser = result[0]
                        tlid = result[1]

                        user = await bot.get_chat(result[1])
                        nome = f"{user.first_name} {user.last_name or ''}".strip()

                        nome = f"[{nome}](tg://user?id={telegram_id})"
                        usernamelink = f"[@{username}](https://t.me/{username})"
    
            banbtns = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="EXPULSAR 🧹", callback_data=f"confirmban_{tlid}"),
                    InlineKeyboardButton(text="CANCELAR ❌", callback_data="cancelban")
                ]
            ])

            await msg.reply(f"🧹 Deseja mesmo varrer o usuário de ID número {iduser} para fora da Vila Tutti-Frutti? Confira as informações abaixo e confirme ou cancele a operação: \n\n🍉 Nome: {nome} \n🍉 Username: {usernamelink}", reply_markup=banbtns)
    else:
        return

async def confirmban(msg, bot, tlid, chat_id, username, adm):
    async with get_cursor() as cursor:
        await cursor.execute("INSERT INTO banidos (telegram_id, username, adm) VALUES (%s, %s, %s)", (tlid, username, adm,))
        await cursor.execute("DELETE FROM usuarios WHERE telegram_id = %s", (tlid,))

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg.message_id,
        text=f"🍉 O habitante @{username} foi varrido para fora da Vila Tutti-Frutti com sucesso. Todas as suas frutinhas, sementes e pertences num geral foram descartadas, não retornando nem em caso de desban."
    )

# FIM DAS ETAPAS PARA BANIR UM USUÁRIO

# -------------------------------------------
# INÍCIO DAS ETAPAS PARA DESBANIR UM USUÁRIO

async def desban(telegram_id, bot, msg):
    if await is_admin(telegram_id, msg):
        desban = msg.text.split()

        if len(desban) < 2:
            await msg.reply("⚙️ Por favor, forneça um @ de usuário para trazer de volta à Vila Tutti-Frutti. Exemplo: /desban @user.")
            return
        elif len(desban) > 2:
            await msg.reply("⚙️ Forneça somente um @ de usuário. Exemplo: /desban @user.")
            return
        else:
            username = desban[1]

            try:
                username = int(username)
                await msg.reply("⚙️ Oops, você só pode desbanir com base no username.")
                return
            except ValueError:
                username = username.lstrip("@")
                
                async with get_cursor() as cursor:
                    await cursor.execute("SELECT telegram_id, username FROM banidos WHERE username = %s", (username,))
                    result = await cursor.fetchone()

                if not result:
                    await msg.reply("⚙️ Oops, esse usuário não está banido ou trocou o username recentemente. Qualquer tentativa de interação com o bot atualizará o username!")
                    return
                else:
                    telegram_id, username = result
                    user = await bot.get_chat(telegram_id)
                    nome = f"{user.first_name} {user.last_name or ''}".strip()
                    nome = f"[{nome}](tg://user?id={telegram_id})"
                    username = f"[@{username}](https://t.me/{username})"
                
                desbanbtns = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text="ACEITAR 🌺", callback_data=f"confirmdesban_{telegram_id}"),
                            InlineKeyboardButton(text="CANCELAR ❌", callback_data="canceldesban")
                        ]
                    ]
                )

                await msg.reply(f"🌺 Deseja mesmo trazer de volta o usuário {username} para a Vila Tutti-Frutti? Habitante {nome} retornará com um novo ID e sem nenhuma frutinha.", reply_markup=desbanbtns)

async def confirmdesban(msg, bot, tlid, chat_id, username, adm):
    async with get_cursor() as cursor:
        await cursor.execute("INSERT INTO usuarios (telegram_id, username) VALUES (%s, %s)", (tlid, username,))
        await cursor.execute("DELETE FROM banidos WHERE telegram_id = %s", (tlid,))
        await cursor.execute("INSERT INTO gerencia (adm, operaçao, destinatario) VALUES (%s, %s, %s)", (adm, "desban", tlid,))

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg.message_id,
        text=f"🌺 Habitante @{username} está de volta à Vila Tutti-Frutti com sucesso. Boas-vindas outra vez!"
    )

# FIM DAS ETAPAS PARA DESBANIR UM USUÁRIO

# -------------------------------------------
# COMANDO PARA VER OS MAIS GIRADOS DE UMA SUB

async def girados(telegram_id, bot, msg):
    if await is_admin(telegram_id, msg):
        busca = msg.text.split(' ', 1)

        if len(busca) < 2:
            await msg.reply("⚙️ Por favor, forneça uma subcategoria para pesquisar. Exemplo: /girados sub.")
            return
        
        sub = busca[1]
        result = await exist_sub(sub, msg)

        if result:
            sub = result[1]
            img = result[2]
            imagem = FSInputFile(img)

            async with get_cursor() as cursor:
                await cursor.execute("""
                    SELECT c.id, SUM(i.quantidade)
                    FROM cartas c
                    LEFT JOIN inventario i ON c.id = i.id_carta
                    WHERE c.subcategoria = %s
                    GROUP BY c.id
                    ORDER BY SUM(i.quantidade) DESC
                """, (sub,))
                girados = await cursor.fetchall()

                if girados:
                    total = sum([row[1] or 0 for row in girados])
                    texto = f"🍑 Olá, ADM @{msg.from_user.username}! Aqui está a lista dos cards mais girados aos menos girados da subcategoria {sub}.\n"

                    for row in girados:
                        id = row[0]
                        quantidade = row[1] or 0
                        await cursor.execute("SELECT nome, raridade FROM cartas WHERE id = %s", (id,))
                        card = await cursor.fetchone()

                        nome = card[0]
                        raridade = card[1]
                        texto += f"\n{raridade_emojis.get(raridade, '❓')} `{id}`. {nome} ({quantidade}x)"
                    
                    texto+= f"\n\n🍁 {total} cards foram girados no total."

                    await bot.send_photo(
                        chat_id=msg.chat.id,
                        photo=imagem,
                        caption=texto,
                        reply_to_message_id=msg.message_id
                    )
                else:
                    await msg.reply(f"⚙️ Oops, parece que nenhum card da subcategoria {sub} foi girado ainda.")

# -------------------------------------------
# COMANDO PARA VER OS MAIS GIRADOS DE UMA CAT

async def allberry(telegram_id, msg):
    if await is_admin(telegram_id, msg):
        busca = msg.text.split(' ', 1)

        if len(busca) < 2:
            await msg.reply("⚙️ Por favor, forneça uma categoria para pesquisar. Exemplo: /allberry cat.")
            return
        
        cat = busca[1].upper()

        if cat in ("MORANGEEK", "ASIAFARM", "STREAMBERRY", "FRUITMIX"):
            async with get_cursor() as cursor:
                await cursor.execute("""
                    SELECT c.subcategoria, SUM(i.quantidade)
                    FROM cartas c
                    LEFT JOIN inventario i ON c.id = i.id_carta
                    WHERE c.categoria = %s
                    GROUP BY c.subcategoria
                    ORDER BY SUM(i.quantidade) DESC
                    LIMIT 20
                """, (cat,))
                allberry = await cursor.fetchall()

                if allberry:
                    await cursor.execute("""
                        SELECT SUM(i.quantidade) AS total
                        FROM cartas c
                        LEFT JOIN inventario i ON c.id = i.id_carta
                        WHERE c.categoria = %s
                    """, (cat,))
                    contagem = await cursor.fetchone()
                    Ncards = contagem[0]
                else:
                    await msg.reply(f"{categoria_emojis.get(cat, '❓')} Oops, parece que nenhum card da categoria {cat} foi girado ainda.")
                    return
        else:
            await msg.reply(f"⚙️ Oops, parece que a categoria {cat} não existe.")
            return

        linhas = len(allberry)
        total_pag = math.ceil(int(linhas) / 10)

        texto = f"{categoria_emojis.get(cat, '❓')} Olá, ADM @{msg.from_user.username}! Aqui estão as subcategorias mais giradas da categoria {cat}.\n💌 Página 1 de {total_pag}.\n"

        nmr = 0   
        for row in allberry:
            if nmr < 10:
                nmr += 1
                sub = row[0]
                quantidade = row[1] or 0
                texto += f"\n{nmr}. {sub} ({quantidade}x)"
        
        texto += f"\n\n🍁 {Ncards} cards foram girados no total.\n\u200B"
        if total_pag == 2:
            allberryopt = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="➡️", callback_data=f"allberry_prox_{cat}_{Ncards}_1_{total_pag}")
                ]
            ])
            await msg.reply(texto, reply_markup=allberryopt)
        else:
            await msg.reply(texto)
    
# -------------------------------------------
# COMANDO PARA PREMIAR UM USUÁRIO COM SEMENTES

async def fermentar(telegram_id, bot, msg):
    if await is_admin(telegram_id, msg):
        fermentar = msg.text.split()

        if not msg.reply_to_message and len(fermentar) == 3:
            try:
                quantidade = int(fermentar[1])
                username = fermentar[2].lstrip('@')

                if username == msg.from_user.username:
                    await msg.reply("⚙️ Oops, você não pode fermentar sementes para si mesmo.")
                    return
                
                async with get_cursor() as cursor:
                    await cursor.execute("SELECT telegram_id FROM usuarios WHERE username = %s", (username,))
                    user = await cursor.fetchone()

                    if user:
                        destinatário = int(user[0])
                    else:
                        await msg.reply("⚙️ Oops, parece que esse usuário não é um habitante da Vila Tutti-Frutti ou não está com o username atualizado. Para atualizar, basta usar qualquer comando!")
                        return
            except ValueError:
                await msg.reply("⚙️ Oops, parece que você ofereceu uma quantidade inválida.")
                return
        elif msg.reply_to_message and len(fermentar) == 2:
            try:
                quantidade = int(fermentar[1])
                destinatário = msg.reply_to_message.from_user.id
                username = msg.reply_to_message.from_user.username

                if username == msg.from_user.username:
                    await msg.reply("⚙️ Oops, você não pode fermentar sementes para si mesmo.")
                    return
                
                async with get_cursor() as cursor:
                    await cursor.execute("SELECT telegram_id FROM usuarios WHERE telegram_id = %s", (destinatário,))
                    user = await cursor.fetchone()
                
                if not user:
                    await msg.reply("⚙️ Oops, parece que esse usuário não é um habitante da Vila Tutti-Frutti.")
                    return
            except ValueError:
                await msg.reply("⚙️ Oops, parece que você ofereceu uma quantidade inválida.")
                return
        else:
            await msg.reply("⚙️ Oops, parece que há algum erro na estrutura do comando. Exemplo: /fermentar quantidade @user.")
            return

        user = await bot.get_chat(telegram_id)
        adm = user.username

        async with get_cursor() as cursor:
            await cursor.execute("UPDATE usuarios SET sementes = sementes + %s WHERE telegram_id = %s", (quantidade, destinatário,))
            await cursor.execute("INSERT INTO gerencia (adm, operaçao, destinatario, quantidade) VALUES(%s, %s, %s, %s)", (adm, "fermentar", destinatário, quantidade,))
        await msg.reply(f"Oba, o usuário @{username} recebeu {quantidade} sementes para sua plantação! ✨")

# -------------------------------------------
# COMANDO PARA PREMIAR TODOS OS USUÁRIOS COM SEMENTES

async def fermentarall(telegram_id, bot, msg):
    if await is_admin(telegram_id, msg):
        fermentar = msg.text.split()

        if len(fermentar) == 2:
            try:
                quantidade = fermentar[1]
                quantidade = int(quantidade)
                user = await bot.get_chat(telegram_id)
                adm = user.username

                async with get_cursor() as cursor:
                    await cursor.execute("UPDATE usuarios SET sementes = sementes + %s", (quantidade,))
                    await cursor.execute("INSERT INTO gerencia (adm, operaçao, destinatario, quantidade) VALUES(%s, %s, %s, %s)", (adm, "fermentarall", 100, quantidade,))
            
                await msg.reply(f"Oba, todos os habitantes da Vila Tutti-Frutti receberam {quantidade} sementes para suas plantações! ✨")
            except ValueError:
                await msg.reply("⚙️ Oops, parece que você ofereceu uma quantidade inválida.")
                return
        else:
            await msg.reply("⚙️ Oops, parece que há algum erro de estrutura no seu comando. Exemplo: /fermentarall quantidade.")
            return

# -------------------------------------------
# COMANDO PARA PRESENTEAR UM USUÁRIO COM CARDS

async def presentear(telegram_id, msg):
    if await is_admin(telegram_id, msg):
        fermentar = msg.text.split()

        if not msg.reply_to_message:
            if len(fermentar) == 4:
                try:
                    id = int(fermentar[2])
                    quantidade = int(fermentar[3])
                    username = fermentar[1].lstrip('@')

                    if username == msg.from_user.username:
                        await msg.reply("⚙️ Oops, você não pode presentear frutinhas à si mesmo.")
                        return
                
                    async with get_cursor() as cursor:
                        await cursor.execute("SELECT telegram_id FROM usuarios WHERE username = %s", (username,))
                        user = await cursor.fetchone()

                    if user:
                        destinatário = int(user[0])
                    else:
                        await msg.reply("⚙️ Oops, parece que esse usuário não é um habitante da Vila Tutti-Frutti ou não está com o username atualizado. Para atualizar, basta usar qualquer comando!")
                        return
                except ValueError:
                    await msg.reply("⚙️ Oops, parece que você ofereceu uma quantidade ou ID inválido.")
                    return
            else:
                await msg.reply("⚙️ Oops, parece que há algum erro de estrutura no seu comando. Exemplo: /presentear @user ID quantidade.")
                return
        else:
            destinatário = msg.reply_to_message.from_user.id
            username = msg.reply_to_message.from_user.username

            if username == msg.from_user.username:
                await msg.reply("⚙️ Oops, você não pode presentear frutinhas à si mesmo.")
                return

            if len(fermentar) == 3:
                try:
                    id = int(fermentar[1])
                    quantidade = int(fermentar[2])
                except ValueError:
                    await msg.reply("⚙️ Oops, parece que você ofereceu uma quantidade ou ID inválido.")
                    return
            else:
                await msg.reply("⚙️ Oops, parece que há algum erro de estrutura no seu comando. Tente quotar uma mensagem usando o seguinte comando: /presentear ID quantidade.")
                return
            
        adm = msg.from_user.username

        if await exist_card(id, msg):
            async with get_cursor() as cursor:
                Ncards = await carta_user(destinatário, id, cursor)

                if Ncards:
                    await cursor.execute("UPDATE inventario SET quantidade = quantidade + %s WHERE id_user = %s AND id_carta = %s", (quantidade, destinatário, id,))
                else:
                    await cursor.execute("INSERT INTO inventario (id_user, id_carta, quantidade) VALUES (%s, %s, %s)", (destinatário, id, quantidade,))     
                await cursor.execute("INSERT INTO gerencia (adm, operaçao, destinatario, quantidade, card) VALUES(%s, %s, %s, %s, %s)", (adm, "presentear", destinatário, quantidade, id,))

                if quantidade > 1:
                    await msg.reply(f"Você premiou @{username} com {quantidade} frutinhas `{id}`! 🎁")
                else:
                    await msg.reply(f"Você premiou @{username} com {quantidade} frutinha `{id}`! 🎁")

# -------------------------------------------
# COMANDO PARA REMOVER CARDS DE UM USUÁRIO

async def remove(telegram_id, msg):
    if await is_admin(telegram_id, msg):
        remove = msg.text.split()

        if not msg.reply_to_message:
            if len(remove) == 4:
                try:
                    id = int(remove[2])
                    quantidade = int(remove[3])
                    username = remove[1].lstrip('@')

                    if username == msg.from_user.username:
                        await msg.reply("⚙️ Oops, você não pode remover frutinhas da sua própria cestinha.")
                        return
                
                    async with get_cursor() as cursor:
                        await cursor.execute("SELECT telegram_id FROM usuarios WHERE username = %s", (username,))
                        user = await cursor.fetchone()

                    if user:
                        destinatário = int(user[0])
                    else:
                        await msg.reply("⚙️ Oops, parece que esse usuário não é um habitante da Vila Tutti-Frutti ou não está com o username atualizado. Para atualizar, basta usar qualquer comando!")
                        return
                except ValueError:
                    await msg.reply("⚙️ Oops, parece que você ofereceu uma quantidade ou ID inválido.")
                    return
            else:
                await msg.reply("⚙️ Oops, parece que há algum erro de estrutura no seu comando. Exemplo: /remove @user ID quantidade.")
                return
        else:
            destinatário = msg.reply_to_message.from_user.id
            username = msg.reply_to_message.from_user.username

            if username == msg.from_user.username:
                await msg.reply("⚙️ Oops, você não pode remover frutinhas da sua própria cestinha.")
                return

            if len(remove) == 3:
                try:
                    id = int(remove[1])
                    quantidade = int(remove[2])
                except ValueError:
                    await msg.reply("⚙️ Oops, parece que você ofereceu uma quantidade ou ID inválido.")
                    return
            else:
                await msg.reply("⚙️ Oops, parece que há algum erro de estrutura no seu comando. Tente quotar uma mensagem usando o seguinte comando: /presentear ID quantidade.")
                return

        adm = msg.from_user.username

        if await exist_card(id, msg):
            async with get_cursor() as cursor:
                Ncards = await carta_user(destinatário, id, cursor)

                if Ncards:
                    resto = Ncards - quantidade

                    match resto:
                        case _ if resto <= 0:
                            quantidade = Ncards
                            await cursor.execute("DELETE FROM inventario WHERE id_user = %s AND id_carta = %s",(destinatário, id,))
                        case _:
                            await cursor.execute("UPDATE inventario SET quantidade = %s WHERE id_user = %s AND id_carta = %s", (resto, destinatário, id,))
                else:
                    await msg.reply(f"⚙️ Oops, @{username} não possui a frutinha que você está tentando remover.")
                    return
                await cursor.execute("INSERT INTO gerencia (adm, operaçao, destinatario, quantidade, card) VALUES(%s, %s, %s, %s, %s)", (adm, "remover", destinatário, quantidade, id,))

                if quantidade > 1:
                    await msg.reply(f"Você removeu da cestinha de @{username} {quantidade} frutinhas `{id}`! 🍎")
                else:
                    await msg.reply(f"Você removeu da cestinha de @{username} {quantidade} frutinha `{id}`! 🍎")

# -------------------------------------------
# COMANDO PARA PREMIAR UM USUÁRIO COM GIROS

async def depositar(telegram_id, bot, msg):
    if await is_admin(telegram_id, msg):
        depositar = msg.text.split()

        if not msg.reply_to_message and len(depositar) == 3:
            try:
                quantidade = int(depositar[1])
                username = depositar[2].lstrip('@')

                if username == msg.from_user.username:
                    await msg.reply("⚙️ Oops, você não pode depositar colheitas para si mesmo.")
                    return

                async with get_cursor() as cursor:
                    await cursor.execute("SELECT telegram_id FROM usuarios WHERE username = %s", (username,))
                    user = await cursor.fetchone()

                    if user:
                        destinatário = int(user[0])
                    else:
                        await msg.reply("⚙️ Oops, parece que esse usuário não é um habitante da Vila Tutti-Frutti ou não está com o username atualizado. Para atualizar, basta usar qualquer comando!")
                        return
            except ValueError:
                await msg.reply("⚙️ Oops, parece que você ofereceu uma quantidade inválida.")
                return
            
        elif msg.reply_to_message and len(depositar) == 2:
            try:
                quantidade = int(depositar[1])
                destinatário = msg.reply_to_message.from_user.id
                username = msg.reply_to_message.from_user.username

                if username == msg.from_user.username:
                    await msg.reply("⚙️ Oops, você não pode depositar colheitas para si mesmo.")
                    return
                
                async with get_cursor() as cursor:
                    await cursor.execute("SELECT telegram_id FROM usuarios WHERE telegram_id = %s", (destinatário,))
                    user = await cursor.fetchone()
                
                if not user:
                    await msg.reply("⚙️ Oops, parece que esse usuário não é um habitante da Vila Tutti-Frutti.")
                    return
            except ValueError:
                await msg.reply("⚙️ Oops, parece que você ofereceu uma quantidade inválida.")
                return
        else:
            await msg.reply("⚙️ Oops, parece que há algum erro na estrutura do comando. Exemplo: /depositar quantidade @user.")
            return

        user = await bot.get_chat(telegram_id)
        adm = user.username

        async with get_cursor() as cursor:
            await cursor.execute("UPDATE usuarios SET giros = giros + %s WHERE telegram_id = %s", (quantidade, destinatário,))
            await cursor.execute("INSERT INTO gerencia (adm, operaçao, destinatario, quantidade) VALUES(%s, %s, %s, %s)", (adm, "depositar", destinatário, quantidade,))
        await msg.reply(f"O habitante @{username} conquistou {quantidade} novas plantações para colher! 🌿")

# -------------------------------------------
# COMANDO PARA PREMIAR TODOS OS USUÁRIOS COM GIROS

async def depositarall(telegram_id, bot, msg):
    if await is_admin(telegram_id, msg):
        depositar = msg.text.split()

        if len(depositar) == 2:
            try:
                quantidade = depositar[1]
                quantidade = int(quantidade)

                user = await bot.get_chat(telegram_id)
                adm = user.username

                async with get_cursor() as cursor:
                    await cursor.execute("UPDATE usuarios SET giros = giros + %s", (quantidade,))
                    await cursor.execute("INSERT INTO gerencia (adm, operaçao, destinatario, quantidade) VALUES(%s, %s, %s, %s)", (adm, "depositarall", 100, quantidade,))
            
                await msg.reply(f"Todos os habitantes da Vila Tutti-Frutti conquistaram {quantidade} novas plantações para colher! 🌿")
            except ValueError:
                await msg.reply("⚙️ Oops, parece que você ofereceu uma quantidade inválida.")
                return
        else:
            await msg.reply("⚙️ Oops, parece que há algum erro de estrutura no seu comando. Exemplo: /depositarall quantidade.")
            return
        
# -------------------------------------------
# COMANDO PARA VISUALIZAR TODAS AS ÚLTIMAS AÇÕES DE ADMS

async def regadm(telegram_id, msg):
    if await is_admin(telegram_id, msg):
        opcoes = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📌 DEPOSITAR", callback_data="regdepositar"),
                InlineKeyboardButton(text="📌 FERMENTAR", callback_data="regfermentar")
            ],
            [
                InlineKeyboardButton(text="📌 PRESENTEAR", callback_data="regpres"),
                InlineKeyboardButton(text="📌 RESET/DESBAN", callback_data="regresetdb")
            ]
        ])

        await msg.reply(f"🍁 Olá, ADM @{msg.from_user.username}! Informe qual registro de operações deseja consultar!", reply_markup=opcoes)

# -------------------------------------------
# COMANDO PARA VISUALIZAR VÍNCULOS DO HABITANTE

async def vinculos(telegram_id, msg):
    if await is_admin(telegram_id, msg):
        if not msg.reply_to_message:
            entrada = msg.text.split()

            if len(entrada) != 2:
                await msg.reply("⚙️ Oops, parece que há algo de errado com seu comando. Exemplo: /vínculos ID.")
                return
            else:
                async with get_cursor() as cursor:
                    try:
                        user = int(entrada[1])
                        await cursor.execute("SELECT telegram_id, username FROM usuarios WHERE id = %s", (user,))
                        tlid = await cursor.fetchone()
                    except ValueError:
                        user = entrada[1].lstrip('@')
                        await cursor.execute("SELECT telegram_id, username FROM usuarios WHERE username = %s", (user,))
                        tlid = await cursor.fetchone()
                    
                    if tlid:
                        await cursor.execute("SELECT laranja FROM laranjas WHERE matriz = %s", (tlid[0],))
                        laranjas = await cursor.fetchall()

                        if laranjas:
                            texto = f"🍊 Essas são as contas vinculadas de @{tlid[1]}:\n"
                            for laranja in laranjas:
                                await cursor.execute("SELECT username, giros, sementes FROM usuarios WHERE telegram_id = %s", (laranja,))
                                dados = await cursor.fetchone()

                                texto += f"\n🐛 @{dados[0]}\n🧃 Giros: {dados[1]}\n🌾 Sementes: {dados[2]}\n"
                            await msg.reply(texto)
                        else:
                            await msg.reply("⚙️ Oops, parece que esse habitante ainda não tem laranjas.")
                            return
                    else:
                        await msg.reply("⚙️ Oops, parece que essa pessoa não é habitante da Vila Tutti-Frutti.")
                        return
        else:
            tlid = msg.reply_to_message.from_user.id

            async with get_cursor() as cursor:
                await cursor.execute("SELECT laranja FROM laranjas WHERE matriz = %s", (tlid,))
                laranjas = await cursor.fetchall()

                if laranjas:
                    texto = f"🍊 Essas são as contas vinculadas de @{msg.reply_to_message.from_user.username}:\n"
                    for laranja in laranjas:
                        await cursor.execute("SELECT username, giros, sementes FROM usuarios WHERE telegram_id = %s", (laranja,))
                        dados = await cursor.fetchone()

                        texto += f"\n🐛 @{dados[0]}\n🧃 Giros: {dados[1]}\n🌾 Sementes: {dados[2]}\n"
                    await msg.reply(texto)
                else:
                    await msg.reply(f"⚙️ Oops, parece que @{msg.reply_to_message.from_user.username} ainda não tem nenhuma laranja.")

# -------------------------------------------
# COMANDO PARA DELETAR CARD OU SUB DO BOT

async def deletar(telegram_id, msg, bot):
    if await is_admin(telegram_id, msg):
        entrada = msg.text.split(' ', 1)
        try:
            card = int(entrada[1])
            result = await exist_card(card, msg)

            if result:
                async with get_cursor() as cursor:
                    match result[2]:
                        case 1:
                            sementes = 1000
                        case 2:
                            sementes = 500
                        case 3:
                            sementes = 250
                    
                    await cursor.execute("SELECT id_user, quantidade FROM inventario WHERE id_carta = %s", (card,))
                    users = await cursor.fetchall()

                    for user, quantidade in users:
                        recompensa = sementes * quantidade
                        await cursor.execute("UPDATE usuarios SET sementes = sementes + %s WHERE telegram_id = %s", (recompensa, user,))
                        await msg.reply(f"🍊 Frutinha `{card}` deletada com sucesso.")
                        await bot.send_message(user, f"🐦‍⬛ Poxa vida! Um corvo comeu todas as suas frutinhas `{card}`, você ganhou {recompensa} sementes.") 
                    await cursor.execute("DELETE FROM cartas WHERE id = %s", (card,))
                    await cursor.execute("UPDATE cartas SET id = id - 1 WHERE id > %s", (card,))
        except ValueError:
            sub = entrada[1]
            result = await exist_sub(sub, msg)

            if result:
                async with get_cursor() as cursor:
                    await cursor.execute("""
                    SELECT 
                        i.id_user,
                        SUM(
                            i.quantidade *
                            CASE c.raridade
                                WHEN 1 THEN 1000
                                WHEN 2 THEN 500
                                WHEN 3 THEN 250
                                ELSE 0
                            END
                        ) AS total_sementes
                    FROM cartas c
                    JOIN inventario i ON c.id = i.id_carta
                    WHERE c.subcategoria = %s
                        OR EXISTS (
                            SELECT 1
                            FROM multisub m
                            WHERE m.id = c.id AND m.subcategoria = %s
                        )
                    GROUP BY i.id_user
                    """, (result[1], result[1],))
                    users = await cursor.fetchall()
                        
                    if users:
                        for user, recompensa in users:
                            await cursor.execute("UPDATE usuarios SET sementes = sementes + %s WHERE telegram_id = %s", (recompensa, user,))
                            await msg.reply(f"🍊 Colheita {sub} deletada com sucesso.")
                            await bot.send_message(user, f"🐦‍⬛ Poxa vida! Um corvo comeu todas as frutinhas da sua coleção {result[1]}, você ganhou {recompensa} sementes.") 
                    
                    await cursor.execute("SELECT COUNT(*), MAX(id) FROM cartas WHERE subcategoria = %s", (sub,))
                    contagem = await cursor.fetchone()
                    await cursor.execute("DELETE FROM divisoes WHERE subcategoria = %s", (sub,))
                    await cursor.execute("UPDATE cartas SET id = id - %s WHERE id > %s", (contagem[0], contagem[1],))