

import streamlit as st
from lab3 import ask, build_report_content, to_table_cell, MODEL_NAME

#Налаштування сторінки
st.set_page_config(page_title="Лабораторна №3 — Prompt Engineering", layout="wide")
st.title("Лабораторна робота №3: Основи Prompt Engineering")


if "task1" not in st.session_state:
    st.session_state.task1 = []       
if "task2" not in st.session_state:
    st.session_state.task2 = {}
if "task3" not in st.session_state:
    st.session_state.task3 = {}
if "task4" not in st.session_state:
    st.session_state.task4 = {}
if "general_conclusions" not in st.session_state:
    st.session_state.general_conclusions = ""


def safe_ask(prompt, system=None):
    
    result = ask(prompt, system=system)
    if result.startswith("Помилка"):
        st.error(result)
        return None
    return result


# Вкладки

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Типи запитів",
    "2. Zero-shot vs Few-shot",
    "3. Удосконалення prompt",
    "4. Системна роль",
    "5. Звіт"
])


TYPES_LIST = ["Пояснення", "Генерація тексту", "Переклад", "Узагальнення", "Список"]

with tab1:
    st.header("Завдання 1: П'ять типів запитів")

    chosen_type = st.selectbox("Оберіть тип запиту:", TYPES_LIST, key="t1_type")
    prompt_t1 = st.text_area("Ваш Prompt:", key="t1_prompt", height=120,
                             placeholder="Введіть ваш запит для обраного типу...")

    if st.button("Надіслати запит", key="t1_send"):
        if not prompt_t1.strip():
            st.warning("Будь ласка, введіть prompt!")
        else:
            with st.spinner("Модель обробляє запит..."):
                answer = safe_ask(prompt_t1)
            if answer:
                st.session_state["t1_last_answer"] = answer

    # Показуємо останню відповідь
    if st.session_state.get("t1_last_answer"):
        st.subheader("Відповідь моделі:")
        st.markdown(st.session_state["t1_last_answer"])

    analysis_t1 = st.text_input("Короткий аналіз (1–3 речення):", key="t1_analysis")

    if st.button("Зберегти цей тип", key="t1_save"):
        answer = st.session_state.get("t1_last_answer", "")
        if not prompt_t1.strip() or not answer:
            st.warning("Спочатку надішліть prompt та отримайте відповідь!")
        else:
            idx = TYPES_LIST.index(chosen_type) + 1
            # Видаляємо старий запис цього типу
            st.session_state.task1 = [
                item for item in st.session_state.task1 if item["type"] != chosen_type
            ]
            st.session_state.task1.append({
                "num": idx, "type": chosen_type,
                "prompt": prompt_t1.strip(), "result": answer,
                "analysis": analysis_t1.strip()
            })
            st.session_state.task1.sort(key=lambda x: x["num"])
            st.success(f"Тип «{chosen_type}» збережено! ({len(st.session_state.task1)}/5)")

    # Таблиця вже збережених
    if st.session_state.task1:
        st.divider()
        st.subheader("Збережені типи:")
        for item in st.session_state.task1:
            st.write(f"**{item['num']}. {item['type']}** — prompt: _{item['prompt'][:80]}..._")


with tab2:
    st.header("Завдання 2: Zero-shot vs Few-shot")

    col_z, col_f = st.columns(2)

    with col_z:
        st.subheader("Zero-shot (без прикладів)")
        zero_prompt = st.text_area("Zero-shot Prompt:", key="t2_zero_p", height=150,
                                   placeholder="Введіть запит без прикладів...")
        if st.button("Надіслати Zero-shot", key="t2_zero_send"):
            if not zero_prompt.strip():
                st.warning("Введіть prompt!")
            else:
                with st.spinner("Запит обробляється..."):
                    ans = safe_ask(zero_prompt)
                if ans:
                    st.session_state["t2_zero_result"] = ans

        if st.session_state.get("t2_zero_result"):
            st.markdown("**Відповідь:**")
            st.markdown(st.session_state["t2_zero_result"])

    with col_f:
        st.subheader("Few-shot (з прикладами)")
        few_prompt = st.text_area("Few-shot Prompt:", key="t2_few_p", height=150,
                                  placeholder="Введіть запит з 2-3 прикладами...")
        if st.button("Надіслати Few-shot", key="t2_few_send"):
            if not few_prompt.strip():
                st.warning("Введіть prompt!")
            else:
                with st.spinner("Запит обробляється..."):
                    ans = safe_ask(few_prompt)
                if ans:
                    st.session_state["t2_few_result"] = ans

        if st.session_state.get("t2_few_result"):
            st.markdown("**Відповідь:**")
            st.markdown(st.session_state["t2_few_result"])

    st.divider()
    conclusion_t2 = st.text_area("Ваш висновок (порівняння Zero-shot та Few-shot):",
                                 key="t2_conclusion", height=80)

    if st.button("Зберегти Завдання 2", key="t2_save"):
        zr = st.session_state.get("t2_zero_result", "")
        fr = st.session_state.get("t2_few_result", "")
        if not zr or not fr:
            st.warning("Спочатку отримайте обидві відповіді!")
        else:
            st.session_state.task2 = {
                "zero_prompt": zero_prompt.strip(),
                "zero_result": zr,
                "few_prompt": few_prompt.strip(),
                "few_result": fr,
                "conclusion": conclusion_t2.strip()
            }
            st.success("Завдання 2 збережено!")


