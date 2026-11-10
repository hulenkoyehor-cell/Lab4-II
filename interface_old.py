

import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# Імпортуємо функцію ask та генератор звіту з lab3.py
from lab3 import ask, build_report_content, MODEL_NAME

# Словник для збереження результатів усіх завдань
data = {
    "task1": [],
    "task2": {},
    "task3": {},
    "task4": {},
    "general_conclusions": ""
}


def send_async(prompt, system, btn, status_lbl, result_widget):
    cleaned_prompt = prompt.strip() if prompt else ""
    if not cleaned_prompt:
        messagebox.showwarning("Увага", "Будь ласка, введіть prompt!")
        return

    btn.config(state=tk.DISABLED)
    status_lbl.config(text="Запит обробляється моделлю...", foreground="blue")
    result_widget.delete("1.0", tk.END)
    result_widget.insert(tk.END, "Зачекайте, модель генерує відповідь...")

    def worker():
        answer = ask(cleaned_prompt, system=system)

        def on_done():
            result_widget.delete("1.0", tk.END)
            result_widget.insert(tk.END, answer)
            if answer.startswith("Помилка:"):
                status_lbl.config(text=answer if len(answer) <= 60 else answer[:57] + "...", foreground="red")
            else:
                status_lbl.config(text="Відповідь отримано!", foreground="green")
            btn.config(state=tk.NORMAL)

        root.after(0, on_done)

    threading.Thread(target=worker, daemon=True).start()



# Вкладка 1: П'ять типів запитів

TYPES_LIST = ["Пояснення", "Генерація тексту", "Переклад", "Узагальнення", "Список"]

def build_tab1(parent):
    frame = ttk.Frame(parent, padding=10)
    parent.add(frame, text="1. Типи запитів")

    # Вибір типу
    top_f = ttk.Frame(frame)
    top_f.pack(fill=tk.X, pady=5)
    ttk.Label(top_f, text="Тип запиту:").pack(side=tk.LEFT)
    combo_type = ttk.Combobox(top_f, values=TYPES_LIST, state="readonly", width=25)
    combo_type.current(0)
    combo_type.pack(side=tk.LEFT, padx=10)

    lbl_count = ttk.Label(top_f, text="Збережено: 0/5", foreground="gray")
    lbl_count.pack(side=tk.RIGHT)

    # Поле вводу prompt (порожнє на старті)
    ttk.Label(frame, text="Ваш Prompt:").pack(anchor="w")
    txt_prompt = scrolledtext.ScrolledText(frame, height=4, wrap=tk.WORD)
    txt_prompt.pack(fill=tk.X, pady=3)

    # Кнопка та статус
    action_f = ttk.Frame(frame)
    action_f.pack(fill=tk.X, pady=4)
    btn_send = ttk.Button(action_f, text="Надіслати запит до моделі")
    btn_send.pack(side=tk.LEFT)
    lbl_status = ttk.Label(action_f, text="", font=("Arial", 9))
    lbl_status.pack(side=tk.LEFT, padx=10)

    # Поле відповіді
    ttk.Label(frame, text="Відповідь моделі:").pack(anchor="w")
    txt_result = scrolledtext.ScrolledText(frame, height=7, wrap=tk.WORD)
    txt_result.pack(fill=tk.BOTH, expand=True, pady=3)

    # Короткий аналіз
    ttk.Label(frame, text="Короткий аналіз (1–3 речення):").pack(anchor="w")
    ent_analysis = ttk.Entry(frame, width=80)
    ent_analysis.pack(fill=tk.X, pady=3)

    # Функції дій
    def on_send():
        p = txt_prompt.get("1.0", "end-1c").strip()
        send_async(p, None, btn_send, lbl_status, txt_result)
    btn_send.config(command=on_send)

    def on_save_item():
        cur_type = combo_type.get()
        p = txt_prompt.get("1.0", "end-1c").strip()
        r = txt_result.get("1.0", "end-1c").strip()
        a = ent_analysis.get().strip()

        if not p or not r:
            messagebox.showwarning("Увага", "Спочатку введіть prompt та отримайте відповідь!")
            return

        if r.startswith("Помилка:"):
            messagebox.showerror("Помилка", "Неможливо зберегти у звіт відповідь з помилкою!")
            return

        # Видаляємо старий запис цього типу, якщо був
        data["task1"] = [item for item in data["task1"] if item["type"] != cur_type]
        idx = TYPES_LIST.index(cur_type) + 1
        data["task1"].append({"num": idx, "type": cur_type, "prompt": p, "result": r, "analysis": a})
        data["task1"].sort(key=lambda x: x["num"])

        lbl_count.config(text=f"Збережено: {len(data['task1'])}/5", foreground="green")
        messagebox.showinfo("Збережено", f"Запит для '{cur_type}' успішно збережено!")

    ttk.Button(frame, text="Зберегти цей тип у звіт", command=on_save_item).pack(pady=5)



