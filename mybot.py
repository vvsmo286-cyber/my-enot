import asyncio, random, os, json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

TOKEN = '8164851577:AAGMU9nAceVgaRCp-xxAtlJHApz5KwjoiEI'
ADMIN_ID = "6032049080" 

# --- ФИКС ДЛЯ RENDER ---
async def handle(r): return web.Response(text="Enot na Chile is Gaming...")
async def start_web():
    app = web.Application(); app.router.add_get('/', handle)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 10000).start()

# --- ДАННЫЕ ---
user_data, mines_games, games_2048 = {}, {}, {}
server_stats = {"total_earned": 0, "tax_pool": 0}

TITLES = {
    "редкие": ["Енот пляжный", "Абобус", "Крутыш", "Зарядник"],
    "сверхредкие": ["Стив", "Мишка Фредди", "Игроман", "Школьник читер666"],
    "мифические": ["Перкусрак", "Роблоксиан", "Майнкрафтер", "Бизнес енот", "Студент читер 777"],
    "легендарные": ["Енот Бармен", "Ручка Без башни", "Легомен", "Босс 67"],
    "ультралегендарные": ["Енот шлепа", "Тюлень", "Тюлень 2.0"]
}

JOBS = [
    {"name": "🧹 Дворник", "pay": 50, "goal": 70},
    {"name": "📦 Доставщик", "pay": 80, "goal": 140},
    {"name": "💻 Программист", "pay": 110, "goal": 210},
    {"name": "💰 Бизнесмен", "pay": 160, "goal": 9999}
]

def load_data():
    global user_data, server_stats
    if os.path.exists("users.json"):
        with open("users.json", "r") as f: user_data = json.load(f)
    if os.path.exists("stats.json"):
        with open("stats.json", "r") as f: server_stats = json.load(f)

def save_all():
    with open("users.json", "w") as f: json.dump(user_data, f)
    with open("stats.json", "w") as f: json.dump(server_stats, f)

def get_user(uid):
    uid = str(uid)
    if uid not in user_data:
        is_admin = (uid == ADMIN_ID)
        user_data[uid] = {
            'coins': 10000 if is_admin else 100,
            'title': "Енот Полоскун" if is_admin else "🦴 Новичок",
            'job_lvl': 0, 'work_count': 0, 'last_work': '',
            'items': [], 'multi': 1.0
        }
    return user_data[uid]

# --- КЛАВИАТУРЫ ---
def get_main_menu(uid):
    u = get_user(uid); b = InlineKeyboardBuilder()
    multi = 1.4 if u['title'] == "Тюлень 2.0" else (2.0 if "Корона" in u['items'] else 1.0)
    b.row(types.InlineKeyboardButton(text=f"👤 {u['title']} | x{multi}", callback_data="none"))
    b.row(types.InlineKeyboardButton(text=f"💰 Баланс: {int(u['coins'])}", callback_data="none"))
    b.button(text="🛠 Работа", callback_data="go_work")
    b.button(text="🎮 Игры", callback_data="open_games")
    b.button(text="🛒 Магазин", callback_data="open_shop")
    b.button(text="📦 Кейс (100)", callback_data="open_case")
    b.button(text="📊 Статистика", callback_data="server_stats")
    if str(uid) == ADMIN_ID: b.button(text="💎 VIP СКЛАД", callback_data="admin_shop")
    b.adjust(1, 1, 2, 2, 1); return b.as_markup()

