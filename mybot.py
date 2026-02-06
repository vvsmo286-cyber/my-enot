import asyncio, random, os, json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web
from fractions import Fraction

TOKEN = '8164851577:AAGMU9nAceVgaRCp-xxAtlJHApz5KwjoiEI'
ADMIN_ID = "6032049080"

# --- RENDER FIX ---
async def handle(r): return web.Response(text="Mega Enot Ultimate + Mines is Live!")
async def start_web():
    app = web.Application(); app.router.add_get('/', handle)
    runner = web.AppRunner(app); await runner.setup()
    try: await web.TCPSite(runner, '0.0.0.0', 10000).start()
    except: pass

# --- DATA ---
user_data, mines_games = {}, {}
TITLES = {"редкие": ["Абобус", "Крутыш"], "легендарные": ["Босс 67"], "ультралегендарные": ["Тюлень 2.0"]}
JOBS = [
    {"name": "🧹 Дворник", "pay": 50, "goal": 70},
    {"name": "📦 Доставщик", "pay": 80, "goal": 140},
    {"name": "🪓 Лесоруб", "pay": 100, "goal": 500},
    {"name": "💻 Программист", "pay": 110, "goal": 210},
    {"name": "💰 Бизнесмен", "pay": 160, "goal": 9999}
]

def load_data():
    global user_data
    if os.path.exists("users.json"):
        try:
            with open("users.json", "r") as f: user_data = json.load(f)
        except: user_data = {}

def save_all():
    try:
        with open("users.json", "w") as f: json.dump(user_data, f)
    except: pass

def get_user(uid, name="Енотик"):
    uid = str(uid)
    if uid not in user_data:
        is_admin = (uid == ADMIN_ID)
        user_data[uid] = {'name': name, 'coins': 10000 if is_admin else 100, 'title': "Енот Полоскун" if is_admin else "🦴 Новичок", 'job_lvl': 0, 'work_count': 0, 'items': [], 'last_work': ''}
    if uid == ADMIN_ID:
        user_data[uid]['title'] = "Енот Полоскун"
        if user_data[uid].get('coins', 0) < 10000: user_data[uid]['coins'] = 10000
    return user_data[uid]

# --- КЛАВИАТУРЫ ---
def get_main_menu(uid):
    u = get_user(uid); b = InlineKeyboardBuilder()
    b.button(text="👤 Профиль", callback_data="open_profile")
    b.button(text="🛠 Работа", callback_data="go_work")
    b.button(text="🎮 Игры", callback_data="open_games")
    b.button(text="🛒 Магазин", callback_data="open_shop")
    b.button(text="🧮 Калькулятор", callback_data="st_calc")
    b.button(text="📦 Кейс (100💰)", callback_data="open_case")
    if str(uid) == ADMIN_ID: b.button(text="💎 VIP СКЛАД", callback_data="admin_shop")
    return b.adjust(1, 2, 2, 1, 1).as_markup()

def get_m_kb(uid, end=False):
    g = mines_games[uid]; b = InlineKeyboardBuilder()
    for i in range(49):
        t = "✅" if i in g['o'] else ("💣" if end and i in g['m'] else "⬜️")
        b.button(text=t, callback_data=f"m_{i}")
    b.button(text="🔙 Назад", callback_data="open_games")
    return b.adjust(7).as_markup()

