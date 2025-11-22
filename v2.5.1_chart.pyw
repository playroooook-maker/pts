import tkinter as tk
from tkinter import ttk, messagebox
import time
from random import randint, choice
import colorsys
import winsound
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os
import atexit
CONFIG_FILE = "config.json"
COMMISSION_RATE = 0.01
leverage = 1
max_price_change = 15
news = ""
price_change = 0
price_history = []
time_points = []
sound_enabled = True
animation_running = False
hue = 0.0
translations = {
    "ru": {
        "title": "💹 Crypto Trading Simulator v2.5",
        "welcome": "📈 Добро пожаловать в Crypto Trading Simulator v2.5!",
        "realmoney": "💵 Реальные деньги: {:.2f}",
        "crypto_balance": "🪙 Крипто в $: {:.2f}",
        "coin_count": "Количество коинов: {:.2f}",
        "coin_value": "1 коин = {:.2f} ({:+.2f}%)",
        "commission": "Комиссия: {:.2f}% | Плечо: {:.2f}x",
        "amount_placeholder": "Введите сумму (+покупка / -продажа)",
        "trade_btn": "💸 Купить / Продать",
        "news_btn": "📰 Свежая новость",
        "update_btn": "🔄 Обновить курс",
        "settings_btn": "⚙️ Настройки",
        "loading": "Загрузка игры...",
        "settings_title": "⚙️ Настройки",
        "settings_label": "Настройки параметров",
        "balance_label": "Баланс (реальные деньги):",
        "coins_label": "Количество криптокоинов:",
        "price_label": "Цена коина:",
        "max_change_label": "Макс. изменение (%):",
        "commission_label": "Комиссия (0.01 = 1%):",
        "leverage_label": "Плечо:",
        "themes_label": "🎨 Обычные темы:",
        "animated_themes_label": "🌈 Анимированные темы:",
        "sound_label": "🔊 Звук:",
        "sound_check": "Включить звук",
        "apply_btn": "Применить",
        "language_label": "🌐 Язык:",
        "news_already": "⚠️ Новость уже активна — обновите курс перед новой!",
        "random_change": "📉 Цена изменилась случайно.",
        "bought": "💸 Куплено {:.2f} коинов.",
        "sold": "💰 Продано {:.2f} коинов.",
        "enter_amount": "Введите сумму больше 0.",
        "error": "Ошибка",
        "enter_number": "Введите число.",
        "insufficient_funds": "Недостаточно средств!",
        "insufficient_coins": "Недостаточно коинов!",
        "toast_news": "📰 Новость",
        "toast_price_up": "📈 Цена выросла",
        "toast_price_down": "📉 Цена упала",
        "toast_trade": "💼 Сделка выполнена"
    },
    "en": {
        "title": "💹 Crypto Trading Simulator v2.5",
        "welcome": "📈 Welcome to Crypto Trading Simulator v2.5!",
        "realmoney": "💵 Real money: {:.2f}",
        "crypto_balance": "🪙 Crypto in $: {:.2f}",
        "coin_count": "Coin count: {:.2f}",
        "coin_value": "1 coin = {:.2f} ({:+.2f}%)",
        "commission": "Commission: {:.2f}% | Leverage: {:.2f}x",
        "amount_placeholder": "Enter amount (+buy / -sell)",
        "trade_btn": "💸 Buy / Sell",
        "news_btn": "📰 Fresh News",
        "update_btn": "🔄 Update Price",
        "settings_btn": "⚙️ Settings",
        "loading": "Loading game...",
        "settings_title": "⚙️ Settings",
        "settings_label": "Parameter Settings",
        "balance_label": "Balance (real money):",
        "coins_label": "Crypto coins amount:",
        "price_label": "Coin price:",
        "max_change_label": "Max change (%):",
        "commission_label": "Commission (0.01 = 1%):",
        "leverage_label": "Leverage:",
        "themes_label": "🎨 Regular themes:",
        "animated_themes_label": "🌈 Animated themes:",
        "sound_label": "🔊 Sound:",
        "sound_check": "Enable sound",
        "apply_btn": "Apply",
        "language_label": "🌐 Language:",
        "news_already": "⚠️ News already active — update price before new one!",
        "random_change": "📉 Price changed randomly.",
        "bought": "💸 Bought {:.2f} coins.",
        "sold": "💰 Sold {:.2f} coins.",
        "enter_amount": "Enter amount greater than 0.",
        "error": "Error",
        "enter_number": "Enter a number.",
        "insufficient_funds": "Insufficient funds!",
        "insufficient_coins": "Insufficient coins!",
        "toast_news": "📰 News",
        "toast_price_up": "📈 Price Up",
        "toast_price_down": "📉 Price Down",
        "toast_trade": "💼 Trade Executed"
    }
}

