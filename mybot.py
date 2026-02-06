import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = '8164851577:AAGMU9nAceVgaRCp-xxAtlJHApz5KwjoiEI'

# --- ДАННЫЕ ---
user_data = {} 
board = [" " for _ in range(9)]
mines_games = {}
games_2048 = {}

def get_user(uid):
    if uid not in user_data: user_data[uid] = {'coins': 100}
    return user_data[uid]

# --- КЛАВИАТУРЫ ---
def get_main_menu(uid):
    u = get_user(uid)
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text=f"💰 Баланс: {u['coins']}", callback_data="none"))
    b.button(text="❌ Крестики-Нолики", callback_data="st_ttt")
    b.button(text="💣 Сапер 7x7", callback_data="st_mines")
    b.button(text="🔢 2048", callback_data="st_2048")
    b.button(text="✊ Камень-Ножницы", callback_data="st_rsp")
    b.button(text="🎰 Слоты 777", callback_data="st_slots")
    b.button(text="🎲 Кубики", callback_data="st_dice")
    b.button(text="🧮 Калькулятор", callback_data="st_calc")
    b.adjust(1, 2, 2, 2, 1); return b.as_markup()

def get_rsp_kb():
    b = InlineKeyboardBuilder()
    b.button(text="✊ Камень", callback_data="rsp_r")
    b.button(text="✋ Бумага", callback_data="rsp_p")
    b.button(text="✌️ Ножницы", callback_data="rsp_s")
    b.button(text="🔙 Меню", callback_data="to_menu")
    b.adjust(3, 1); return b.as_markup()

# --- ЛОГИКА 2048 ---
def init_2048():
    g = [[0]*4 for _ in range(4)]
    for _ in range(2): add_t(g)
    return g

def add_t(g):
    e = [(r, c) for r in range(4) for c in range(4) if g[r][c] == 0]
    if e: r, c = random.choice(e); g[r][c] = 2 if random.random() < 0.9 else 4

def comp(row):
    n = [i for i in row if i != 0]
    for i in range(len(n)-1):
        if n[i] == n[i+1]: n[i]*=2; n[i+1]=0
    r = [i for i in n if i != 0]
    return r + [0]*(4-len(r))

def move_2048(g, d):
    nw = []
    if d in ['left', 'right']:
        for r in g:
            l = r if d == 'left' else r[::-1]
            res = comp(l)
            nw.append(res if d == 'left' else res[::-1])
    else:
        for c in range(4):
            col = [g[r][c] for r in range(4)]
            res = comp(col if d == 'up' else col[::-1])
            res = res if d == 'up' else res[::-1]
            if not nw: nw = [[0]*4 for _ in range(4)]
            for r in range(4): nw[r][c] = res[r]
    return nw

