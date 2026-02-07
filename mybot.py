import asyncio, random, os, json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web
from fractions import Fraction

TOKEN = '8164851577:AAGMU9nAceVgaRCp-xxAtlJHApz5KwjoiEI'
ADMIN_ID = "6032049080" 

async def handle(r): return web.Response(text="Enot 100k + Cases Edition")
async def start_web():
    app = web.Application(); app.router.add_get('/', handle)
    runner = web.AppRunner(app); await runner.setup()
    try: await web.TCPSite(runner, '0.0.0.0', 10000).start()
    except: pass

user_data, ttt_games = {}, {}
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
    {"name": "🪓 Лесоруб", "pay": 100, "goal": 500},
    {"name": "💻 Программист", "pay": 110, "goal": 210},
    {"name": "🚜 Фермер", "pay": 250, "goal": 300}
]

def load_data():
    global user_data
    if os.path.exists("users.json"):
        try: with open("users.json", "r") as f: user_data = json.load(f)
        except: user_data = {}

def save_all():
    try: 
        with open("users.json", "w") as f: json.dump(user_data, f)
    except: pass

def get_user(uid, name="Енотик"):
    uid = str(uid); is_admin = (uid == ADMIN_ID)
    if uid not in user_data:
        user_data[uid] = {'name': name, 'coins': 100000 if is_admin else 100, 'title': "Енот Полоскун" if is_admin else "🦴 Новичок", 'job_lvl': 0, 'work_count': 0, 'items': [], 'last_work': ''}
    if is_admin:
        user_data[uid]['title'] = "Енот Полоскун"
        if user_data[uid].get('coins', 0) < 100000: user_data[uid]['coins'] = 100000
    return user_data[uid]

def get_main_menu(uid):
    u = get_user(uid); b = InlineKeyboardBuilder()
    m = 2.0 if "Корона" in u['items'] else (1.4 if u['title'] == "Тюлень 2.0" else 1.0)
    b.row(types.InlineKeyboardButton(text=f"👤 {u['title']} | x{m}", callback_data="open_profile"))
    b.row(types.InlineKeyboardButton(text=f"💰 Баланс: {int(u['coins'])}", callback_data="none"))
    b.button(text="🛠 Работа", callback_data="go_work")
    b.button(text="🎮 Игры", callback_data="open_games")
    b.button(text="🛒 Магазин", callback_data="open_shop")
    b.button(text="📦 Кейс (100💰)", callback_data="open_case")
    b.button(text="🧮 Калькулятор", callback_data="st_calc")
    if str(uid) == ADMIN_ID: b.button(text="💎 VIP СКЛАД", callback_data="admin_shop")
    return b.adjust(1, 1, 2, 2, 1, 1).as_markup()

# --- КРЕСТИКИ НОЛИКИ ---
def get_ttt_kb(board):
    b = InlineKeyboardBuilder()
    for i, cell in enumerate(board): b.button(text=cell if cell else "⬜️", callback_data=f"ttt_{i}")
    b.button(text="🔙 Выход", callback_data="open_games")
    return b.adjust(3, 3, 3, 1).as_markup()

