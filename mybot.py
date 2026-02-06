import asyncio
import random
import os
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Твой токен напрямую
TOKEN = '8164851577:AAGMU9nAceVgaRCp-xxAtlJHApz5KwjoiEI'

# --- ПАМЯТЬ ЕНОТА ---
user_data = {}
mines_games = {}
games_2048 = {}

def load_data():
    global user_data
    if os.path.exists("users.json"):
        try:
            with open("users.json", "r") as f: user_data = json.load(f)
        except: user_data = {}

def save_data():
    with open("users.json", "w") as f: json.dump(user_data, f)

def get_user(uid):
    uid = str(uid)
    if uid not in user_data:
        user_data[uid] = {'coins': 100, 'last_bonus': '', 'wins': 0}
    return user_data[uid]

def get_status(coins):
    if coins < 300: return "🦝 Помоечный Енот"
    if coins < 1500: return "🎩 Енот в законе"
    if coins < 5000: return "👑 Король Печенек"
    return "💎 МЕГА-ЕНОТ"

# --- КЛАВИАТУРЫ ---
def get_main_menu(uid):
    u = get_user(uid)
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text=f"{get_status(u['coins'])} | {u['coins']}💰", callback_data="none"))
    b.button(text="💣 Сапер 7x7", callback_data="st_mines")
    b.button(text="🔢 2048", callback_data="st_2048")
    b.button(text="✊ Камень-Ножницы", callback_data="st_rsp")
    b.button(text="🎰 Слоты 777", callback_data="st_slots")
    b.button(text="🎲 Кубики", callback_data="st_dice")
    b.button(text="🎁 БОНУС", callback_data="get_bonus")
    b.button(text="📊 МОЯ ИНФО", callback_data="my_info")
    b.adjust(1, 2, 2, 2, 1); return b.as_markup()

# --- ЛОГИКА 2048 ---
def init_2048():
    g = [[0]*4 for _ in range(4)]
    for _ in range(2): add_tile_2048(g)
    return g

def add_tile_2048(g):
    empty = [(r, c) for r in range(4) for c in range(4) if g[r][c] == 0]
    if empty: r, c = random.choice(empty); g[r][c] = 2 if random.random() < 0.9 else 4

def compress_2048(row):
    n = [i for i in row if i != 0]
    for i in range(len(n)-1):
        if n[i] == n[i+1]: n[i]*=2; n[i+1]=0
    res = [i for i in n if i != 0]
    return res + [0]*(4-len(res))

def move_2048(g, d):
    nw = []
    if d in ['left', 'right']:
        for r in g:
            l = r if d == 'left' else r[::-1]
            res = compress_2048(l)
            nw.append(res if d == 'left' else res[::-1])
    else:
        nw = [[0]*4 for _ in range(4)]
        for c in range(4):
            col = [g[r][c] for r in range(4)]
            res = compress_2048(col if d == 'up' else col[::-1])
            res = res if d == 'up' else res[::-1]
            for r in range(4): nw[r][c] = res[r]
    return nw

def get_2048_kb(uid):
    g = games_2048[uid]
    b = InlineKeyboardBuilder()
    for row in g:
        for v in row: b.button(text=str(v) if v != 0 else "·", callback_data="none")
    b.row(types.InlineKeyboardButton(text="⬆️", callback_data="mv_up"),
          types.InlineKeyboardButton(text="⬅️", callback_data="mv_left"), 
          types.InlineKeyboardButton(text="➡️", callback_data="mv_right"),
          types.InlineKeyboardButton(text="⬇️", callback_data="mv_down"))
    b.button(text="🔙 Меню", callback_data="to_menu")
    b.adjust(4, 4, 4, 4, 4, 1); return b.as_markup()

