import tkinter as tk
from tkinter import ttk, messagebox
import time
from random import randint, choice
import colorsys
import winsound

# === Константы ===
COMMISSION_RATE = 0.01
leverage = 1
max_price_change = 15
news = ""
price_change = 0
price_history = []
time_points = []
sound_enabled = True  # вкл/выкл звук

animation_running = False
hue = 0.0


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
        winsound.Beep(freq, dur)


# === Новости и рынок ===
def generate_news():
    global max_price_change
    news_types = ["Положительная", "Отрицательная", "Нейтральная"]
    news_type = choice(news_types)
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

    if news_type == "Положительная":
        return choice(positive), randint(1, max_price_change)
    elif news_type == "Отрицательная":
        return choice(negative), randint(-max_price_change, -1)
    else:
        return choice(neutral), randint(-3, 3)


def display_news():
    global news, price_change
    if news:
        status_label.config(text="⚠️ Новость уже активна — обновите курс перед новой!")
        play_sound("error")
        return
    news, price_change = generate_news()
    status_label.config(text=f"📰 Новость: {news}")
    play_sound("news")
    new_button.config(state="disabled")


def update_price():
    global vaalue_of_coin, realmoney_in_crypto, cryptocoins, realmoney, price_history, time_points, price_change, news
    try:
        if news:
            percent_change = price_change / 100.0
        else:
            random_change = randint(-max_price_change // 2, max_price_change // 2)
            percent_change = random_change / 100.0
            status_label.config(text="📉 Цена изменилась случайно.")
        vaalue_of_coin += vaalue_of_coin * percent_change
        vaalue_of_coin = max(0.01, vaalue_of_coin)
        realmoney_in_crypto = cryptocoins * vaalue_of_coin
        update_labels(price_change if news else random_change)
        price_history.append(vaalue_of_coin)
        time_points.append(len(price_history))
        news = ""
        price_change = 0
        new_button.config(state="normal")
        play_sound("update")
    except Exception as e:
        play_sound("error")
        messagebox.showerror("Ошибка", str(e))


def make_trade():
    global realmoney, cryptocoins, realmoney_in_crypto, vaalue_of_coin, COMMISSION_RATE, leverage
    try:
        amount = float(amount_entry.get())
        if amount == 0:
            status_label.config(text="Введите сумму больше 0.")
            play_sound("error")
            return
        amount_with_leverage = amount * leverage
        if amount > 0:
            total_cost = amount_with_leverage + amount_with_leverage * COMMISSION_RATE
            if total_cost > realmoney:
                messagebox.showerror("Ошибка", "Недостаточно средств!")
                play_sound("error")
                return
            coins = amount_with_leverage / vaalue_of_coin
            cryptocoins += coins
            realmoney -= total_cost
            status_label.config(text=f"💸 Куплено {coins:.2f} коинов.")
            play_sound("buy")
        else:
            amount = abs(amount)
            coins_to_sell = amount / vaalue_of_coin
            if coins_to_sell > cryptocoins:
                messagebox.showerror("Ошибка", "Недостаточно коинов!")
                play_sound("error")
                return
            cryptocoins -= coins_to_sell
            revenue = amount - amount * COMMISSION_RATE
            realmoney += revenue
            status_label.config(text=f"💰 Продано {coins_to_sell:.2f} коинов.")
            play_sound("sell")
        realmoney_in_crypto = cryptocoins * vaalue_of_coin
        update_labels(0)
    except ValueError:
        messagebox.showerror("Ошибка", "Введите число.")
        play_sound("error")


# === Интерфейс ===
def update_labels(change):
    realmoney_label.config(text=f"💵 Реальные деньги: {realmoney:.2f}")
    crypto_balance_label.config(text=f"🪙 Крипто в $: {realmoney_in_crypto:.2f}")
    coin_count_label.config(text=f"Количество коинов: {cryptocoins:.2f}")
    coin_value_label.config(text=f"1 коин = {vaalue_of_coin:.2f} ({change:+.2f}%)")
    commission_rate_label.config(
        text=f"Комиссия: {COMMISSION_RATE*100:.2f}% | Плечо: {leverage:.2f}x"
    )


def open_settings():
    global settings_window
    settings_window = tk.Toplevel(root)
    settings_window.title("⚙️ Настройки")
    settings_window.geometry("340x650")
    settings_window.configure(bg=bg_color)
    ttk.Label(settings_window, text="Настройки параметров", font=("Arial", 13, "bold")).pack(pady=10)

    def add_entry(label, var):
        ttk.Label(settings_window, text=label).pack()
        entry = ttk.Entry(settings_window)
        entry.insert(0, str(var))
        entry.pack(pady=3)
        return entry

    global realmoney_entry, cryptocoins_entry, coin_value_entry, max_change_entry, commission_rate_entry, leverage_entry, theme_var, sound_var
    realmoney_entry = add_entry("Баланс (реальные деньги):", realmoney)
    cryptocoins_entry = add_entry("Количество криптокоинов:", cryptocoins)
    coin_value_entry = add_entry("Цена коина:", vaalue_of_coin)
    max_change_entry = add_entry("Макс. изменение (%):", max_price_change)
    commission_rate_entry = add_entry("Комиссия (0.01 = 1%):", COMMISSION_RATE)
    leverage_entry = add_entry("Плечо:", leverage)

    ttk.Label(settings_window, text="🎨 Обычные темы:").pack(pady=5)
    theme_var = tk.StringVar(value=current_theme)
    for t in base_themes.keys():
        ttk.Radiobutton(settings_window, text=t.capitalize(), variable=theme_var, value=t).pack(anchor="w", padx=20)

    ttk.Label(settings_window, text="🌈 Анимированные темы:").pack(pady=5)
    for t in animated_themes.keys():
        ttk.Radiobutton(settings_window, text=t, variable=theme_var, value=t).pack(anchor="w", padx=20)

    ttk.Label(settings_window, text="🔊 Звук:").pack(pady=5)
    sound_var = tk.BooleanVar(value=sound_enabled)
    ttk.Checkbutton(settings_window, text="Включить звук", variable=sound_var).pack(anchor="w", padx=20)

    ttk.Button(settings_window, text="Применить", command=apply_settings).pack(pady=10)


def apply_settings():
    global realmoney, cryptocoins, vaalue_of_coin, max_price_change, COMMISSION_RATE, leverage, current_theme, sound_enabled
    try:
        realmoney = float(realmoney_entry.get())
        cryptocoins = float(cryptocoins_entry.get())
        vaalue_of_coin = float(coin_value_entry.get())
        max_price_change = int(max_change_entry.get())
        COMMISSION_RATE = float(commission_rate_entry.get())
        leverage = float(leverage_entry.get())
        sound_enabled = sound_var.get()
        theme = theme_var.get()
        if theme != current_theme:
            apply_theme(theme)
            current_theme = theme
        update_labels(0)
        settings_window.destroy()
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректные данные!")
        play_sound("error")


# === Темы и анимации ===
def apply_theme(theme_name):
    global bg_color, fg_color, button_bg, button_fg, animation_running, hue
    stop_animation()
    if theme_name in base_themes:
        theme = base_themes[theme_name]
        bg_color, fg_color, button_bg, button_fg = theme
        root.configure(bg=bg_color)
        for w in [info_label, realmoney_label, crypto_balance_label, coin_count_label,
                  coin_value_label, commission_rate_label, status_label]:
            w.config(bg=bg_color, fg=fg_color)
        for b in [trade_button, new_button, update_button, settings_button]:
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
        if not animation_running:
            return
        hue = (hue + 0.01) % 1.0
        rgb = colorsys.hsv_to_rgb(hue, 0.5, 1.0)
        color = "#%02x%02x%02x" % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        root.configure(bg=color)
        for w in [info_label, realmoney_label, crypto_balance_label, coin_count_label,
                  coin_value_label, commission_rate_label, status_label]:
            w.config(bg=color)
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
        if not animation_running:
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
            w.config(bg=color, fg=text_color)
        for b in [trade_button, new_button, update_button, settings_button]:
            b.config(bg=button_color, fg="white", activebackground="white", activeforeground=button_color)
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


# === Данные ===
realmoney = 100
cryptocoins = 10
vaalue_of_coin = 20
realmoney_in_crypto = cryptocoins * vaalue_of_coin
current_theme = "light"
bg_color, fg_color, button_bg, button_fg = base_themes[current_theme]


# === Основное окно ===
def show_main_window():
    loading_frame.destroy()
    global info_label, realmoney_label, crypto_balance_label, coin_count_label, coin_value_label
    global commission_rate_label, trade_button, new_button, update_button, settings_button, status_label, amount_entry
    info_label = tk.Label(root, text="📈 Добро пожаловать в Crypto Trading Simulator v2.4!",
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
    amount_entry.insert(0, "Введите сумму (+покупка / -продажа)")
    trade_button = tk.Button(root, text="💸 Купить / Продать", command=make_trade, font=("Arial", 11, "bold"),
                             bg=button_bg, fg=button_fg)
    trade_button.pack(pady=6)
    new_button = tk.Button(root, text="📰 Свежая новость", command=display_news, font=("Arial", 11, "bold"),
                           bg=button_bg, fg=button_fg)
    new_button.pack(pady=6)
    update_button = tk.Button(root, text="🔄 Обновить курс", command=update_price, font=("Arial", 11, "bold"),
                              bg=button_bg, fg=button_fg)
    update_button.pack(pady=6)
    settings_button = tk.Button(root, text="⚙️ Настройки", command=open_settings, font=("Arial", 11, "bold"),
                                bg=button_bg, fg=button_fg)
    settings_button.pack(pady=6)
    status_label = tk.Label(root, text="", font=("Arial", 11, "italic"), bg=bg_color, fg=fg_color)
    status_label.pack(pady=15)
    update_labels(0)


root = tk.Tk()
root.title("💹 Crypto Trading Simulator v2.4")
root.geometry("450x550")
root.configure(bg=bg_color)
loading_frame = tk.Frame(root, bg="#121212")
loading_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
loading_label = tk.Label(loading_frame, text="Загрузка игры...", font=("Arial", 15, "bold"),
                         bg="#121212", fg="white")
loading_label.pack(pady=20)
progress = ttk.Progressbar(loading_frame, orient="horizontal", mode="determinate", length=300)
progress.pack(pady=20)


def animate_loading(value=0):
    if value < 100:
        progress["value"] = value
        root.after(20, animate_loading, value + 2)
    else:
        show_main_window()


animate_loading()
root.mainloop()