# Вкладка 2: Zero-shot vs Few-shot

def build_tab2(parent):
    frame = ttk.Frame(parent, padding=10)
    parent.add(frame, text="2. Zero vs Few-shot")

    # Контейнер на 2 колонки
    cols = ttk.Frame(frame)
    cols.pack(fill=tk.BOTH, expand=True)

    # Ліва колонка: Zero-shot
    col1 = ttk.LabelFrame(cols, text=" Zero-shot (без прикладів) ", padding=5)
    col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    ttk.Label(col1, text="Zero-shot Prompt:").pack(anchor="w")
    p1 = scrolledtext.ScrolledText(col1, height=4, wrap=tk.WORD)
    p1.pack(fill=tk.X, pady=2)

    btn1 = ttk.Button(col1, text="Надіслати Zero-shot")
    btn1.pack(anchor="w", pady=2)
    s1 = ttk.Label(col1, text="", font=("Arial", 8))
    s1.pack(anchor="w")

    ttk.Label(col1, text="Відповідь:").pack(anchor="w")
    r1 = scrolledtext.ScrolledText(col1, height=6, wrap=tk.WORD)
    r1.pack(fill=tk.BOTH, expand=True, pady=2)
    btn1.config(command=lambda: send_async(p1.get("1.0", "end-1c").strip(), None, btn1, s1, r1))

    # Права колонка: Few-shot
    col2 = ttk.LabelFrame(cols, text=" Few-shot (з 2–3 прикладами) ", padding=5)
    col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    ttk.Label(col2, text="Few-shot Prompt:").pack(anchor="w")
    p2 = scrolledtext.ScrolledText(col2, height=4, wrap=tk.WORD)
    p2.pack(fill=tk.X, pady=2)

    btn2 = ttk.Button(col2, text="Надіслати Few-shot")
    btn2.pack(anchor="w", pady=2)
    s2 = ttk.Label(col2, text="", font=("Arial", 8))
    s2.pack(anchor="w")

    ttk.Label(col2, text="Відповідь:").pack(anchor="w")
    r2 = scrolledtext.ScrolledText(col2, height=6, wrap=tk.WORD)
    r2.pack(fill=tk.BOTH, expand=True, pady=2)
    btn2.config(command=lambda: send_async(p2.get("1.0", "end-1c").strip(), None, btn2, s2, r2))

    # Висновок
    ttk.Label(frame, text="Висновок (порівняння Zero-shot та Few-shot):").pack(anchor="w", pady=(8, 2))
    ent_concl = ttk.Entry(frame, width=90)
    ent_concl.pack(fill=tk.X, pady=2)

    def on_save_t2():
        zp = p1.get("1.0", "end-1c").strip()
        zr = r1.get("1.0", "end-1c").strip()
        fp = p2.get("1.0", "end-1c").strip()
        fr = r2.get("1.0", "end-1c").strip()
        concl = ent_concl.get().strip()

        if not zp or not fp:
            messagebox.showwarning("Увага", "Будь ласка, заповніть обидва поля: Zero-shot та Few-shot prompt!")
            return

        if not zr or not fr:
            messagebox.showwarning("Увага", "Отримайте відповіді моделі для обох запитів перед збереженням!")
            return

        if zr.startswith("Помилка:") or fr.startswith("Помилка:"):
            messagebox.showerror("Помилка", "Неможливо зберегти у звіт відповіді з помилкою!")
            return

        data["task2"] = {
            "zero_prompt": zp,
            "zero_result": zr,
            "few_prompt": fp,
            "few_result": fr,
            "conclusion": concl
        }
        messagebox.showinfo("Збережено", "Завдання 2 збережено у пам'яті!")

    ttk.Button(frame, text="Зберегти Завдання 2", command=on_save_t2).pack(pady=5)


