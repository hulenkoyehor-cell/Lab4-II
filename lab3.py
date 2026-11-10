import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Завантажуємо змінні оточення з файлу .env
load_dotenv()


MODEL_NAME = "gemini-3.8-flash"


def get_client():
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        return None
    try:
        return genai.Client(api_key=api_key.strip())
    except Exception as e:
        print(f"\n[ПОМИЛКА] Не вдалося створити клієнт API: {e}")
        return None


def ask(prompt, system=None):
    
    cleaned_prompt = prompt.strip() if prompt else ""
    if not cleaned_prompt:
        return "Помилка: Порожній запит prompt."

    client = get_client()
    if not client:
        return "Помилка: API-ключ не налаштовано у файлі .env (перевірте GEMINI_API_KEY)"

    # Вимикаємо "thinking" щоб модель відповідала швидше
    config_with_thinking = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        system_instruction=system.strip() if system and system.strip() else None
    )
    config_without_thinking = types.GenerateContentConfig(
        system_instruction=system.strip() if system and system.strip() else None
    )

   
    models_to_try = [MODEL_NAME, "gemini-3.5-flash", "gemini-3.5-flash-lite"]

    last_error = None
    for m in models_to_try:
        
        for cfg in [config_with_thinking, config_without_thinking]:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=cleaned_prompt,
                    config=cfg
                )
                if response and response.text:
                    return response.text
            except Exception as api_err:
                last_error = api_err
                continue

    if "PERMISSION_DENIED" in str(last_error) or "403" in str(last_error):
        return (
            "Помилка: 403 PERMISSION_DENIED. Доступ для поточного Google Cloud проєкту заблоковано "
            "(Your project has been denied access). Будь ласка, створіть новий безкоштовний API-ключ "
            "на сайті https://aistudio.google.com/apikey та вставте його у файл .env"
        )
    return f"Помилка: {last_error}"


def input_text(prompt_message, multiline=True):
    
    print(f"\n{prompt_message}")
    if not multiline:
        return input("> ").strip()

    print("[Підказка: введіть текст. Завершити: натисніть Enter на порожньому рядку або введіть END]")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        # Завершення введення ключовим словом END
        if line.strip().upper() == "END":
            break
        # Завершення введення, якщо рядок закінчується на END
        if line.endswith("END"):
            lines.append(line[:-3])
            break
        # Порожній рядок завершує введення, якщо текст уже вводився
        if line == "":
            if lines:
                break
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def to_table_cell(text):
    
    if not text:
        return "-"
    return str(text).replace("|", "\\|").replace("\r\n", "\n").replace("\n", "<br>")


def run_task1(data):
    
    print("\n" + "=" * 50)
    print("ЗАВДАННЯ 1: П'ять типів запитів")
    print("=" * 50)

    types_list = [
        "Пояснення",
        "Генерація тексту",
        "Переклад",
        "Узагальнення",
        "Список"
    ]

    task1_results = []
    for i, type_name in enumerate(types_list, start=1):
        print(f"\n--- [{i}/5] Тип запиту: {type_name} ---")
        prompt = input_text(f"Введіть ваш prompt для типу '{type_name}':")
        if not prompt:
            print("Запит пропущено.")
            continue

        print("\nНадсилання запиту до моделі...")
        answer = ask(prompt)
        print("\nВІДПОВІДЬ МОДЕЛІ:")
        print("-" * 40)
        print(answer)
        print("-" * 40)

        analysis = input_text("Введіть ваш короткий аналіз відповіді (1–3 речення):", multiline=False)

        task1_results.append({
            "num": i,
            "type": type_name,
            "prompt": prompt,
            "result": answer,
            "analysis": analysis
        })

    data["task1"] = task1_results
    print("\nЗавдання 1 успішно збережено!")


def run_task2(data):
   
    print("\n" + "=" * 50)
    print("ЗАВДАННЯ 2: Zero-shot vs Few-shot")
    print("=" * 50)

    # 1. Zero-shot
    print("\n--- 1. Zero-shot prompt ---")
    zero_prompt = input_text("Введіть ваш Zero-shot prompt (без прикладів):")
    if not zero_prompt:
        print("Скасовано.")
        return

    print("\nНадсилання Zero-shot запиту...")
    zero_result = ask(zero_prompt)
    print("\nВІДПОВІДЬ МОДЕЛІ (Zero-shot):")
    print("-" * 40)
    print(zero_result)
    print("-" * 40)

    # 2. Few-shot
    print("\n--- 2. Few-shot prompt ---")
    few_prompt = input_text("Введіть ваш Few-shot prompt (з 2–3 прикладами):")
    if not few_prompt:
        print("Скасовано.")
        return

    print("\nНадсилання Few-shot запиту...")
    few_result = ask(few_prompt)
    print("\nВІДПОВІДЬ МОДЕЛІ (Few-shot):")
    print("-" * 40)
    print(few_result)
    print("-" * 40)

    # 3. Висновок
    conclusion = input_text("Введіть ваш висновок щодо порівняння Zero-shot та Few-shot:")

    data["task2"] = {
        "zero_prompt": zero_prompt,
        "zero_result": zero_result,
        "few_prompt": few_prompt,
        "few_result": few_result,
        "conclusion": conclusion
    }
    print("\nЗавдання 2 успішно збережено!")