with tab3:
    st.header("Завдання 3: Удосконалення prompt")

    col_i, col_u = st.columns(2)

    with col_i:
        st.subheader("Початковий (простий) prompt")
        init_prompt = st.text_area("Prompt:", key="t3_init_p", height=150,
                                   placeholder="Введіть базовий prompt...")
        if st.button("Надіслати початковий", key="t3_init_send"):
            if not init_prompt.strip():
                st.warning("Введіть prompt!")
            else:
                with st.spinner("Запит обробляється..."):
                    ans = safe_ask(init_prompt)
                if ans:
                    st.session_state["t3_init_result"] = ans

        if st.session_state.get("t3_init_result"):
            st.markdown("**Відповідь:**")
            st.markdown(st.session_state["t3_init_result"])

    with col_u:
        st.subheader("Вдосконалений prompt")
        impr_prompt = st.text_area("Prompt:", key="t3_impr_p", height=150,
                                   placeholder="Введіть вдосконалений prompt...")
        if st.button("Надіслати вдосконалений", key="t3_impr_send"):
            if not impr_prompt.strip():
                st.warning("Введіть prompt!")
            else:
                with st.spinner("Запит обробляється..."):
                    ans = safe_ask(impr_prompt)
                if ans:
                    st.session_state["t3_impr_result"] = ans

        if st.session_state.get("t3_impr_result"):
            st.markdown("**Відповідь:**")
            st.markdown(st.session_state["t3_impr_result"])

    st.divider()
    conclusion_t3 = st.text_area("Ваш висновок щодо покращення prompt:",
                                 key="t3_conclusion", height=80)

    if st.button("Зберегти Завдання 3", key="t3_save"):
        ir = st.session_state.get("t3_init_result", "")
        ur = st.session_state.get("t3_impr_result", "")
        if not ir or not ur:
            st.warning("Спочатку отримайте обидві відповіді!")
        else:
            st.session_state.task3 = {
                "initial_prompt": init_prompt.strip(),
                "initial_result": ir,
                "improved_prompt": impr_prompt.strip(),
                "improved_result": ur,
                "conclusion": conclusion_t3.strip()
            }
            st.success("Завдання 3 збережено!")


with tab4:
    st.header("Завдання 4: Системна роль")

    task_prompt = st.text_area("Базове запитання (однакове для всіх ролей):",
                               key="t4_task", height=100,
                               placeholder="Введіть задачу, яку передамо моделі з кожною роллю...")

    col_r1, col_r2, col_r3 = st.columns(3)

    for i, col in enumerate([col_r1, col_r2, col_r3], start=1):
        with col:
            st.subheader(f"Роль #{i}")
            role = st.text_input(f"System instruction:", key=f"t4_role_{i}",
                                 placeholder=f"Напр.: Ти досвідчений ...")
            if st.button(f"Запустити роль #{i}", key=f"t4_send_{i}"):
                if not task_prompt.strip() or not role.strip():
                    st.warning("Заповніть базове запитання та роль!")
                else:
                    with st.spinner(f"Роль #{i} обробляється..."):
                        ans = safe_ask(task_prompt, system=role)
                    if ans:
                        st.session_state[f"t4_result_{i}"] = ans

            if st.session_state.get(f"t4_result_{i}"):
                st.markdown("**Відповідь:**")
                st.markdown(st.session_state[f"t4_result_{i}"])

    st.divider()
    conclusion_t4 = st.text_area("Ваш висновок про вплив системної ролі:",
                                 key="t4_conclusion", height=80)

    if st.button("Зберегти Завдання 4", key="t4_save"):
        roles_list = []
        all_ok = True
        for i in range(1, 4):
            r = st.session_state.get(f"t4_role_{i}", "").strip()
            res = st.session_state.get(f"t4_result_{i}", "")
            if not res:
                all_ok = False
            roles_list.append({"role": r, "result": res})
        if not all_ok:
            st.warning("Спочатку отримайте відповіді для всіх трьох ролей!")
        else:
            st.session_state.task4 = {
                "task_prompt": task_prompt.strip(),
                "roles": roles_list,
                "conclusion": conclusion_t4.strip()
            }
            st.success("Завдання 4 збережено!")


with tab5:
    st.header("Формування звіту report.md")

    gen_concl = st.text_area("Загальні висновки до лабораторної роботи:",
                             key="t5_conclusions", height=120)

    if st.button("Сформувати та зберегти report.md", key="t5_generate"):
        
        report_data = {
            "task1": st.session_state.task1,
            "task2": st.session_state.task2,
            "task3": st.session_state.task3,
            "task4": st.session_state.task4,
            "general_conclusions": gen_concl.strip()
        }
        report_md = build_report_content(report_data)

        # Зберігаємо у файл
        with open("report.md", "w", encoding="utf-8") as f:
            f.write(report_md)

        st.session_state["report_md"] = report_md
        st.success("Звіт збережено у файл report.md!")

    # Кнопка завантаження та попередній перегляд
    if st.session_state.get("report_md"):
        st.download_button(
            label="⬇ Завантажити report.md",
            data=st.session_state["report_md"],
            file_name="report.md",
            mime="text/markdown"
        )
        st.divider()
        st.subheader("Попередній перегляд:")
        st.code(st.session_state["report_md"], language="markdown")
