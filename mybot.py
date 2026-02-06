import asyncio, random, os, json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web
from fractions import Fraction # Для работы с дробями

TOKEN = '8164851577:AAGMU9nAceVgaRCp-xxAtlJHApz5KwjoiEI'
ADMIN_ID = "6032049080" 

# --- ФИКС RENDER ---
async def handle(r): return web.Response(text="Enot is Alive!")
async def start_web():
    app = web.Application(); app.router.add_get('/', handle)
    runner = web.AppRunner(app); await runner.setup()
    try: await web.TCPSite(runner, '0.0.0.0', 10000).start()
    except: pass

# --- ДАННЫЕ ---
user_data = {}
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
    global user_data
    if os.path.exists("users.json"):
        try:
            with open("users.json", "r") as f: user_data = json.load(f)
        except: user_data = {}

def save_all():
    try:
        with open("users.json", "w") as f: json.dump(user_data, f)
    except: pass

def get_user(uid):
    uid = str(uid)
    if uid not in user_data:
        is_admin = (uid == ADMIN_ID)
        user_data[uid] = {
            'coins': 10000 if is_admin else 100,
            'title': "Енот Полоскун" if is_admin else "🦴 Новичок",
            'job_lvl': 0, 'work_count': 0, 'items': [], 'multi': 1.0
        }
    return user_data[uid]

def get_main_menu(uid):
    u = get_user(uid); b = InlineKeyboardBuilder()
    multi = 1.4 if u['title'] == "Тюлень 2.0" else (2.0 if "Корона" in u['items'] else 1.0)
    b.row(types.InlineKeyboardButton(text=f"👤 {u['title']} | x{multi}", callback_data="none"))
    b.row(types.InlineKeyboardButton(text=f"💰 Баланс: {int(u['coins'])}", callback_data="none"))
    b.button(text="🛠 Работа", callback_data="go_work")
    b.button(text="🎮 Игры", callback_data="open_games")
    b.button(text="🛒 Магазин", callback_data="open_shop")
    b.button(text="🧮 Калькулятор", callback_data="st_calc") # Кнопка калькулятора
    b.button(text="📦 Кейс (100)", callback_data="open_case")
    if str(uid) == ADMIN_ID: b.button(text="💎 VIP СКЛАД", callback_data="admin_shop")
    b.adjust(1, 1, 2, 2, 1, 1); return b.as_markup()

async def main():
    load_data(); await start_web()
    bot = Bot(token=TOKEN); dp = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)

    @dp.message(lambda m: m.text and m.text.lower() in ["игры", "меню", "енот", "/start", "калькулятор"])
    async def start_handler(m: types.Message):
        await m.answer(f"🦝 **Енот на чиле** в здании!", reply_markup=get_main_menu(m.from_user.id))

    # --- ЛОГИКА КАЛЬКУЛЯТОРА ---
    @dp.callback_query(F.data == "st_calc")
    async def calc_menu(c: types.CallbackQuery):
        b = InlineKeyboardBuilder()
        b.button(text="🔢 Обычный", callback_data="calc_simple")
        b.button(text="🍰 Дробный", callback_data="calc_frac")
        b.button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("🧮 Выбери тип калькулятора:\n(Отправь пример сообщением после выбора)", reply_markup=b.as_markup())

    @dp.callback_query(F.data.startswith("calc_"))
    async def calc_type(c: types.CallbackQuery):
        t = "обычный" if "simple" in c.data else "дробный"
        await c.answer(f"Принято! Пиши пример в чат (например 2+2 или 1/2+1/4)", show_alert=True)

    @dp.message(F.text.regexp(r"^(\d+[\+\-\*\/]\d+)$")) # Для обычных 2+2
    async def simple_calc(m: types.Message):
        try:
            res = eval(m.text)
            await m.answer(f"🧩 Результат: {res}")
        except: await m.answer("❌ Ошибка в примере!")

    @dp.message(F.text.regexp(r"^(\d+\/\d+[\+\-\*\/]\d+\/\d+)$")) # Для дробей 1/2+1/2
    async def frac_calc(m: types.Message):
        try:
            # Парсим пример типа 1/2 + 1/4
            txt = m.text.replace(" ", "")
            for op in "+-*/":
                if op in txt:
                    parts = txt.split(op)
                    f1, f2 = Fraction(parts[0]), Fraction(parts[1])
                    if op == "+": res = f1 + f2
                    if op == "-": res = f1 - f2
                    if op == "*": res = f1 * f2
                    if op == "/": res = f1 / f2
                    await m.answer(f"🍰 Дробный результат: {res}")
                    break
        except: await m.answer("❌ Ошибка! Пиши дроби как 1/2+1/3")

    # --- ОСТАЛЬНАЯ ЛОГИКА ---
    @dp.callback_query(F.data == "go_work")
    async def work(c: types.CallbackQuery):
        u = get_user(c.from_user.id); job = JOBS[u['job_lvl']]
        multi = 1.4 if u['title'] == "Тюлень 2.0" else (2.0 if "Корона" in u['items'] else 1.0)
        pay = int(job['pay'] * multi)
        u['coins'] += pay; u['work_count'] += 1; save_all()
        await c.answer(f"+{pay}💰"); await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "open_games")
    async def g_m(c: types.CallbackQuery):
        b = InlineKeyboardBuilder()
        b.button(text="🎰 Слоты", callback_data="st_slots")
        b.button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("🎮 Игры:", reply_markup=b.as_markup())

    @dp.callback_query(F.data == "to_menu")
    async def to_m(c: types.CallbackQuery): 
        await c.message.edit_text("🦝 Меню:", reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "open_case")
    async def open_c(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        if u['coins'] < 100: return await c.answer("Мало монет!", show_alert=True)
        u['coins'] -= 100; r = random.choices(list(TITLES.keys()), weights=[50, 30, 15, 4, 1])[0]
        u['title'] = random.choice(TITLES[r]); save_all()
        await c.answer(f"📦 Новый титул: {u['title']}", show_alert=True)
        await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    print("🚀 БОТ С КАЛЬКУЛЯТОРОМ ЗАПУЩЕН!"); await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