# --- САПЕР ---
def get_m_kb(uid, end=False):
    g = mines_games[uid]
    b = InlineKeyboardBuilder()
    for i in range(49):
        t = "✅" if i in g['o'] else ("💣" if end and i in g['m'] else "⬜️")
        b.button(text=t, callback_data=f"m_{i}")
    b.button(text="🔙 Меню", callback_data="to_menu")
    b.adjust(7); return b.as_markup()

# --- ОСНОВНОЙ ЦИКЛ ---
async def main():
    load_data()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)

    @dp.message(F.text.lower().in_(["/start", "меню", "игры", "енот"]))
    async def open_menu(m: types.Message):
        await m.answer(f"🐾 Мега-Енот приветствует, {m.from_user.first_name}!", reply_markup=get_main_menu(m.from_user.id))

    @dp.callback_query(F.data == "get_bonus")
    async def b_cb(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        day = datetime.now().strftime("%Y-%m-%d")
        if u.get('last_bonus') == day: await c.answer("🍪 Только раз в день!", show_alert=True)
        else:
            u['coins'] += 50; u['last_bonus'] = day; save_data()
            await c.answer("🐾 Получено 50💰!", show_alert=True)
            await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "my_info")
    async def i_cb(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        await c.answer(f"📊 ДОСЬЕ: {get_status(u['coins'])}\nМонеты: {u['coins']}💰", show_alert=True)

    @dp.callback_query(F.data == "to_menu")
    async def to_m(c: types.CallbackQuery):
        await c.answer(); save_data()
        await c.message.edit_text("🎮 Главное меню Мега-Енота:", reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "st_slots")
    async def slot_pl(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        if u['coins'] < 20: return await c.answer("Нужно 20💰", show_alert=True)
        await c.answer("🎰 Погнали!"); u['coins'] -= 20
        m = await c.message.answer_dice(emoji="🎰")
        await asyncio.sleep(3.5)
        if m.dice.value in [1, 22, 43, 64]:
            u['coins'] += 250; await c.message.answer("💎 ДЖЕКПОТ! +250💰")
        else: await c.message.answer("❌ Пусто...")
        save_data(); await c.message.answer("Играем дальше?", reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "st_mines")
    async def mine_st(c: types.CallbackQuery):
        await c.answer()
        mines_games[c.from_user.id] = {'m': random.sample(range(49), 10), 'o': []}
        await c.message.edit_text("💣 Сапер 7x7:", reply_markup=get_m_kb(c.from_user.id))

    @dp.callback_query(F.data.startswith("m_"))
    async def mine_pl(c: types.CallbackQuery):
        u = c.from_user.id; idx = int(c.data.split("_")[1]); g = mines_games[u]
        if idx in g['m']:
            await c.answer("💥 БУМ!", show_alert=True)
            await c.message.edit_text("💀 Ты проиграл!", reply_markup=get_m_kb(u, True))
        else:
            await c.answer()
            if idx not in g['o']: g['o'].append(idx); get_user(u)['coins'] += 2
            await c.message.edit_reply_markup(reply_markup=get_m_kb(u))

    @dp.callback_query(F.data == "st_2048")
    async def s_2048(c: types.CallbackQuery):
        await c.answer()
        games_2048[c.from_user.id] = init_2048()
        await c.message.edit_text("🔢 Собери 2048:", reply_markup=get_2048_kb(c.from_user.id))

    @dp.callback_query(F.data.startswith("mv_"))
    async def mv_2048(c: types.CallbackQuery):
        uid = c.from_user.id
        if uid not in games_2048: return await c.answer("Начни игру заново!")
        d = c.data.split("_")[1]
        old = [r[:] for r in games_2048[uid]]
        new = move_2048(old, d)
        if new != old:
            add_tile_2048(new); games_2048[uid] = new
            await c.message.edit_reply_markup(reply_markup=get_2048_kb(uid))
        await c.answer()

    print("🚀 МЕГА-ЕНОТ С ТВОИМ ТОКЕНОМ ЗАПУЩЕН")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