def run_task3(data):
    """Завдання 3: Удосконалення prompt."""
    print("\n" + "=" * 50)
    print("ЗАВДАННЯ 3: Удосконалення prompt")
    print("=" * 50)

    # 1. Початковий prompt
    print("\n--- 1. Початковий prompt ---")
    initial_prompt = input_text("Введіть початковий (базовий/простий) prompt:")
    if not initial_prompt:
        print("Скасовано.")
        return

    print("\nНадсилання початкового запиту...")
    initial_result = ask(initial_prompt)
    print("\nВІДПОВІДЬ МОДЕЛІ (Початковий prompt):")
    print("-" * 40)
    print(initial_result)
    print("-" * 40)

    # 2. Вдосконалений prompt
    print("\n--- 2. Вдосконалений prompt ---")
    improved_prompt = input_text("Введіть вдосконалений prompt (з контекстом, обмеженнями, форматом тощо):")
    if not improved_prompt:
        print("Скасовано.")
        return

    print("\nНадсилання вдосконаленого запиту...")
    improved_result = ask(improved_prompt)
    print("\nВІДПОВІДЬ МОДЕЛІ (Вдосконалений prompt):")
    print("-" * 40)
    print(improved_result)
    print("-" * 40)

    # 3. Висновок
    conclusion = input_text("Введіть ваш висновок щодо покращення prompt:")

    data["task3"] = {
        "initial_prompt": initial_prompt,
        "initial_result": initial_result,
        "improved_prompt": improved_prompt,
        "improved_result": improved_result,
        "conclusion": conclusion
    }
    print("\nЗавдання 3 успішно збережено!")


def run_task4(data):
   
    print("\n" + "=" * 50)
    print("ЗАВДАННЯ 4: Системна роль")
    print("=" * 50)

    # Задача вводиться один раз
    task_prompt = input_text("Введіть задачу/запитання (буде передано кожній ролі):")
    if not task_prompt:
        print("Скасовано.")
        return

    roles = []
    for i in range(1, 4):
        print(f"\n--- Роль #{i} ---")
        role_instruction = input_text(f"Введіть системну роль #{i} (system instruction):")
        if not role_instruction:
            print("Пропущено.")
            continue

        print(f"\nНадсилання запиту для ролі #{i}...")
        answer = ask(task_prompt, system=role_instruction)
        print(f"\nВІДПОВІДЬ МОДЕЛІ (Роль #{i}: {role_instruction}):")
        print("-" * 40)
        print(answer)
        print("-" * 40)

        roles.append({
            "role": role_instruction,
            "result": answer
        })

    conclusion = input_text("Введіть ваш висновок про вплив системної ролі на відповідь моделі:")

    data["task4"] = {
        "task_prompt": task_prompt,
        "roles": roles,
        "conclusion": conclusion
    }
    print("\nЗавдання 4 успішно збережено!")


