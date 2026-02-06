import asyncio, random, os, json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web
from fractions import Fraction

TOKEN = '8164851577:AAGMU9nAceVgaRCp-xxAtlJHApz5KwjoiEI'
ADMIN_ID = "6032049080"

# --- СЕРВЕР RENDER ---
async def handle(r): return web.Response(text="Enot Ultimate Active")
async def start_web():
    app = web.Application(); app.router.add_get('/', handle)
    runner = web.AppRunner(app); await runner.setup()
    try: await web.TCPSite(runner, '0.0.0.0', 10000).start()
    except: pass

# --- ДАННЫЕ ---
user_data, mines_games, games_2048 = {}, {}, {}
TITLES = {"редкие": ["Абобус", "Крутыш"], "ультралегендарные": ["Тюлень 2.0"]}
JOBS = [
    {"name": "🧹 Дворник", "pay": 50, "goal": 70},
    {"name": "📦 Доставщик", "pay": 80, "goal": 140},
    {"name": "🪓 Лесоруб", "pay": 100, "goal": 500},
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
        if user_data[uid]['coins'] < 10000: user_data[uid]['coins'] = 10000
    return user_data[uid]

def get_main_menu(uid):
    u = get_user(uid); b = InlineKeyboardBuilder()
    b.button(text="👤 Профиль", callback_data="open_profile")
    b.button(text="🛠 Работа", callback_data="go_work")
    b.button(text="🎮 Игры", callback_data="open_games")
    b.button(text="🛒 Магазин", callback_data="open_shop")
    b.button(text="🧮 Калькулятор", callback_data="st_calc")
    if str(uid) == ADMIN_ID: b.button(text="💎 VIP СКЛАД", callback_data="admin_shop")
    return b.adjust(1, 2, 2, 1).as_markup()

# --- САПЕР КЛАВА ---
def get_m_kb(uid, end=False):
    g = mines_games[uid]; b = InlineKeyboardBuilder()
    for i in range(49):
        t = "✅" if i in g['o'] else ("💣" if end and i in g['m'] else "⬜️")
        b.button(text=t, callback_data=f"m_{i}")
    b.button(text="🔙 Назад", callback_data="open_games")
    return b.adjust(7).as_markup()

async def main():
    load_data(); await start_web()
    bot = Bot(token=TOKEN); dp = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)

    @dp.message(lambda m: m.text and m.text.lower() in ["/start", "меню", "енот", "игры"])
    async def cmd_start(m: types.Message):
        get_user(m.from_user.id, m.from_user.first_name); save_all()
        await m.answer(f"🦝 **Енот на чиле ULTIMATE** запущен!", reply_markup=get_main_menu(m.from_user.id))

    @dp.callback_query(F.data == "go_work")
    async def work(c: types.CallbackQuery):
        u = get_user(c.from_user.id); now = datetime.now()
        if u.get('last_work'):
            diff = now - datetime.strptime(u['last_work'], "%H:%M:%S")
            if diff < timedelta(seconds=30) and "Компотик" not in u['items']:
                return await c.answer("Подожди 30 сек!", show_alert=True)
        if "Компотик" in u['items']: u['items'].remove("Компотик")
        job = JOBS[u['job_lvl']]
        bonus = (15 if "Мех. перчатки" in u['items'] else 0) + (40 if "Велосипед" in u['items'] else 0) + (150 if "Рюкзак" in u['items'] else 0)
        pay = int((job['pay'] + bonus) * (2.0 if "Корона" in u['items'] else 1.0))
        u['coins'] += pay; u['work_count'] += 1; u['last_work'] = now.strftime("%H:%M:%S")
        if u['work_count'] >= job['goal'] and u['job_lvl'] < 3: u['job_lvl'] += 1; u['work_count'] = 0
        save_all(); await c.answer(f"+{pay}💰"); await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "open_games")
    async def games(c: types.CallbackQuery):
        b = InlineKeyboardBuilder()
        b.button(text="💣 Сапер", callback_data="st_mines")
        b.button(text="🎰 Слоты", callback_data="st_slots")
        b.button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("🎮 Игры:", reply_markup=b.adjust(2, 1).as_markup())

    @dp.callback_query(F.data == "st_mines")
    async def mine_st(c: types.CallbackQuery):
        mines_games[c.from_user.id] = {'m': random.sample(range(49), 10), 'o': []}
        await c.message.edit_text("💣 Сапер 7x7:", reply_markup=get_m_kb(c.from_user.id))

    @dp.callback_query(F.data.startswith("m_"))
    async def mine_pl(c: types.CallbackQuery):
        u = c.from_user.id; idx = int(c.data.split("_")); g = mines_games[u]
        if idx in g['m']: await c.message.edit_text("💥 БУМ!", reply_markup=get_m_kb(u, True))
        else:
            if idx not in g['o']: g['o'].append(idx); get_user(u)['coins'] += 5
            await c.message.edit_reply_markup(reply_markup=get_m_kb(u))
        await c.answer()

    @dp.callback_query(F.data == "open_shop")
    async def shop(c: types.CallbackQuery):
        b = InlineKeyboardBuilder()
        b.button(text="🧤 Мех. перчатки (500)", callback_data="buy_перчатки")
        b.button(text="🚲 Велосипед (1350)", callback_data="buy_велосипед")
        b.button(text="🧃 Компотик (130)", callback_data="buy_компотик")
        b.button(text="🎒 Рюкзак (6000)", callback_data="buy_рюкзак")
        b.button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("🛒 МАГАЗИН:", reply_markup=b.adjust(1).as_markup())

    @dp.callback_query(F.data.startswith("buy_"))
    async def buying(c: types.CallbackQuery):
        u = get_user(c.from_user.id); item = c.data.split("_")
        p = {"перчатки": 500, "велосипед": 1350, "компотик": 130, "рюкзак": 6000, "тазик": 10000, "очки": 5000, "корона": 25000}
        it_name = item.capitalize()
        if u['coins'] < p[item]: return await c.answer("Мало монет!", show_alert=True)
        u['coins'] -= p[item]; u['items'].append(it_name); save_all()
        await c.answer("Куплено!"); await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "open_profile")
    async def profile(c: types.CallbackQuery):
        u = get_user(c.from_user.id); job = JOBS[u['job_lvl']]; items_str = ", ".join(u['items']) if u['items'] else "Пусто"
        res = f"👤 **ПРОФИЛЬ**\n🏆 Титул: {u['title']}\n💰 Баланс: {u['coins']}\n🛠 Работа: {job['name']}\n📈 Смены: {u['work_count']}/{job['goal']}\n🎒 Вещи: {items_str}"
        await c.message.edit_text(res, reply_markup=InlineKeyboardBuilder().button(text="🔙 Назад", callback_data="to_menu").as_markup())

    @dp.callback_query(F.data == "admin_shop")
    async def admin(c: types.CallbackQuery):
        if str(c.from_user.id) != ADMIN_ID: return
        b = InlineKeyboardBuilder().button(text="🧼 Тазик (10к)", callback_data="buy_тазик").button(text="👓 Очки (5к)", callback_data="buy_очки").button(text="👑 Корона (25к)", callback_data="buy_корона").button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("💎 VIP СКЛАД:", reply_markup=b.adjust(1).as_markup())

    @dp.callback_query(F.data == "st_calc")
    async def calc(c: types.CallbackQuery): await c.answer("🔢 Пиши пример в чат (2+2 или 1/2+1/2)", show_alert=True)

    @dp.message(F.text.regexp(r"^(\d+[\+\-\*\/]\d+)$"))
    async def s_calc(m: types.Message):
        try: await m.answer(f"🧩 Ответ: {eval(m.text)}")
        except: pass

    @dp.message(F.text.regexp(r"^(\d+\/\d+[\+\-\*\/]\d+\/\d+)$"))
    async def f_calc(m: types.Message):
        try:
            t = m.text.replace(" ", ""); op = next(o for o in "+-*/" if o in t)
            p = t.split(op); f1, f2 = Fraction(p), Fraction(p)
            if op == "+": r = f1 + f2
            elif op == "-": r = f1 - f2
            elif op == "*": r = f1 * f2
            elif op == "/": r = f1 / f2
            await m.answer(f"🍰 Результат: {r}")
        except: pass

    @dp.callback_query(F.data == "to_menu")
    async def back(c: types.CallbackQuery): await c.message.edit_text("🦝 Меню:", reply_markup=get_main_menu(c.from_user.id))

    print("🚀 ЕНОТ ULTIMATE ЗАПУЩЕН!"); await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())