# --- ЛОГИКА ---
async def main():
    load_data(); await start_web()
    bot = Bot(token=TOKEN); dp = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)

    @dp.message(F.text.lower().in_(["меню", "игры", "/start", "енот"]))
    async def start(m: types.Message):
        await m.answer(f"🦝 **Енот на чиле** приветствует тебя!", reply_markup=get_main_menu(m.from_user.id))

    # --- ИГРОВОЕ МЕНЮ ---
    @dp.callback_query(F.data == "open_games")
    async def games_menu(c: types.CallbackQuery):
        b = InlineKeyboardBuilder()
        b.button(text="💣 Сапер", callback_data="st_mines")
        b.button(text="🎰 Слоты", callback_data="st_slots")
        b.button(text="🎲 Кубики", callback_data="st_dice")
        b.button(text="🔢 2048", callback_data="st_2048")
        b.button(text="🔙 Назад", callback_data="to_menu")
        b.adjust(2, 2, 1); await c.message.edit_text("🎮 Выбери игру на чиле:", reply_markup=b.as_markup())

    # --- САПЕР ---
    def get_m_kb(uid, end=False):
        g = mines_games[uid]; b = InlineKeyboardBuilder()
        for i in range(49):
            t = "✅" if i in g['o'] else ("💣" if end and i in g['m'] else "⬜️")
            b.button(text=t, callback_data=f"m_{i}")
        b.button(text="🔙 Меню", callback_data="to_menu")
        b.adjust(7); return b.as_markup()

    @dp.callback_query(F.data == "st_mines")
    async def mine_st(c: types.CallbackQuery):
        mines_games[c.from_user.id] = {'m': random.sample(range(49), 10), 'o': []}
        await c.message.edit_text("💣 Сапер 7x7 (5💰 за клетку * множитель):", reply_markup=get_m_kb(c.from_user.id))

    @dp.callback_query(F.data.startswith("m_"))
    async def mine_pl(c: types.CallbackQuery):
        u = c.from_user.id; idx = int(c.data.split("_")[1]); g = mines_games[u]
        if idx in g['m']: await c.message.edit_text("💥 БУМ!", reply_markup=get_m_kb(u, True))
        else:
            if idx not in g['o']: 
                g['o'].append(idx); us = get_user(u)
                multi = 1.4 if us['title'] == "Тюлень 2.0" else (2.0 if "Корона" in us['items'] else 1.0)
                us['coins'] += int(5 * multi)
            await c.message.edit_reply_markup(reply_markup=get_m_kb(u))
        await c.answer()

    # --- РАБОТА И ОСТАЛЬНОЕ ---
    @dp.callback_query(F.data == "go_work")
    async def work(c: types.CallbackQuery):
        u = get_user(c.from_user.id); now = datetime.now()
        if u.get('last_work'):
            diff = now - datetime.strptime(u['last_work'], "%H:%M:%S")
            if diff < timedelta(seconds=30) and "Компотик" not in u['items']:
                return await c.answer("Чильни 30 сек! 🍹", show_alert=True)
        if "Компотик" in u['items']: u['items'].remove("Компотик")
        job = JOBS[u['job_lvl']]; bonus = (15 if "Перчатки" in u['items'] else 0) + (40 if "Велосипед" in u['items'] else 0) + (150 if "Рюкзак" in u['items'] else 0)
        multi = 1.4 if u['title'] == "Тюлень 2.0" else (2.0 if "Корона" in u['items'] else 1.0)
        pay = int((job['pay'] + bonus) * multi)
        u['coins'] += pay; u['work_count'] += 1; u['last_work'] = now.strftime("%H:%M:%S")
        server_stats['total_earned'] += pay
        if u['work_count'] >= job['goal'] and u['job_lvl'] < 3: u['job_lvl'] += 1; u['work_count'] = 0
        save_all(); await c.answer(f"+{pay}💰"); await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "open_shop")
    async def shop_menu(c: types.CallbackQuery):
        b = InlineKeyboardBuilder()
        b.button(text="🧤 Перчатки (500)", callback_data="buy_перчатки")
        b.button(text="🚲 Велик (1350)", callback_data="buy_велосипед")
        b.button(text="🧃 Компотик (130)", callback_data="buy_компотик")
        b.button(text="🎒 Рюкзак (6000)", callback_data="buy_рюкзак")
        b.button(text="🔙 Назад", callback_data="to_menu")
        b.adjust(1); await c.message.edit_text("🛒 Магазин:", reply_markup=b.as_markup())

    @dp.callback_query(F.data == "to_menu")
    async def to_m(c: types.CallbackQuery):
        await c.answer(); await c.message.edit_text("🦝 Главное меню:", reply_markup=get_main_menu(c.from_user.id))

    print("🚀 ЕНОТ НА ЧИЛЕ С ИГРАМИ ЗАПУЩЕН!"); await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