# ====================================================
# Вкладка 3: Удосконалення prompt
# ====================================================
def build_tab3(parent):
    frame = ttk.Frame(parent, padding=10)
    parent.add(frame, text="3. Удосконалення")

    cols = ttk.Frame(frame)
    cols.pack(fill=tk.BOTH, expand=True)

    # Початковий prompt
    col1 = ttk.LabelFrame(cols, text=" Початковий (простий) prompt ", padding=5)
    col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    ttk.Label(col1, text="Prompt:").pack(anchor="w")
    p1 = scrolledtext.ScrolledText(col1, height=4, wrap=tk.WORD)
    p1.pack(fill=tk.X, pady=2)

    btn1 = ttk.Button(col1, text="Надіслати початковий")
    btn1.pack(anchor="w", pady=2)
    s1 = ttk.Label(col1, text="", font=("Arial", 8))
    s1.pack(anchor="w")

    ttk.Label(col1, text="Відповідь:").pack(anchor="w")
    r1 = scrolledtext.ScrolledText(col1, height=6, wrap=tk.WORD)
    r1.pack(fill=tk.BOTH, expand=True, pady=2)
    btn1.config(command=lambda: send_async(p1.get("1.0", "end-1c").strip(), None, btn1, s1, r1))

    # Вдосконалений prompt
    col2 = ttk.LabelFrame(cols, text=" Вдосконалений prompt ", padding=5)
    col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    ttk.Label(col2, text="Prompt:").pack(anchor="w")
    p2 = scrolledtext.ScrolledText(col2, height=4, wrap=tk.WORD)
    p2.pack(fill=tk.X, pady=2)

    btn2 = ttk.Button(col2, text="Надіслати вдосконалений")
    btn2.pack(anchor="w", pady=2)
    s2 = ttk.Label(col2, text="", font=("Arial", 8))
    s2.pack(anchor="w")

    ttk.Label(col2, text="Відповідь:").pack(anchor="w")
    r2 = scrolledtext.ScrolledText(col2, height=6, wrap=tk.WORD)
    r2.pack(fill=tk.BOTH, expand=True, pady=2)
    btn2.config(command=lambda: send_async(p2.get("1.0", "end-1c").strip(), None, btn2, s2, r2))

    # Висновок
    ttk.Label(frame, text="Висновок щодо покращення prompt:").pack(anchor="w", pady=(8, 2))
    ent_concl = ttk.Entry(frame, width=90)
    ent_concl.pack(fill=tk.X, pady=2)

    def on_save_t3():
        ip = p1.get("1.0", "end-1c").strip()
        ir = r1.get("1.0", "end-1c").strip()
        imp_p = p2.get("1.0", "end-1c").strip()
        imp_r = r2.get("1.0", "end-1c").strip()
        concl = ent_concl.get().strip()

        if not ip or not imp_p:
            messagebox.showwarning("Увага", "Будь ласка, введіть початковий та вдосконалений prompt!")
            return

        if not ir or not imp_r:
            messagebox.showwarning("Увага", "Отримайте відповіді моделі для обох запитів перед збереженням!")
            return

        if ir.startswith("Помилка:") or imp_r.startswith("Помилка:"):
            messagebox.showerror("Помилка", "Неможливо зберегти у звіт відповіді з помилкою!")
            return

        data["task3"] = {
            "initial_prompt": ip,
            "initial_result": ir,
            "improved_prompt": imp_p,
            "improved_result": imp_r,
            "conclusion": concl
        }
        messagebox.showinfo("Збережено", "Завдання 3 збережено у пам'яті!")

    ttk.Button(frame, text="Зберегти Завдання 3", command=on_save_t3).pack(pady=5)



# Вкладка 4: Системна роль

