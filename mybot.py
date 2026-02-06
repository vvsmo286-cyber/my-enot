import asyncio
import random
import os
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# Твой токен напрямую
TOKEN = '8164851577:AAGMU9nAceVgaRCp-xxAtlJHApz5KwjoiEI'

# --- ФИКС ДЛЯ RENDER (ВЕБ-СЕРВЕР ЧТОБЫ НЕ ВЫЛЕТАЛО) ---
async def handle(request):
    return web.Response(text="Mega Enot Economy is Live!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 10000).start()

# --- ЭКОНОМИКА И ДАННЫЕ ---
user_data = {}
mines_games = {}
games_2048 = {}
TITLES = {
    "🥉 Новичок": 1.0,
    "🥈 Ворюга": 1.5,
    "🥇 Мастер": 2.5,
    "💎 Мега-Енот": 5.0,
    "🔥 ЛЕГЕНДА": 10.0
}

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
        user_data[uid] = {'coins': 150, 'title': "🥉 Новичок", 'multi': 1.0, 'upg_price': 200, 'last_bonus': ''}
    return user_data[uid]

# --- ГЛАВНОЕ МЕНЮ ---
def get_main_menu(uid):
    u = get_user(uid)
    b = InlineKeyboardBuilder()
    total_multi = round(TITLES[u['title']] * u['multi'], 1)
    b.row(types.InlineKeyboardButton(text=f"{u['title']} | Множитель: x{total_multi}", callback_data="none"))
    b.row(types.InlineKeyboardButton(text=f"💰 Баланс: {int(u['coins'])}", callback_data="none"))
    b.button(text="💣 Сапер", callback_data="st_mines")
    b.button(text="🔢 2048", callback_data="st_2048")
    b.button(text="🎰 Слоты", callback_data="st_slots")
    b.button(text=f"⚡️ Усиление ({u['upg_price']}💰)", callback_data="buy_upg")
    b.button(text="📦 Кейс Титулов (300💰)", callback_data="open_case")
    b.button(text="🎁 БОНУС", callback_data="get_bonus")
    b.adjust(1, 1, 3, 1, 1, 1); return b.as_markup()

# --- ЛОГИКА 2048 (РАЗВЕРНУТАЯ) ---
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
            res = compress_2048(l); nw.append(res if d == 'left' else res[::-1])
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

# --- СТАРТ ---
async def main():
    load_data()
    await start_web_server()
    bot = Bot(token=TOKEN); dp = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)

    @dp.message(F.text.lower().in_(["/start", "меню", "игры"]))
    async def menu(m: types.Message):
        await m.answer(f"🦝 Мега-Енот: Экономика от Компотика!\nПокупай усиления и выбивай титулы!", reply_markup=get_main_menu(m.from_user.id))

    # --- ПОКУПКА УСИЛЕНИЙ ---
    @dp.callback_query(F.data == "buy_upg")
    async def buy_upg(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        if u['coins'] < u['upg_price']: return await c.answer("Не хватает монет! ❌", show_alert=True)
        u['coins'] -= u['upg_price']
        u['multi'] = round(u['multi'] + 0.2, 1)
        u['upg_price'] = int(u['upg_price'] * 1.6)
        save_data()
        await c.answer(f"⚡️ Множитель прокачан до x{u['multi']}!", show_alert=True)
        await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    # --- КЕЙСЫ ---
    @dp.callback_query(F.data == "open_case")
    async def open_case(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        if u['coins'] < 300: return await c.answer("Кейс стоит 300💰", show_alert=True)
        u['coins'] -= 300
        new_t = random.choices(list(TITLES.keys()), weights=[50, 30, 15, 4, 1])[0]
        u['title'] = new_t
        save_data()
        await c.message.answer(f"📦 БА-БАХ! Твой новый титул: {new_t}!\nМножитель звания: x{TITLES[new_t]}", reply_markup=get_main_menu(c.from_user.id))

    # --- ИГРЫ ---
    @dp.callback_query(F.data == "st_slots")
    async def slots(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        if u['coins'] < 20: return await c.answer("Ставка 20💰", show_alert=True)
        u['coins'] -= 20; await c.answer("🎰 Крутим!")
        m = await c.message.answer_dice(emoji="🎰")
        await asyncio.sleep(3.5)
        total_m = u['multi'] * TITLES[u['title']]
        if m.dice.value in [1, 22, 43, 64]:
            win = int(400 * total_m)
            u['coins'] += win; await c.message.answer(f"💎 ДЖЕКПОТ! +{win}💰")
        else: await c.message.answer("❌ Пусто...")
        save_data(); await c.message.answer("Меню:", reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "st_mines")
    async def mine_st(c: types.CallbackQuery):
        mines_games[c.from_user.id] = {'m': random.sample(range(49), 10), 'o': []}
        await c.message.edit_text("💣 Сапер 7x7 (Каждое поле +монеты):", reply_markup=get_m_kb(c.from_user.id))

    @dp.callback_query(F.data.startswith("m_"))
    async def mine_pl(c: types.CallbackQuery):
        u = c.from_user.id; idx = int(c.data.split("_")[1]); g = mines_games[u]
        if idx in g['m']:
            await c.message.edit_text("💥 БУМ! Ты подорвался.", reply_markup=get_m_kb(u, True))
        else:
            if idx not in g['o']:
                g['o'].append(idx)
                multi = get_user(u)['multi'] * TITLES[get_user(u)['title']]
                get_user(u)['coins'] += int(5 * multi)
            await c.message.edit_reply_markup(reply_markup=get_m_kb(u))
        await c.answer()

    @dp.callback_query(F.data == "st_2048")
    async def s_2048(c: types.CallbackQuery):
        games_2048[c.from_user.id] = init_2048()
        await c.message.edit_text("🔢 2048:", reply_markup=get_2048_kb(c.from_user.id))

    @dp.callback_query(F.data.startswith("mv_"))
    async def mv_2048(c: types.CallbackQuery):
        uid = c.from_user.id; d = c.data.split("_")[1]
        old = [r[:] for r in games_2048[uid]]; new = move_2048(old, d)
        if new != old: add_tile_2048(new); games_2048[uid] = new
        await c.message.edit_reply_markup(reply_markup=get_2048_kb(uid)); await c.answer()

    @dp.callback_query(F.data == "get_bonus")
    async def bonus(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        day = datetime.now().strftime("%Y-%m-%d")
        if u.get('last_bonus') == day: return await c.answer("Жди завтра! 🍪", show_alert=True)
        bonus_val = int(100 * (u['multi'] * TITLES[u['title']]))
        u['coins'] += bonus_val; u['last_bonus'] = day; save_data()
        await c.answer(f"🎁 Бонус: {bonus_val}💰", show_alert=True)
        await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "to_menu")
    async def to_m(c: types.CallbackQuery):
        await c.answer(); save_data()
        await c.message.edit_text("🎮 Главное меню:", reply_markup=get_main_menu(c.from_user.id))

    print("🚀 МЕГА-ЕНОТ: ЭКОНОМИКА КОМПОТИКА ЗАПУЩЕНА")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

