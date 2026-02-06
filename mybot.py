import asyncio, random, os, json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web
from fractions import Fraction

TOKEN = '8164851577:AAGMU9nAceVgaRCp-xxAtlJHApz5KwjoiEI'
ADMIN_ID = "6032049080"

# --- СЕРВЕР ДЛЯ RENDER ---
async def handle(r): return web.Response(text="Enot Status: 100%")
async def start_web():
    app = web.Application(); app.router.add_get('/', handle)
    runner = web.AppRunner(app); await runner.setup()
    try: await web.TCPSite(runner, '0.0.0.0', 10000).start()
    except: pass

# --- ГЛОБАЛЬНЫЕ ДАННЫЕ ---
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

# --- СИСТЕМА СОХРАНЕНИЯ ---
def load_data():
    global user_data, server_stats
    if os.path.exists("users.json"):
        try:
            with open("users.json", "r") as f: user_data = json.load(f)
        except: user_data = {}
    if os.path.exists("stats.json"):
        try:
            with open("stats.json", "r") as f: server_stats = json.load(f)
        except: server_stats = {"total_earned": 0, "tax_pool": 0}

def save_all():
    try:
        with open("users.json", "w") as f: json.dump(user_data, f)
        with open("stats.json", "w") as f: json.dump(server_stats, f)
    except: pass

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
    m = 1.4 if u['title'] == "Тюлень 2.0" else (2.0 if "Корона" in u['items'] else 1.0)
    b.row(types.InlineKeyboardButton(text=f"👤 {u['title']} | x{m} ⚡️", callback_data="none"))
    b.row(types.InlineKeyboardButton(text=f"💰 Баланс: {int(u['coins'])}", callback_data="none"))
    b.button(text="🛠 Работа", callback_data="go_work")
    b.button(text="🎮 Игры", callback_data="open_games")
    b.button(text="🛒 Магазин", callback_data="open_shop")
    b.button(text="🧮 Калькулятор", callback_data="st_calc")
    b.button(text="📦 Кейс (100)", callback_data="open_case")
    b.button(text="📊 Статы", callback_data="server_stats")
    if str(uid) == ADMIN_ID: b.button(text="💎 VIP СКЛАД", callback_data="admin_shop")
    b.adjust(1, 1, 2, 2, 1, 1, 1); return b.as_markup()