async def main():
    load_data(); await start_web()
    bot = Bot(token=TOKEN); dp = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)

    @dp.message(F.text.lower().in_(["/start", "меню", "енот", "игры"]))
    async def cmd_start(m: types.Message):
        get_user(m.from_user.id, m.from_user.first_name); save_all()
        await m.answer("🦝 **Енот на чиле: Кейсы и 100К**!", reply_markup=get_main_menu(m.from_user.id))

    # --- КЕЙСЫ ---
    @dp.callback_query(F.data == "open_case")
    async def open_case(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        if u['coins'] < 100: return await c.answer("Мало монет!", show_alert=True)
        u['coins'] -= 100
        rarity = random.choices(list(TITLES.keys()), weights=)[0]
        new_title = random.choice(TITLES[rarity])
        u['title'] = new_title; save_all()
        await c.message.answer(f"📦 БУМ! Тебе выпал статус [{rarity.upper()}]:\n✨ **{new_title}** ✨")
        await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "open_profile")
    async def profile(c: types.CallbackQuery):
        u = get_user(c.from_user.id); job = JOBS[u['job_lvl']]
        res = f"👤 **ПРОФИЛЬ**\n🏆 Титул: {u['title']}\n💰 Баланс: {int(u['coins'])}\n🛠 Работа: {job['name']}\n📈 Смены: {u['work_count']}/{job['goal']}\n🎒 Вещи: {', '.join(u['items']) if u['items'] else 'Пусто'}"
        await c.message.edit_text(res, reply_markup=InlineKeyboardBuilder().button(text="🔙 Назад", callback_data="to_menu").as_markup())

    # --- ИГРЫ ---
    @dp.callback_query(F.data == "open_games")
    async def games_m(c: types.CallbackQuery):
        b = InlineKeyboardBuilder().button(text="❌ Крестики", callback_data="st_ttt").button(text="🎰 Казино", callback_data="st_slots").button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("🎮 Игры на чиле:", reply_markup=b.adjust(2, 1).as_markup())

    @dp.callback_query(F.data == "st_slots")
    async def slots(c: types.CallbackQuery):
        u = get_user(c.from_user.id); u['coins'] -= 50; m = await c.message.answer_dice(emoji="🎰"); await asyncio.sleep(3)
        if m.dice.value in: u['coins'] += 1000; await c.message.answer("💎 ДЖЕКПОТ! +1000💰")
        save_all(); await c.message.answer("Меню:", reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "st_ttt")
    async def ttt_start(c: types.CallbackQuery):
        ttt_games[c.from_user.id] = [""] * 9
        await c.message.edit_text("❌ Твой ход:", reply_markup=get_ttt_kb(ttt_games[c.from_user.id]))

    @dp.callback_query(F.data.startswith("ttt_"))
    async def ttt_move(c: types.CallbackQuery):
        idx = int(c.data.split("_")); board = ttt_games.get(c.from_user.id)
        if not board or board[idx]: return await c.answer("Занято!")
        board[idx] = "❌"
        empty = [i for i, v in enumerate(board) if v == ""]
        if empty: board[random.choice(empty)] = "⭕️"
        await c.message.edit_reply_markup(reply_markup=get_ttt_kb(board))

    # --- РАБОТА ---
    @dp.callback_query(F.data == "go_work")
    async def work_m(c: types.CallbackQuery):
        u = get_user(c.from_user.id); b = InlineKeyboardBuilder()
        b.button(text=f"🏢 {JOBS[u['job_lvl']]['name']}", callback_data="work_normal")
        b.button(text="🤫 Контрабанда", callback_data="work_smuggle")
        b.button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("Выбери путь:", reply_markup=b.adjust(1).as_markup())

    @dp.callback_query(F.data == "work_normal")
    async def work_n(c: types.CallbackQuery):
        u = get_user(c.from_user.id); now = datetime.now()
        if u.get('last_work') and (now - datetime.strptime(u['last_work'], "%H:%M:%S")) < timedelta(seconds=15):
            return await c.answer("Чильни немного! 🍹", show_alert=True)
        job = JOBS[u['job_lvl']]; m = 2.0 if "Корона" in u['items'] else 1.0
        pay = int(job['pay'] * m); u['coins'] += pay; u['work_count'] += 1; u['last_work'] = now.strftime("%H:%M:%S")
        if u['work_count'] >= job['goal'] and u['job_lvl'] < 4: u['job_lvl'] += 1; u['work_count'] = 0
        save_all(); await c.answer(f"+{pay}💰"); await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    # --- МАГАЗИН И ПРОЧЕЕ ---
    @dp.callback_query(F.data == "open_shop")
    async def shop_m(c: types.CallbackQuery):
        b = InlineKeyboardBuilder().button(text="🧤 Перчатки (500)", callback_data="buy_перчатки").button(text="🚲 Велик (1350)", callback_data="buy_велик").button(text="🎒 Рюкзак (6000)", callback_data="buy_рюкзак").button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("🛒 Магазин:", reply_markup=b.adjust(1).as_markup())

    @dp.callback_query(F.data == "admin_shop")
    async def a_shop(c: types.CallbackQuery):
        if str(c.from_user.id) != ADMIN_ID: return
        b = InlineKeyboardBuilder().button(text="🧼 Тазик (10к)", callback_data="buy_тазик").button(text="👓 Очки (5к)", callback_data="buy_очки").button(text="👑 Корона (25к)", callback_data="buy_корона").button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("💎 VIP СКЛАД ПОЛОСКУНА:", reply_markup=b.adjust(1).as_markup())

    @dp.callback_query(F.data.startswith("buy_"))
    async def buy_h(c: types.CallbackQuery):
        u = get_user(c.from_user.id); item = c.data.split("_"); p = {"тазик": 10000, "очки": 5000, "корона": 25000, "перчатки": 500, "велик": 1350, "рюкзак": 6000}
        if u['coins'] < p.get(item, 999999): return await c.answer("Мало монет!", show_alert=True)
        u['coins'] -= p[item]; u['items'].append(item.capitalize()); save_all()
        await c.answer("Куплено!"); await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "to_menu")
    async def back(c: types.CallbackQuery): await c.message.edit_text("🦝 Главное меню:", reply_markup=get_main_menu(c.from_user.id))

    print("🚀 ЕНОТ ULTIMATE + КЕЙСЫ ЗАПУЩЕН!"); await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