current_language = "ru"

def tr(key, *args):
    text = translations[current_language].get(key, key)
    if args:
        return text.format(*args)
    return text
class Toast:
    def __init__(self, root):
        self.root = root
        self.active_toasts = []
    def show(self, message, duration=2000):
        if not self.root.winfo_exists():
            return
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.configure(bg='#333333', relief='solid', bd=1)
        x = self.root.winfo_x() + self.root.winfo_width() - 250
        y = self.root.winfo_y() + 50
        toast.geometry(f"+{x}+{y}")
        
        label = tk.Label(toast, text=message, fg='white', bg='#333333', 
                        font=('Arial', 10), padx=15, pady=8)
        label.pack()
        
        self.active_toasts.append(toast)
        
        # Плавное появление
        toast.attributes('-alpha', 0.0)
        
        def fade_in(step=0):
            if not toast.winfo_exists() or step > 100:
                return
            toast.attributes('-alpha', step/100)
            if step < 100:
                toast.after(2, fade_in, step + 5)
        
        def fade_out(step=100):
            if not toast.winfo_exists() or step < 0:
                if toast.winfo_exists():
                    toast.destroy()
                if toast in self.active_toasts:
                    self.active_toasts.remove(toast)
                return
            toast.attributes('-alpha', step/100)
            if step > 0:
                toast.after(2, fade_out, step - 5)
            else:
                if toast.winfo_exists():
                    toast.destroy()
                if toast in self.active_toasts:
                    self.active_toasts.remove(toast)
        fade_in()
        toast.after(duration, fade_out)
    def cleanup(self):
        """Очистка всех уведомлений"""
        for toast in self.active_toasts[:]:
            if toast.winfo_exists():
                toast.destroy()
        self.active_toasts.clear()
def load_config():
    global current_language, sound_enabled, realmoney, cryptocoins, vaalue_of_coin, max_price_change, COMMISSION_RATE, leverage
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                current_language = config.get('language', 'ru')
                sound_enabled = config.get('sound_enabled', True)
                realmoney = config.get('realmoney', 100)
                cryptocoins = config.get('cryptocoins', 10)
                vaalue_of_coin = config.get('vaalue_of_coin', 20)
                max_price_change = config.get('max_price_change', 15)
                COMMISSION_RATE = config.get('COMMISSION_RATE', 0.01)
                leverage = config.get('leverage', 1)
    except Exception as e:
        print(f"Error loading config: {e}")

