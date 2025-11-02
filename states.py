from aiogram.fsm.state import State, StatesGroup

em_troca = {}

class Csub(StatesGroup):
    nome = State()
    foto = State()
    confirm = State()

class Esub(StatesGroup):
    sub = State()
    foto = State()
    nome = State()
    addvar = State()
    removevar = State()

class Ctag(StatesGroup):
    nome = State()
    ids = State()
    foto = State()
    salvar = State()

class Etag(StatesGroup):
    tag = State()
    foto = State()
    nome = State()

class Atag(StatesGroup):
    tag = State()
    ids = State()

class Rtag(StatesGroup):
    tag = State()
    ids = State()

class Ccard(StatesGroup):
    sub = State()
    nome = State()
    rare = State()
    confirm = State()
    salvar = State()

class Ecard(StatesGroup):
    card = State()
    nome = State()
    img = State()
    sub = State()
    rare = State()
    multisub = State()

class Loja(StatesGroup):
    giros = State()
    vip = State()
    divorcio = State()
    caixinha = State()

class Receita(StatesGroup):
    settings = State()