def build_tab4(parent):
    frame = ttk.Frame(parent, padding=10)
    parent.add(frame, text="4. Системна роль")

    # Задача
    ttk.Label(frame, text="Базове запитання/задача (однакова для всіх ролей):").pack(anchor="w")
    txt_task = scrolledtext.ScrolledText(frame, height=3, wrap=tk.WORD)
    txt_task.pack(fill=tk.X, pady=2)

    roles_frame = ttk.Frame(frame)
    roles_frame.pack(fill=tk.BOTH, expand=True, pady=5)

    entries_role = []
    texts_result = []

    # 3 ролі
    for i in range(1, 4):
        rf = ttk.LabelFrame(roles_frame, text=f" Роль #{i} ", padding=5)
        rf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)

        ttk.Label(rf, text="System instruction:").pack(anchor="w")
        e_role = ttk.Entry(rf)
        e_role.pack(fill=tk.X, pady=2)
        entries_role.append(e_role)

        btn_r = ttk.Button(rf, text=f"Запустити роль #{i}")
        btn_r.pack(anchor="w", pady=2)
        lbl_s = ttk.Label(rf, text="", font=("Arial", 8))
        lbl_s.pack(anchor="w")

        res_box = scrolledtext.ScrolledText(rf, height=6, wrap=tk.WORD)
        res_box.pack(fill=tk.BOTH, expand=True, pady=2)
        texts_result.append(res_box)

        # Прив'язка кнопки до запуску (роль передається через system_instruction)
        def make_handler(idx=i-1, b=btn_r, s=lbl_s, r_box=res_box):
            def handler():
                task_text = txt_task.get("1.0", "end-1c").strip()
                role_text = entries_role[idx].get().strip()
                if not task_text:
                    messagebox.showwarning("Увага", "Будь ласка, введіть базове запитання/задачу!")
                    return
                if not role_text:
                    messagebox.showwarning("Увага", f"Будь ласка, вкажіть системну роль #{idx+1}!")
                    return
                send_async(task_text, role_text, b, s, r_box)
            return handler
        btn_r.config(command=make_handler())

    # Висновок про вплив ролі
    ttk.Label(frame, text="Висновок про вплив ролі на відповіді:").pack(anchor="w", pady=(5, 2))
    ent_concl = ttk.Entry(frame, width=90)
    ent_concl.pack(fill=tk.X, pady=2)

    def on_save_t4():
        task_text = txt_task.get("1.0", "end-1c").strip()
        if not task_text:
            messagebox.showwarning("Увага", "Будь ласка, введіть базове запитання/задачу!")
            return

        roles_list = []
        for i in range(3):
            role_text = entries_role[i].get().strip()
            res_text = texts_result[i].get("1.0", "end-1c").strip()

            if not role_text or not res_text:
                messagebox.showwarning("Увага", f"Будь ласка, заповніть роль #{i+1} та отримайте відповідь!")
                return

            if res_text.startswith("Помилка:"):
                messagebox.showerror("Помилка", f"Неможливо зберегти у звіт відповідь з помилкою (Роль #{i+1})!")
                return

            roles_list.append({
                "role": role_text,
                "result": res_text
            })

        data["task4"] = {
            "task_prompt": task_text,
            "roles": roles_list,
            "conclusion": ent_concl.get().strip()
        }
        messagebox.showinfo("Збережено", "Завдання 4 збережено у пам'яті!")

    ttk.Button(frame, text="Зберегти Завдання 4", command=on_save_t4).pack(pady=5)



# Вкладка 5: Звіт report.md

def build_tab5(parent):
    frame = ttk.Frame(parent, padding=10)
    parent.add(frame, text="5. Звіт report.md")

    ttk.Label(frame, text="Загальні висновки до лабораторної роботи:").pack(anchor="w")
    txt_general = scrolledtext.ScrolledText(frame, height=4, wrap=tk.WORD)
    txt_general.pack(fill=tk.X, pady=4)

    preview_box = scrolledtext.ScrolledText(frame, height=12, wrap=tk.WORD)

    def on_generate_report():
        data["general_conclusions"] = txt_general.get("1.0", "end-1c").strip()
        report_md = build_report_content(data)

        # Запис у файл
        with open("report.md", "w", encoding="utf-8") as f:
            f.write(report_md)

        # Відображення у вікні перегляду
        preview_box.delete("1.0", tk.END)
        preview_box.insert(tk.END, report_md)

        messagebox.showinfo("Успіх", "Звіт успішно згенеровано та збережено у файл report.md!")

    btn_report = ttk.Button(frame, text="Сформувати та зберегти звіт у report.md", command=on_generate_report)
    btn_report.pack(pady=5)

    ttk.Label(frame, text="Попередній перегляд сформованого звіту:").pack(anchor="w", pady=(8, 2))
    preview_box.pack(fill=tk.BOTH, expand=True, pady=2)



# Головне вікно програми

root = tk.Tk()
root.title("Лабораторна робота №3 — Prompt Engineering")
root.geometry("880x680")

# Заголовок
header = ttk.Label(root, text="Лабораторна робота №3: Основи Prompt Engineering",
                   font=("Arial", 13, "bold"))
header.pack(pady=8)

# Вкладки
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

build_tab1(notebook)
build_tab2(notebook)
build_tab3(notebook)
build_tab4(notebook)
build_tab5(notebook)

root.mainloop()
