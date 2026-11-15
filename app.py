import streamlit as st
import pandas as pd
from datetime import date, time, datetime, timedelta

st.set_page_config(
    page_title="DayFlow — планировщик",
    page_icon="✅",
    layout="wide"
)

# ---------- Стили ----------
st.markdown("""
<style>
    .main {
        background-color: #f6f8fc;
    }

    h1, h2, h3 {
        color: #172554;
    }

    .card {
        padding: 20px;
        border-radius: 18px;
        background: white;
        box-shadow: 0 4px 18px rgba(0,0,0,0.07);
        margin-bottom: 15px;
    }

    .small-text {
        color: #64748b;
        font-size: 14px;
    }

    .success {
        color: #15803d;
        font-weight: bold;
    }

    .danger {
        color: #dc2626;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Данные ----------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "notes" not in st.session_state:
    st.session_state.notes = ""

# ---------- Заголовок ----------
st.title("✅ DayFlow")
st.caption("Умный планировщик дня: задачи, расписание и контроль прогресса")

# ---------- Боковая панель ----------
with st.sidebar:
    st.header("Настройки дня")

    selected_date = st.date_input(
        "Дата планирования",
        value=date.today()
    )

    start_time = st.time_input(
        "Начало рабочего дня",
        value=time(9, 0)
    )

    end_time = st.time_input(
        "Конец рабочего дня",
        value=time(18, 0)
    )

    st.divider()

    st.header("Фильтры")

    category_filter = st.selectbox(
        "Категория",
        ["Все", "Учёба", "Работа", "Личное", "Здоровье", "Другое"]
    )

    status_filter = st.selectbox(
        "Статус",
        ["Все", "Выполненные", "Невыполненные"]
    )

# ---------- Функции ----------
def get_tasks_for_date():
    result = []

    for task in st.session_state.tasks:
        if task["date"] == selected_date.isoformat():
            if category_filter != "Все" and task["category"] != category_filter:
                continue

            if status_filter == "Выполненные" and task["done"] is not True:
                continue

            if status_filter == "Невыполненные" and task["done"] is True:
                continue

            result.append(task)

    return result


def priority_value(priority):
    values = {
        "Высокий": 1,
        "Средний": 2,
        "Низкий": 3
    }
    return values[priority]


def auto_plan():
    current = datetime.combine(selected_date, start_time)

    pending = [
        task for task in st.session_state.tasks
        if task["date"] == selected_date.isoformat()
        and not task["done"]
    ]

    pending.sort(
        key=lambda x: (priority_value(x["priority"]), x["duration"])
    )

    for task in pending:
        finish = current + timedelta(minutes=task["duration"])

        task["planned_start"] = current.strftime("%H:%M")
        task["planned_end"] = finish.strftime("%H:%M")

        current = finish + timedelta(minutes=10)

    st.session_state.tasks = st.session_state.tasks


def delete_task(task_id):
    st.session_state.tasks = [
        task for task in st.session_state.tasks
        if task["id"] != task_id
    ]

# ---------- Метрики ----------
all_tasks = [
    task for task in st.session_state.tasks
    if task["date"] == selected_date.isoformat()
]

completed = sum(task["done"] for task in all_tasks)
total = len(all_tasks)
total_minutes = sum(task["duration"] for task in all_tasks)

progress = completed / total if total else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Всего задач", total)
col2.metric("Выполнено", completed)
col3.metric("Время на задачи", f"{total_minutes // 60} ч {total_minutes % 60} мин")
col4.metric("Прогресс", f"{int(progress * 100)}%")

st.progress(progress)

# ---------- Вкладки ----------
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Мои задачи",
    "➕ Добавить задачу",
    "📊 Статистика",
    "📝 Заметки"
])

# ---------- Задачи ----------
with tab1:
    st.subheader(f"План на {selected_date.strftime('%d.%m.%Y')}")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.write("Задачи можно сортировать по приоритету и автоматически распределять по времени.")

    with col2:
        if st.button("⚡ Составить план"):
            auto_plan()
            st.success("План составлен!")
            st.rerun()

    visible_tasks = get_tasks_for_date()

    if not visible_tasks:
        st.info("На этот день пока нет задач.")
    else:
        for task in visible_tasks:
            with st.container():
                col_check, col_info, col_delete = st.columns([0.5, 5, 1])

                with col_check:
                    new_status = st.checkbox(
                        "",
                        value=task["done"],
                        key=f"check_{task['id']}"
                    )

                    if new_status != task["done"]:
                        task["done"] = new_status
                        st.rerun()

                with col_info:
                    title = task["title"]

                    if task["done"]:
                        st.markdown(f"~~### {title}~~")
                    else:
                        st.markdown(f"### {title}")

                    planned = ""

                    if task["planned_start"]:
                        planned = (
                            f"🕒 {task['planned_start']}–"
                            f"{task['planned_end']} · "
                        )

                    st.caption(
                        f"{planned}"
                        f"📁 {task['category']} · "
                        f"⏱ {task['duration']} мин · "
                        f"⭐ {task['priority']}"
                    )

                    if task["description"]:
                        st.write(task["description"])

                with col_delete:
                    if st.button("🗑", key=f"delete_{task['id']}"):
                        delete_task(task["id"])
                        st.rerun()

                st.divider()

# ---------- Добавление ----------
with tab2:
    st.subheader("Добавить новую задачу")

    with st.form("task_form", clear_on_submit=True):
        title = st.text_input(
            "Название задачи",
            placeholder="Например: подготовить презентацию"
        )

        description = st.text_area(
            "Описание",
            placeholder="Что именно нужно сделать?"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            task_date = st.date_input(
                "Дата",
                value=selected_date
            )

        with col2:
            duration = st.number_input(
                "Длительность, минут",
                min_value=5,
                max_value=720,
                value=30,
                step=5
            )

        with col3:
            priority = st.selectbox(
                "Приоритет",
                ["Высокий", "Средний", "Низкий"]
            )

        category = st.selectbox(
            "Категория",
            ["Учёба", "Работа", "Личное", "Здоровье", "Другое"]
        )

        submitted = st.form_submit_button(
            "Добавить задачу"
        )

        if submitted:
            if not title.strip():
                st.error("Введите название задачи.")
            else:
                new_task = {
                    "id": len(st.session_state.tasks) + 1,
                    "title": title,
                    "description": description,
                    "date": task_date.isoformat(),
                    "duration": int(duration),
                    "priority": priority,
                    "category": category,
                    "done": False,
                    "planned_start": "",
                    "planned_end": ""
                }

                st.session_state.tasks.append(new_task)
                st.success("Задача добавлена!")

# ---------- Статистика ----------
with tab3:
    st.subheader("Статистика продуктивности")

    if all_tasks:
        data = []

        for task in all_tasks:
            data.append({
                "Задача": task["title"],
                "Категория": task["category"],
                "Приоритет": task["priority"],
                "Минуты": task["duration"],
                "Выполнено": "Да" if task["done"] else "Нет"
            })

        df = pd.DataFrame(data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Время по категориям")

        category_stats = (
            df.groupby("Категория")["Минуты"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(category_stats)

        st.subheader("Экспорт данных")

        csv = df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "⬇️ Скачать задачи в CSV",
            data=csv,
            file_name=f"plan_{selected_date}.csv",
            mime="text/csv"
        )
    else:
        st.info("Статистика появится после добавления задач.")

# ---------- Заметки ----------
with tab4:
    st.subheader("Заметки на день")

    st.session_state.notes = st.text_area(
        "Запишите важные мысли, идеи или напоминания",
        value=st.session_state.notes,
        height=250,
        placeholder="Например: не забыть взять документы..."
    )

    st.success("Заметки сохраняются во время работы приложения.")

# ---------- Нижняя часть ----------
st.divider()

st.caption(
    "DayFlow помогает распределять задачи, видеть загрузку и контролировать результат."
)