# --- ОСНОВНОЙ КОД ---
async def main():
    load_data(); await start_web()
    bot = Bot(token=TOKEN); dp = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)

    @dp.message(lambda m: m.text and m.text.lower() in ["игры", "меню", "енот", "/start"])
    async def start(m: types.Message):
        await m.answer(f"🦝 **Енот на чиле** приветствует тебя!", reply_markup=get_main_menu(m.from_user.id))

    # РАБОТА
    @dp.callback_query(F.data == "go_work")
    async def work(c: types.CallbackQuery):
        u = get_user(c.from_user.id); now = datetime.now()
        if u.get('last_work'):
            diff = now - datetime.strptime(u['last_work'], "%H:%M:%S")
            if diff < timedelta(seconds=30) and "Компотик" not in u['items']:
                return await c.answer("Чильни 30 сек или выпей Компотик!", show_alert=True)
        
        if "Компотик" in u['items']: u['items'].remove("Компотик")
        job = JOBS[u['job_lvl']]
        bonus = (15 if "Перчатки" in u['items'] else 0) + (40 if "Велосипед" in u['items'] else 0) + (150 if "Рюкзак" in u['items'] else 0)
        multi = 1.4 if u['title'] == "Тюлень 2.0" else (2.0 if "Корона" in u['items'] else 1.0)
        pay = int((job['pay'] + bonus) * multi)
        
        event = ""
        if random.random() < 0.1: 
            r = random.randint(20, 50); u['coins'] += r; event = f"\n🍀 Нашел заначку: +{r}"
        elif random.random() > 0.9 and "Очки" not in u['items']: 
            u['coins'] -= 20; event = "\n💢 Штраф: -20"

        u['coins'] += pay; u['work_count'] += 1; u['last_work'] = now.strftime("%H:%M:%S")
        server_stats['total_earned'] += pay
        for uid, data in user_data.items():
            if "Тазик" in data.get('items', []): data['coins'] += 2; server_stats['tax_pool'] += 2

        if u['work_count'] >= job['goal'] and u['job_lvl'] < 3:
            u['job_lvl'] += 1; u['work_count'] = 0
            await c.message.answer(f"📈 ПОВЫШЕНИЕ! Ты теперь {JOBS[u['job_lvl']]['name']}!")
        
        save_all(); await c.answer(f"+{pay}💰 {event}"); await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    # МАГАЗИНЫ
    @dp.callback_query(F.data == "open_shop")
    async def shop(c: types.CallbackQuery):
        b = InlineKeyboardBuilder()
        b.button(text="🧤 Перчатки (500)", callback_data="buy_перчатки")
        b.button(text="🚲 Велосипед (1350)", callback_data="buy_велосипед")
        b.button(text="🧃 Компотик (130)", callback_data="buy_компотик")
        b.button(text="🎒 Рюкзак (6000)", callback_data="buy_рюкзак")
        b.button(text="🔙 Назад", callback_data="to_menu")
        b.adjust(1); await c.message.edit_text("🛒 Магазин на чиле:", reply_markup=b.as_markup())

    @dp.callback_query(F.data == "admin_shop")
    async def admin(c: types.CallbackQuery):
        if str(c.from_user.id) != ADMIN_ID: return
        b = InlineKeyboardBuilder()
        b.button(text="🧼 Золотой Тазик (10к)", callback_data="buy_тазик")
        b.button(text="👓 Инж. Очки (5к)", callback_data="buy_очки")
        b.button(text="👑 Корона (25к)", callback_data="buy_корона")
        b.button(text="🔙 Назад", callback_data="to_menu")
        b.adjust(1); await c.message.edit_text("💎 VIP СКЛАД ПОЛОСКУНА:", reply_markup=b.as_markup())

    @dp.callback_query(F.data.startswith("buy_"))
    async def buy_item(c: types.CallbackQuery):
        u = get_user(c.from_user.id); item = c.data.split("_")
        prices = {"перчатки": 500, "велосипед": 1350, "компотик": 130, "рюкзак": 6000, "тазик": 10000, "очки": 5000, "корона": 25000}
        name = item.capitalize()
        if u['coins'] < prices[item]: return await c.answer("Мало монет!", show_alert=True)
        u['coins'] -= prices[item]; u['items'].append(name); save_all()
        await c.answer(f"Куплено: {name}!"); await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    # КАЛЬКУЛЯТОР
    @dp.callback_query(F.data == "st_calc")
    async def calc(c: types.CallbackQuery):
        b = InlineKeyboardBuilder()
        b.button(text="🔢 Обычный", callback_data="calc_s")
        b.button(text="🍰 Дробный", callback_data="calc_f")
        b.button(text="🔙 Назад", callback_data="to_menu")
        await c.message.edit_text("🧮 Тип калькулятора:\n(Пример пиши просто в чат)", reply_markup=b.as_markup())

    @dp.message(F.text.regexp(r"^(\d+[\+\-\*\/]\d+)$"))
    async def s_calc(m: types.Message):
        try: await m.answer(f"🧩 Результат: {eval(m.text)}")
        except: pass

    @dp.message(F.text.regexp(r"^(\d+\/\d+[\+\-\*\/]\d+\/\d+)$"))
    async def f_calc(m: types.Message):
        try:
            t = m.text.replace(" ", "")
            for op in "+-*/":
                if op in t:
                    p = t.split(op); f1, f2 = Fraction(p), Fraction(p)
                    if op == "+": r = f1 + f2
                    elif op == "-": r = f1 - f2
                    elif op == "*": r = f1 * f2
                    elif op == "/": r = f1 / f2
                    await m.answer(f"🍰 Дробный результат: {r}"); break
        except: pass

    # КЕЙСЫ И СТАТИСТИКА
    @dp.callback_query(F.data == "open_case")
    async def case(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        if u['coins'] < 100: return await c.answer("Мало монет!", show_alert=True)
        u['coins'] -= 100; r = random.choices(list(TITLES.keys()), weights=)
        u['title'] = random.choice(TITLES[r]); save_all()
        await c.answer(f"📦 Титул: {u['title']}", show_alert=True); await c.message.edit_reply_markup(reply_markup=get_main_menu(c.from_user.id))

    @dp.callback_query(F.data == "server_stats")
    async def stats(c: types.CallbackQuery):
        msg = f"📊 СТАТЫ:\n💰 Всего заработано: {server_stats['total_earned']}\n🧺 Налогов в Тазике: {server_stats['tax_pool']}\n\n🏆 ТОП:\n"
        sort = sorted(user_data.items(), key=lambda x: x['coins'], reverse=True)[:5]
        for i, (uid, data) in enumerate(sort, 1): msg += f"{i}. {data['title']} — {int(data['coins'])}💰\n"
        await c.answer(msg, show_alert=True)

    @dp.callback_query(F.data == "to_menu")
    async def back(c: types.CallbackQuery): await c.message.edit_text("🦝 Меню:", reply_markup=get_main_menu(c.from_user.id))

    print("🚀 ЕНОТ НА ЧИЛЕ В ПОЛНОМ РАЗМЕРЕ ЗАПУЩЕН!"); await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())