def save_config():
    try:
        config = {
            'language': current_language,
            'sound_enabled': sound_enabled,
            'realmoney': realmoney,
            'cryptocoins': cryptocoins,
            'vaalue_of_coin': vaalue_of_coin,
            'max_price_change': max_price_change,
            'COMMISSION_RATE': COMMISSION_RATE,
            'leverage': leverage
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config: {e}")

# === Воспроизведение звука ===
def play_sound(event_type):
    if not sound_enabled:
        return
    sounds = {
        "buy": (880, 150),
        "sell": (600, 150),
        "news": (700, 200),
        "error": (300, 250),
        "update": (500, 120),
    }
    if event_type in sounds:
        freq, dur = sounds[event_type]
        try:
            winsound.Beep(freq, dur)
        except:
            pass  # Игнорируем ошибки звука

# === Новости и рынок ===
def generate_news():
    global max_price_change
    if current_language == "ru":
        news_types = ["Положительная", "Отрицательная", "Нейтральная"]
        positive = [
            "Криптовалюта демонстрирует устойчивый рост.",
            "Институциональные инвесторы проявляют интерес.",
            "Новые партнёрства стимулируют рынок.",
        ]
        negative = [
            "Регуляторы усиливают контроль.",
            "Хакерская атака на крупную биржу.",
            "Паника среди инвесторов из-за слухов.",
        ]
        neutral = ["Рынок стабилен.", "Небольшие колебания в пределах нормы."]
    else:
        news_types = ["Positive", "Negative", "Neutral"]
        positive = [
            "Cryptocurrency shows steady growth.",
            "Institutional investors show interest.",
            "New partnerships stimulate the market.",
        ]
        negative = [
            "Regulators tighten control.",
            "Hacker attack on a major exchange.",
            "Investor panic due to rumors.",
        ]
        neutral = ["Market is stable.", "Small fluctuations within normal range."]

    news_type = choice(news_types)
    
    if news_type in ["Положительная", "Positive"]:
        return choice(positive), randint(1, max_price_change)
    elif news_type in ["Отрицательная", "Negative"]:
        return choice(negative), randint(-max_price_change, -1)
    else:
        return choice(neutral), randint(-3, 3)

def display_news():
    global news, price_change
    if news:
        status_label.config(text=tr("news_already"))
        play_sound("error")
        return
    news, price_change = generate_news()
    status_label.config(text=f"📰 {news}")
    play_sound("news")
    new_button.config(state="disabled")
    toast.show(tr("toast_news"))

def update_price():
    global vaalue_of_coin, realmoney_in_crypto, cryptocoins, realmoney, price_history, time_points, price_change, news
    try:
        if news:
            percent_change = price_change / 100.0
        else:
            random_change = randint(-max_price_change // 2, max_price_change // 2)
            percent_change = random_change / 100.0
            status_label.config(text=tr("random_change"))
        vaalue_of_coin += vaalue_of_coin * percent_change
        vaalue_of_coin = max(0.01, vaalue_of_coin)
        realmoney_in_crypto = cryptocoins * vaalue_of_coin
        update_labels(price_change if news else random_change)
        price_history.append(vaalue_of_coin)
        time_points.append(len(price_history))
        
        # Показываем toast об изменении цены
        if percent_change > 0:
            toast.show(tr("toast_price_up"))
        elif percent_change < 0:
            toast.show(tr("toast_price_down"))
            
        news = ""
        price_change = 0
        new_button.config(state="normal")
        play_sound("update")
        update_chart()
    except Exception as e:
        play_sound("error")
        messagebox.showerror(tr("error"), str(e))

def make_trade():
    global realmoney, cryptocoins, realmoney_in_crypto, vaalue_of_coin, COMMISSION_RATE, leverage
    try:
        amount = float(amount_entry.get())
        if amount == 0:
            status_label.config(text=tr("enter_amount"))
            play_sound("error")
            return
        amount_with_leverage = amount * leverage
        if amount > 0:
            total_cost = amount_with_leverage + amount_with_leverage * COMMISSION_RATE
            if total_cost > realmoney:
                messagebox.showerror(tr("error"), tr("insufficient_funds"))
                play_sound("error")
                return
            coins = amount_with_leverage / vaalue_of_coin
            cryptocoins += coins
            realmoney -= total_cost
            status_label.config(text=tr("bought", coins))
            play_sound("buy")
        else:
            amount = abs(amount)
            coins_to_sell = amount / vaalue_of_coin
            if coins_to_sell > cryptocoins:
                messagebox.showerror(tr("error"), tr("insufficient_coins"))
                play_sound("error")
                return
            cryptocoins -= coins_to_sell
            revenue = amount - amount * COMMISSION_RATE
            realmoney += revenue
            status_label.config(text=tr("sold", coins_to_sell))
            play_sound("sell")
        realmoney_in_crypto = cryptocoins * vaalue_of_coin
        update_labels(0)
        toast.show(tr("toast_trade"))
    except ValueError:
        messagebox.showerror(tr("error"), tr("enter_number"))
        play_sound("error")
def update_labels(change):
    if 'realmoney_label' in globals() and realmoney_label.winfo_exists():
        realmoney_label.config(text=tr("realmoney", realmoney))
        crypto_balance_label.config(text=tr("crypto_balance", realmoney_in_crypto))
        coin_count_label.config(text=tr("coin_count", cryptocoins))
        coin_value_label.config(text=tr("coin_value", vaalue_of_coin, change))
        commission_rate_label.config(text=tr("commission", COMMISSION_RATE*100, leverage))
def open_settings():
    global settings_window
    if 'settings_window' in globals() and settings_window and settings_window.winfo_exists():
        settings_window.lift()
        return
    settings_window = tk.Toplevel(root)
    settings_window.title(tr("settings_title"))
    settings_window.geometry("340x700")
    settings_window.configure(bg=bg_color)
    settings_window.protocol("WM_DELETE_WINDOW", lambda: settings_window.destroy())
    ttk.Label(settings_window, text=tr("settings_label"), font=("Arial", 13, "bold")).pack(pady=10)
    def add_entry(label, var):
        ttk.Label(settings_window, text=label).pack()
        entry = ttk.Entry(settings_window)
        entry.insert(0, str(var))
        entry.pack(pady=3)
        return entry
    global realmoney_entry, cryptocoins_entry, coin_value_entry, max_change_entry, commission_rate_entry, leverage_entry, theme_var, sound_var, language_var
    realmoney_entry = add_entry(tr("balance_label"), realmoney)
    cryptocoins_entry = add_entry(tr("coins_label"), cryptocoins)
    coin_value_entry = add_entry(tr("price_label"), vaalue_of_coin)
    max_change_entry = add_entry(tr("max_change_label"), max_price_change)
    commission_rate_entry = add_entry(tr("commission_label"), COMMISSION_RATE)
    leverage_entry = add_entry(tr("leverage_label"), leverage)
    ttk.Label(settings_window, text=tr("language_label")).pack(pady=5)
    language_var = tk.StringVar(value=current_language)
    ttk.Radiobutton(settings_window, text="Русский", variable=language_var, value="ru").pack(anchor="w", padx=20)
    ttk.Radiobutton(settings_window, text="English", variable=language_var, value="en").pack(anchor="w", padx=20)
    ttk.Label(settings_window, text=tr("themes_label")).pack(pady=5)
    theme_var = tk.StringVar(value=current_theme)
    for t in base_themes.keys():
        ttk.Radiobutton(settings_window, text=t.capitalize(), variable=theme_var, value=t).pack(anchor="w", padx=20)
    ttk.Label(settings_window, text=tr("animated_themes_label")).pack(pady=5)
    for t in animated_themes.keys():
        ttk.Radiobutton(settings_window, text=t, variable=theme_var, value=t).pack(anchor="w", padx=20)
    ttk.Label(settings_window, text=tr("sound_label")).pack(pady=5)
    sound_var = tk.BooleanVar(value=sound_enabled)
    ttk.Checkbutton(settings_window, text=tr("sound_check"), variable=sound_var).pack(anchor="w", padx=20)
    ttk.Button(settings_window, text=tr("apply_btn"), command=apply_settings).pack(pady=10)
def apply_settings():
    global realmoney, cryptocoins, vaalue_of_coin, max_price_change, COMMISSION_RATE, leverage, current_theme, sound_enabled, current_language
    try:
        realmoney = float(realmoney_entry.get())
        cryptocoins = float(cryptocoins_entry.get())
        vaalue_of_coin = float(coin_value_entry.get())
        max_price_change = int(max_change_entry.get())
        COMMISSION_RATE = float(commission_rate_entry.get())
        leverage = float(leverage_entry.get())
        sound_enabled = sound_var.get()
        theme = theme_var.get()
        new_language = language_var.get()
        
        if theme != current_theme:
            apply_theme(theme)
            current_theme = theme
            
        if new_language != current_language:
            current_language = new_language
            update_ui_language()
            
        update_labels(0)
        save_config()
        if settings_window and settings_window.winfo_exists():
            settings_window.destroy()
    except ValueError:
        messagebox.showerror(tr("error"), tr("enter_number"))
        play_sound("error")

def update_ui_language():
    if not root.winfo_exists():
        return
    root.title(tr("title"))
    info_label.config(text=tr("welcome"))
    amount_entry.delete(0, tk.END)
    amount_entry.insert(0, tr("amount_placeholder"))
    trade_button.config(text=tr("trade_btn"))
    new_button.config(text=tr("news_btn"))
    update_button.config(text=tr("update_btn"))
    settings_button.config(text=tr("settings_btn"))
    update_labels(0)
def apply_theme(theme_name):
    global bg_color, fg_color, button_bg, button_fg, animation_running, hue
    stop_animation()
    if theme_name in base_themes:
        theme = base_themes[theme_name]
        bg_color, fg_color, button_bg, button_fg = theme
        if root.winfo_exists():
            root.configure(bg=bg_color)
            for w in [info_label, realmoney_label, crypto_balance_label, coin_count_label,
                      coin_value_label, commission_rate_label, status_label]:
                if w.winfo_exists():
                    w.config(bg=bg_color, fg=fg_color)
            for b in [trade_button, new_button, update_button, settings_button]:
                if b.winfo_exists():
                    b.config(bg=button_bg, fg=button_fg, activebackground=button_fg, activeforeground=button_bg)
    else:
        if theme_name == "AnimatedGradient":
            start_gradient_animation()
        elif theme_name == "NeonPulse":
            start_neon_animation()
def stop_animation():
    global animation_running
    animation_running = False
def start_gradient_animation():
    global animation_running, hue
    animation_running = True
    hue = 0.0
    def animate():
        global hue
        if not animation_running or not root.winfo_exists():
            return
        hue = (hue + 0.01) % 1.0
        rgb = colorsys.hsv_to_rgb(hue, 0.5, 1.0)
        color = "#%02x%02x%02x" % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        root.configure(bg=color)
        for w in [info_label, realmoney_label, crypto_balance_label, coin_count_label,
                  coin_value_label, commission_rate_label, status_label]:
            if w.winfo_exists():
                w.config(bg=color)
        if animation_running and root.winfo_exists():
            root.after(50, animate)
    animate()
def start_neon_animation():
    global animation_running, hue
    animation_running = True
    hue = 0.0
    brightness = 1.0
    direction = -0.02
    def animate():
        nonlocal brightness, direction
        global hue
        if not animation_running or not root.winfo_exists():
            return
        hue = (hue + 0.01) % 1.0
        rgb = colorsys.hsv_to_rgb(hue, 0.7, 1.0)
        color = "#%02x%02x%02x" % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        root.configure(bg=color)
        brightness += direction
        if brightness <= 0.6 or brightness >= 1.0:
            direction *= -1
        text_color = "#%02x%02x%02x" % (int(255*brightness), int(255*brightness*0.8), int(255))
        button_color = "#%02x%02x%02x" % (int(255*brightness*0.7), int(100*brightness), int(255))
        for w in [info_label, realmoney_label, crypto_balance_label, coin_count_label,
                  coin_value_label, commission_rate_label, status_label]:
            if w.winfo_exists():
                w.config(bg=color, fg=text_color)
        for b in [trade_button, new_button, update_button, settings_button]:
            if b.winfo_exists():
                b.config(bg=button_color, fg="white", activebackground="white", activeforeground=button_color)
        if animation_running and root.winfo_exists():
            root.after(50, animate)
    animate()
# === Стили ===
base_themes = {
    "light": ("#F0F0F0", "black", "#4CAF50", "white"),
    "dark": ("#2E2E2E", "white", "#444", "white"),
    "blue": ("#E6F3FF", "#003366", "#66B2FF", "white"),
    "green": ("#E6FFE6", "#006600", "#66FF66", "white"),
    "solarized": ("#FDF6E3", "#657B83", "#B58900", "white"),
    "cyberpunk": ("#1A001A", "#FF66FF", "#9900FF", "white"),
    "ocean": ("#E0FFFF", "#004C66", "#00BFFF", "white"),
    "retro": ("#FFF3E0", "#8B4513", "#FFB347", "white"),
}

animated_themes = {"AnimatedGradient": "🌈 Плавный градиент", "NeonPulse": "⚡ Неоновое свечение"}
realmoney = 100
cryptocoins = 10
vaalue_of_coin = 20
realmoney_in_crypto = cryptocoins * vaalue_of_coin
current_theme = "light"
bg_color, fg_color, button_bg, button_fg = base_themes[current_theme]
def cleanup():
    global animation_running
    animation_running = False
    if 'toast' in globals():
        toast.cleanup()
    save_config()
def update_chart():
    global fig, ax, chart_canvas, price_history
    try:
        ax.clear()
        ax.plot(price_history, linewidth=2)
        ax.set_title("исьормичя ценыг")
        ax.set_xlabel("ходы")
        ax.set_ylabel("цена")
        chart_canvas.draw()
    except Exception as e:
        pass  # или print(e)

def show_main_window():
    loading_frame.destroy()
    global info_label, realmoney_label, crypto_balance_label, coin_count_label, coin_value_label
    global commission_rate_label, trade_button, new_button, update_button, settings_button, status_label, amount_entry
    info_label = tk.Label(root, text=tr("welcome"),
                          font=("Arial", 13, "bold"), bg=bg_color, fg=fg_color)
    info_label.pack(pady=15)
    realmoney_label = tk.Label(root, font=("Arial", 12), bg=bg_color, fg=fg_color)
    crypto_balance_label = tk.Label(root, font=("Arial", 12), bg=bg_color, fg=fg_color)
    coin_count_label = tk.Label(root, font=("Arial", 12), bg=bg_color, fg=fg_color)
    coin_value_label = tk.Label(root, font=("Arial", 12), bg=bg_color, fg=fg_color)
    commission_rate_label = tk.Label(root, font=("Arial", 12), bg=bg_color, fg=fg_color)
    for lbl in [realmoney_label, crypto_balance_label, coin_count_label, coin_value_label, commission_rate_label]:
        lbl.pack(pady=2)
    amount_entry = ttk.Entry(root, font=("Arial", 12), justify="center")
    amount_entry.pack(pady=5)
    amount_entry.insert(0, tr("amount_placeholder"))
    trade_button = tk.Button(root, text=tr("trade_btn"), command=make_trade, font=("Arial", 11, "bold"),
                             bg=button_bg, fg=button_fg)
    trade_button.pack(pady=6)
    new_button = tk.Button(root, text=tr("news_btn"), command=display_news, font=("Arial", 11, "bold"),
                           bg=button_bg, fg=button_fg)
    new_button.pack(pady=6)
    update_button = tk.Button(root, text=tr("update_btn"), command=update_price, font=("Arial", 11, "bold"),
                              bg=button_bg, fg=button_fg)
    update_button.pack(pady=6)
    settings_button = tk.Button(root, text=tr("settings_btn"), command=open_settings, font=("Arial", 11, "bold"),
                                bg=button_bg, fg=button_fg)
    settings_button.pack(pady=6)
    status_label = tk.Label(root, text="", font=("Arial", 11, "italic"), bg=bg_color, fg=fg_color)
    status_label.pack(pady=15)
    global fig, ax, chart_canvas
    chart_frame = tk.Frame(root, bg=bg_color)
    chart_frame.pack(fill="both", expand=True, pady=10)
    fig = Figure(figsize=(4.5, 2.5), dpi=100)
    ax = fig.add_subplot(111)
    chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    chart_canvas.get_tk_widget().pack(fill="both", expand=True)
    update_labels(0)
load_config()
root = tk.Tk()
root.title(tr("title"))
root.geometry("450x550")
root.configure(bg=bg_color)
def on_closing():
    cleanup()
    root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)
atexit.register(cleanup)
toast = Toast(root)
loading_frame = tk.Frame(root, bg="#121212")
loading_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
loading_label = tk.Label(loading_frame, text=tr("loading"), font=("Arial", 15, "bold"),
                         bg="#121212", fg="white")
loading_label.pack(pady=20)
progress = ttk.Progressbar(loading_frame, orient="horizontal", mode="determinate", length=300)
progress.pack(pady=20)
def animate_loading(value=0):
    if value < 100 and root.winfo_exists():
        progress["value"] = value
        root.after(0, animate_loading, value + 2)
    elif root.winfo_exists():
        show_main_window()
animate_loading()
root.mainloop()