def build_report_content(data):
  
    lines = []
    lines.append("# Лабораторна робота № 3")
    lines.append("## Тема: Робота з LLM через API. Основи Prompt Engineering\n")
    lines.append("### Мета роботи:")
    lines.append("Ознайомитися з основами взаємодії з великими мовними моделями (LLM) через API, ")
    lines.append("опанувати практичні навички складання промптів різних типів, дослідити техніки ")
    lines.append("Zero-shot, Few-shot та використання системних ролей для управління відповідями моделі.\n")
    lines.append("### Використана LLM:")
    lines.append(f"- **Модель:** {MODEL_NAME}")
    lines.append("- **Бібліотека:** google-genai\n")
    lines.append("---\n")

    #  Завдання 1
    lines.append("## 1. Приклади запитів та результати (П'ять типів запитів)\n")
    lines.append("| № | Тип завдання | Prompt | Результат | Аналіз |")
    lines.append("|---|---|---|---|---|")
    if data.get("task1"):
        for item in data["task1"]:
            num = item["num"]
            t_type = item["type"]
            prompt_cell = to_table_cell(item["prompt"])
            result_cell = to_table_cell(item["result"])
            analysis_cell = to_table_cell(item["analysis"])
            lines.append(f"| {num} | {t_type} | {prompt_cell} | {result_cell} | {analysis_cell} |")
    else:
        lines.append("| - | *(Завдання ще не виконано)* | - | - | - |")
    lines.append("\n---\n")

    #  Завдання 2
    lines.append("## 2. Порівняння Zero-shot і Few-shot\n")
    lines.append("| Підхід | Prompt | Result | Висновок |")
    lines.append("|---|---|---|---|")
    t2 = data.get("task2", {})
    if t2:
        zero_prompt_cell = to_table_cell(t2.get("zero_prompt", ""))
        zero_result_cell = to_table_cell(t2.get("zero_result", ""))
        few_prompt_cell = to_table_cell(t2.get("few_prompt", ""))
        few_result_cell = to_table_cell(t2.get("few_result", ""))
        conclusion_cell = to_table_cell(t2.get("conclusion", ""))

        lines.append(f"| Zero-shot | {zero_prompt_cell} | {zero_result_cell} | {conclusion_cell} |")
        lines.append(f"| Few-shot | {few_prompt_cell} | {few_result_cell} | {conclusion_cell} |")
        lines.append(f"\n**Висновок до порівняння:**\n{t2.get('conclusion', '')}\n")
    else:
        lines.append("| - | *(Завдання ще не виконано)* | - | - |")
    lines.append("\n---\n")

    #  Завдання 3
    lines.append("## 3. Удосконалення prompt\n")
    t3 = data.get("task3", {})
    if t3:
        lines.append("### Початковий prompt:")
        lines.append(f"```text\n{t3.get('initial_prompt', '')}\n```\n")
        lines.append("**Результат моделі:**")
        lines.append(f"{t3.get('initial_result', '')}\n")

        lines.append("### Вдосконалений prompt:")
        lines.append(f"```text\n{t3.get('improved_prompt', '')}\n```\n")
        lines.append("**Результат моделі:**")
        lines.append(f"{t3.get('improved_result', '')}\n")

        lines.append(f"**Висновок щодо покращення:**\n{t3.get('conclusion', '')}\n")
    else:
        lines.append("*(Завдання ще не виконано)*\n")
    lines.append("---\n")

    # Завдання 4
    lines.append("## 4. Системна роль\n")
    t4 = data.get("task4", {})
    if t4:
        lines.append(f"**Базова задача/запит:**\n```text\n{t4.get('task_prompt', '')}\n```\n")
        for idx, r in enumerate(t4.get("roles", []), start=1):
            lines.append(f"### Роль {idx}: {r.get('role', '')}")
            lines.append("**Результат моделі:**")
            lines.append(f"{r.get('result', '')}\n")
        lines.append(f"**Висновок про вплив ролі:**\n{t4.get('conclusion', '')}\n")
    else:
        lines.append("*(Завдання ще не виконано)*\n")
    lines.append("---\n")

    # Загальні висновки
    lines.append("## 5. Загальні висновки\n")
    lines.append(f"{data.get('general_conclusions', 'Висновки не вказані.')}\n")
    lines.append("---\n")

    #  Контрольні запитання
    lines.append("## 6. Контрольні запитання\n")
    lines.append("1. Що таке Prompt Engineering та яка його основна мета?")
    lines.append("   *Відповідь:*\n")
    lines.append("2. У чому полягає відмінність між Zero-shot та Few-shot prompting?")
    lines.append("   *Відповідь:*\n")
    lines.append("3. Як саме системна інструкція (System Instruction / System Role) змінює поведінку LLM?")
    lines.append("   *Відповідь:*\n")
    lines.append("4. Яких основних правил слід дотримуватися для формування ефективного промпту?")
    lines.append("   *Відповідь:*\n")
    lines.append("5. Що розуміють під терміном 'галюцинація' мовної моделі і як її мінімізувати?")
    lines.append("   *Відповідь:*\n")

    return "\n".join(lines)


def save_report(data):
    
    print("\n" + "=" * 50)
    print("ЗБЕРЕЖЕННЯ ЗВІТУ")
    print("=" * 50)

    # Запитуємо загальні висновки, якщо вони ще не введені
    if not data.get("general_conclusions"):
        data["general_conclusions"] = input_text("Введіть загальні висновки для звіту:")

    report_content = build_report_content(data)
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report_content)

    print("\n[УСПІХ] Звіт успішно збережено у файл report.md!")


def main():
    
    data = {
        "task1": [],
        "task2": {},
        "task3": {},
        "task4": {},
        "general_conclusions": ""
    }

    while True:
        print("\n" + "=" * 50)
        print("   ЛАБОРАТОРНА РОБОТА № 3: МЕНЮ")
        print("=" * 50)
        print("1. Завдання 1: п'ять типів запитів")
        print("2. Завдання 2: Zero-shot vs Few-shot")
        print("3. Завдання 3: Удосконалення prompt")
        print("4. Завдання 4: Системна роль")
        print("5. Зберегти звіт у report.md")
        print("0. Вихід")
        print("=" * 50)

        choice = input("Оберіть пункт (0-5): ").strip()

        if choice == "1":
            run_task1(data)
        elif choice == "2":
            run_task2(data)
        elif choice == "3":
            run_task3(data)
        elif choice == "4":
            run_task4(data)
        elif choice == "5":
            save_report(data)
        elif choice == "0":
            print("\nРоботу завершено. Успіхів у навчанні!")
            break
        else:
            print("\nНекоректний вибір. Введіть число від 0 до 5.")


if __name__ == "__main__":
    main()
