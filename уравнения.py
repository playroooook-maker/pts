import re
import tkinter as tk
from tkinter import messagebox
from sympy import symbols, Eq, solve, sympify
def solve_equation():
    equ = entry.get().strip()
    if '=' not in equ:
        messagebox.showerror("ошибка", "уравнение должно иметь =.")
        return
    variables = set(re.findall(r'[a-zA-Z]+', equ))
    if not variables:
        messagebox.showerror("ошибка", "нужна переменная.")
        return
    sym_vars = symbols(list(variables))
    equ = re.sub(r'(?<=\d)(?=[a-zA-Z])', '*', equ)
    parts = equ.split('=')
    if len(parts) != 2:
        messagebox.showerror("ошибка", "в уравнении только одно =.")
        return
    l, r = parts
    try:
        l_expr = sympify(l)
        r_expr = sympify(r)
    except Exception as e:
        messagebox.showerror("ошибка", f"нельзя такое выражение:\n{e}")
        return
    solutions = solve(Eq(l_expr, r_expr), sym_vars)
    if not solutions:
        result_label.config(text="нет реш.")
    else:
        result_text = "\n".join([str(sol) for sol in solutions])
        result_label.config(text=f"решение:\n{result_text}")
root = tk.Tk()
root.title("уравнения")
tk.Label(root, text="уравнение:").pack(pady=5)
entry = tk.Entry(root, width=40)
entry.pack(pady=5)
solve_button = tk.Button(root, text="решение", command=solve_equation)
solve_button.pack(pady=10)
result_label = tk.Label(root, text="", justify="left")
result_label.pack(pady=5)
root.mainloop()
