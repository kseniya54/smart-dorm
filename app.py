import streamlit as st

st.set_page_config(
    page_title="Умная общага",
    page_icon="🏠 "
)

st.title("🏠  Умная общага")
st.write("Помощник для распределения дел и расходов")

tab1, tab2, tab3 = st.tabs(
    ["🧹  Уборка", "💰  Расходы", "🔇  Тишина"]
)

with tab1:
    st.header("График уборки")

    names = st.text_input(
        "Введите имена через запятую",
        placeholder="Варя, Ксюша, Алина"
    )

    if st.button("Создать график"):
        people = [
            name.strip()
            for name in names.split(",")
            if name.strip()
        ]

        days = [
            "Понедельник",
            "Среда",
            "Пятница",
            "Воскресенье"
        ]

        if people:
            for i, person in enumerate(people):
                st.success(
                    f"{days[i % len(days)]}: {person}"
                )
        else:
            st.warning("Введите хотя бы одно имя")

with tab2:
    st.header("Разделить расходы")

    total = st.number_input(
        "Общая сумма, рублей",
        min_value=0.0,
        step=100.0
    )

    count = st.number_input(
        "Количество жильцов",
        min_value=1,
        step=1
    )

    if st.button("Рассчитать сумму"):
        result = total / count
        st.success(
            f"С каждого человека: {result:.2f} ₽"
        )

with tab3:
    st.header("Тихие часы")

    shift = st.selectbox(
        "Выберите учебную смену",
        ["Первая смена", "Вторая смена"]
    )

    if shift == "Первая смена":
        st.info("Рекомендуемое время тишины: 22:30–06:30")
    else:
        st.info("Рекомендуемое время тишины: 00:00–08:00")