# --- СТАРТ ---
async def start():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)

    @dp.message(F.text.lower().in_(["меню", "игры", "/start"]))
    async def menu(m: types.Message):
        await m.answer("🎮 Выбери игру:", reply_markup=get_main_menu(m.from_user.id))

    @dp.callback_query(F.data == "to_menu")
    async def to_m(c: types.CallbackQuery):
        await c.message.edit_text("🎮 Главное меню:", reply_markup=get_main_menu(c.from_user.id))

    # --- КАМЕНЬ НОЖНИЦЫ БУМАГА ---
    @dp.callback_query(F.data == "st_rsp")
    async def start_rsp(c: types.CallbackQuery):
        await c.message.edit_text("Твой выбор? Ставка 10💰", reply_markup=get_rsp_kb())

    @dp.callback_query(F.data.startswith("rsp_"))
    async def play_rsp(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        if u['coins'] < 10: return await c.answer("Мало монет!", show_alert=True)
        
        u_choice = c.data.split("_")[1]
        b_choice = random.choice(['r', 'p', 's'])
        mapping = {'r': '✊ Камень', 'p': '✋ Бумага', 's': '✌️ Ножницы'}
        
        u['coins'] -= 10
        if u_choice == b_choice:
            u['coins'] += 10
            res = f"Ничья! 🤝 Оба выбрали {mapping[u_choice]}"
        elif (u_choice == 'r' and b_choice == 's') or (u_choice == 'p' and b_choice == 'r') or (u_choice == 's' and b_choice == 'p'):
            u['coins'] += 25
            res = f"Ты победил! 🏆\nТвой: {mapping[u_choice]}\nМой: {mapping[b_choice]}\n+25💰"
        else:
            res = f"Я выиграл! 🤖\nТвой: {mapping[u_choice]}\nМой: {mapping[b_choice]}\n-10💰"
        
        await c.message.edit_text(res, reply_markup=get_main_menu(c.from_user.id))
        await c.answer()

    # --- СЛОТЫ 777 ---
    @dp.callback_query(F.data == "st_slots")
    async def play_slots(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        if u['coins'] < 15: return await c.answer("Нужно 15 монет!", show_alert=True)
        u['coins'] -= 15
        await c.message.answer("🎰 Крутим барабаны...")
        msg = await c.message.answer_dice(emoji="🎰")
        await asyncio.sleep(4)
        
        # В [Dice API](https://core.telegram.org) значения 1, 22, 43, 64 - это выигрышные комбинации
        if msg.dice.value in [1, 22, 43, 64]:
            u['coins'] += 100
            await c.message.answer("ДЖЕКПОТ! 🍒🍒🍒 +100💰", reply_markup=get_main_menu(c.from_user.id))
        else:
            await c.message.answer("Не повезло! Попробуй еще раз.", reply_markup=get_main_menu(c.from_user.id))
        await c.answer()

    # --- КУБИКИ ---
    @dp.callback_query(F.data == "st_dice")
    async def play_dice(c: types.CallbackQuery):
        u = get_user(c.from_user.id)
        if u['coins'] < 10: return await c.answer("Нужно 10 монет!", show_alert=True)
        u['coins'] -= 10
        await c.message.answer("🎲 Бросаем кубики...")
        msg_u = await c.message.answer_dice("🎲")
        msg_b = await c.message.answer_dice("🎲")
        await asyncio.sleep(4)
        v_u, v_b = msg_u.dice.value, msg_b.dice.value
        if v_u > v_b: u['coins'] += 25; res = f"Победа! {v_u}:{v_b} +25💰"
        elif v_u < v_b: res = f"Проигрыш! {v_u}:{v_b} -10💰"
        else: u['coins'] += 10; res = "Ничья! Возврат."
        await c.message.answer(res, reply_markup=get_main_menu(c.from_user.id))
        await c.answer()

    # --- ОСТАЛЬНОЕ (Кратко) ---
    @dp.callback_query(F.data == "st_ttt")
    async def t_init(c: types.CallbackQuery):
        global board; board = [" " for _ in range(9)]
        await c.message.edit_text("Крестики-нолики:", reply_markup=get_t_kb())

    @dp.callback_query(F.data.startswith("ce_"))
    async def t_move(c: types.CallbackQuery):
        idx = int(c.data.split("_")[1])
        if board[idx] == " ":
            board[idx] = "X"
            if not check_w(board):
                m = get_b_m(board)
                if m is not None: board[m] = "O"
            w = check_w(board)
            txt = f"Результат: {w}" if w else "Твой ход (X):"
            await c.message.edit_text(txt, reply_markup=get_t_kb())
        await c.answer()

    @dp.callback_query(F.data == "st_2048")
    async def s_2048(c: types.CallbackQuery):
        games_2048[c.from_user.id] = init_2048()
        await c.message.edit_text("2048:", reply_markup=get_2048_kb(c.from_user.id))

    @dp.callback_query(F.data.startswith("mv_"))
    async def mv_2048(c: types.CallbackQuery):
        u = c.from_user.id; d = c.data.split("_")[1]
        old = [r[:] for r in games_2048[u]]; new = move_2048(old, d)
        if new != old: add_t(new); games_2048[u] = new
        await c.message.edit_reply_markup(reply_markup=get_2048_kb(u)); await c.answer()

    @dp.callback_query(F.data == "st_mines")
    async def st_m(c: types.CallbackQuery):
        mines_games[c.from_user.id] = {'m': random.sample(range(49), 10), 'o': []}
        await c.message.edit_text("Сапер:", reply_markup=get_m_kb(c.from_user.id))

    @dp.callback_query(F.data.startswith("m_"))
    async def m_move(c: types.CallbackQuery):
        u = c.from_user.id; idx = int(c.data.split("_")[1]); g = mines_games[u]
        if idx in g['m']: await c.message.edit_text("БУМ! 💥", reply_markup=get_m_kb(u, True))
        else: 
            if idx not in g['o']: g['o'].append(idx)
            await c.message.edit_reply_markup(reply_markup=get_m_kb(u))
        await c.answer()

    @dp.callback_query(F.data == "st_calc")
    async def c_i(c: types.CallbackQuery): await c.message.edit_text("0", reply_markup=get_c_kb())

    @dp.callback_query(F.data.startswith("cl_"))
    async def c_p(c: types.CallbackQuery):
        cur, act = c.message.text, c.data.split("_")[1]
        if act == "clear": n = "0"
        elif act == "=":
            try: n = str(eval(cur))
            except: n = "Error"
        else: n = act if cur in ["0","Error"] else cur + act
        await c.message.edit_text(n, reply_markup=get_c_kb()); await c.answer()

    print("Бот запущен! Добавлены Слоты и КНБ.")
    await dp.start_polling(bot)

# --- ВСПОМОГАТЕЛЬНОЕ ---
def get_b_m(b):
    for i in range(9):
        cp = list(b)
        if cp[i]==" ":
            cp[i]="O"
            if check_w(cp)=="O": return i
    for i in range(9):
        cp = list(b)
        if cp[i]==" ":
            cp[i]="X"
            if check_w(cp)=="X": return i
    e = [i for i,v in enumerate(b) if v==" "]; return random.choice(e) if e else None

def check_w(b):
    for c in [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]:
        if b[c[0]]==b[c[1]]==b[c[2]] and b[c[0]]!=" ": return b[c[0]]
    return "Ничья" if " " not in b else None

def get_t_kb():
    b = InlineKeyboardBuilder()
    for i,v in enumerate(board): b.button(text=v if v!=" " else "⬜", callback_data=f"ce_{i}")
    b.button(text="🔙 Меню", callback_data="to_menu"); b.adjust(3,3,3,1); return b.as_markup()

def get_m_kb(u, over=False):
    b = InlineKeyboardBuilder(); g = mines_games[u]
    for i in range(49):
        t = "💥" if i in g['o'] and i in g['m'] else "⬜" if i in g['o'] else "💣" if over and i in g['m'] else "❓"
        b.button(text=t, callback_data=f"m_{i}")
    b.button(text="🔙 Меню", callback_data="to_menu"); b.adjust(7); return b.as_markup()

def get_c_kb():
    b = InlineKeyboardBuilder()
    for i in ["7","8","9","/","4","5","6","*","1","2","3","-","0",".","=","+"]: b.button(text=i, callback_data=f"cl_{i}")
    b.button(text="C", callback_data="cl_clear"); b.button(text="🔙", callback_data="to_menu"); b.adjust(4); return b.as_markup()

def get_2048_kb(u):
    b = InlineKeyboardBuilder(); g = games_2048[u]
    em = {0:"⬛",2:"2️⃣",4:"4️⃣",8:"8️⃣",16:"💥",32:"🔥",64:"🚀",128:"💎",256:"👑"}
    for r in g:
        for v in r: b.button(text=em.get(v, str(v)), callback_data="none")
    for d, l in [("left","⬅️"),("up","⬆️"),("down","⬇️"),("right","➡️")]: b.button(text=l, callback_data=f"mv_{d}")
    b.button(text="🔙 Меню", callback_data="to_menu"); b.adjust(4,4,4,4,4,1); return b.as_markup()

if __name__ == "__main__": asyncio.run(start())