# --- ЛОГИКА ---
async def main():
    load_data(); await start_web()
    bot = Bot(token=TOKEN); dp = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)

    @dp.message(lambda m: m.text and m.text.lower() in ["/start", "меню", "енот", "игры", "профиль"])
    async def cmd_start(m: types.Message):
        get_user(m.from_user.id, m.from_user.first_name); save_all()
        await m.answer(f"🦝 **Енот на чиле ULTIMATE** (Сапер вернулся!)", reply_markup=get_main_menu(m.from_user.id))

    @dp.callback_query(F.data == "open_games")
    async def games_m(c: types.CallbackQuery):
        b = InlineKeyboardBuilder().button(text="💣 Сапер", callback_data="st_mines").button(text="🎰 Слоты", callback_data="st_slots").button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("🎮 Выбери игру:", reply_markup=b.adjust(2, 1).as_markup())

    @dp.callback_query(F.data == "st_mines")
    async def mine_st(c: types.CallbackQuery):
        mines_games[c.from_user.id] = {'m': random.sample(range(49), 10), 'o': []}
        await c.message.edit_text("💣 Сапер 7x7 (нажми на клетку):", reply_markup=get_m_kb(c.from_user.id))

    @dp.callback_query(F.data.startswith("m_"))
    async def mine_pl(c: types.CallbackQuery):
        u = c.from_user.id; idx = int(c.data.split("_")); g = mines_games[u]
        if idx in g['m']: await c.message.edit_text("💥 БУМ! Ты подорвался.", reply_markup=get_m_kb(u, True))
        else:
            if idx not in g['o']: g['o'].append(idx); get_user(u)['coins'] += 5; save_all()
            await c.message.edit_reply_markup(reply_markup=get_m_kb(u))
        await c.answer()

    @dp.callback_query(F.data == "go_work")
    async def work_choice(c: types.CallbackQuery):
        u = get_user(c.from_user.id); b = InlineKeyboardBuilder()
        b.button(text=f"🏢 {JOBS[u['job_lvl']]['name']}", callback_data="work_normal")
        b.button(text="🤫 Контрабанда", callback_data="work_smuggle")
        b.button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("Выбери путь:", reply_markup=b.adjust(1).as_markup())

    @dp.callback_query(F.data == "work_normal")
    async def work_normal(c: types.CallbackQuery):
        u = get_user(c.from_user.id); job = JOBS[u['job_lvl']]
        multi = 2.0 if "Корона" in u['items'] else (1.4 if u['title'] == "Тюлень 2.0" else 1.0)
        pay = int(job['pay'] * multi)
        u['coins'] += pay; u['work_count'] += 1
        if u['work_count'] >= job['goal'] and u['job_lvl'] < 4: u['job_lvl'] += 1; u['work_count'] = 0
        save_all(); await c.answer(f"+{pay}💰"); await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "work_smuggle")
    async def smug(c: types.CallbackQuery):
        u = get_user(c.from_user.id); b = InlineKeyboardBuilder(); sw = random.choice(["Лес", "Мост", "Тоннель"])
        hint = f"\n💡 Очки шепчут: {sw}" if "Очки" in u['items'] else ""
        for w in ["Лес", "Мост", "Тоннель"]: b.button(text=w, callback_data=f"sm_{w}_{sw}")
        await c.message.edit_text(f"📦 Путь:{hint}", reply_markup=b.adjust(1).as_markup())

    @dp.callback_query(F.data.startswith("sm_"))
    async def smug_res(c: types.CallbackQuery):
        u = get_user(c.from_user.id); d = c.data.split("_")
        if d == d: u['coins'] += 300; m = "✅ +300"
        else: u['coins'] -= 100; m = "💢 -100"
        save_all(); await c.answer(m, show_alert=True); await c.message.edit_text(m, reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "admin_shop")
    async def admin(c: types.CallbackQuery):
        if str(c.from_user.id) != ADMIN_ID: return
        b = InlineKeyboardBuilder().button(text="🧼 Тазик (10к)", callback_data="buy_тазик").button(text="👓 Очки (5к)", callback_data="buy_очки").button(text="👑 Корона (25к)", callback_data="buy_корона").button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("💎 VIP:", reply_markup=b.adjust(1).as_markup())

    @dp.callback_query(F.data.startswith("buy_"))
    async def buy(c: types.CallbackQuery):
        u = get_user(c.from_user.id); item = c.data.split("_"); p = {"корона": 25000, "очки": 5000, "тазик": 10000}
        if u['coins'] < p.get(item, 0): return await c.answer("Мало монет!", show_alert=True)
        u['coins'] -= p.get(item, 0); u['items'].append(item.capitalize()); save_all()
        await c.answer("Куплено!"); await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "to_menu")
    async def to_m(c: types.CallbackQuery): await c.message.edit_text("🦝 Меню:", reply_markup=get_main_menu(c.from_user.id))

    print("🚀 ЕНОТ ULTIMATE + САПЕР ГОТОВ!"); await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())


