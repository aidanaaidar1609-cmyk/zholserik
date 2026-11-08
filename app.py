"""Главный файл сайта. Запуск: streamlit run app.py"""
import pandas as pd
import streamlit as st

from ai import parse_request
from calc import documents, estimate
from storage import load_requests, save_request

st.set_page_config(
    page_title="Жолсерік AI — Трансграничная логистика",
    page_icon="🚚",
    layout="centered",
)

CARGO_TYPES = ["одежда", "продукты", "стройматериалы", "электроника", "другое"]


def money(value):
    return f"{value:,}".replace(",", " ")


# --- ШАПКА И БЕНДИНГ ---
st.title("🚚 Жолсерік AI")
st.caption(
    "Умный логистический коридор **Шымкент 🇰🇿 ➔ 🇺🇿 Ташкент**: расчет тарифов, таможни и подбор машин"
)

# Баннер
st.image("my_banner.png", use_container_width=True)

seller_tab, carrier_tab = st.tabs(
    ["📦 Продавцу (Заказчику)", "🚛 Перевозчику (Панель)"]
)

with seller_tab:
    st.subheader("1. Расчет доставки и таможни")

    # Шаг 1. ИИ парсер
    text = st.text_input(
        "Опишите ваш груз в свободной форме",
        placeholder="Например: 500 кг бытовой техники и электроники в Ташкент",
    )
    if st.button("✨ Распознать через ИИ") and text:
        data = parse_request(
            text,
            st.secrets["GEMINI_API_KEY"],
            st.secrets.get("GEMINI_MODEL", "gemini-3.1-flash-lite"),
        )
        if data is None:
            st.warning("ИИ сейчас недоступен. Заполните параметры вручную.")
        else:
            cargo = data.get("cargo_type")
            st.session_state["cargo"] = (
                cargo if cargo in CARGO_TYPES else "другое"
            )
            weight_ai = data.get("weight_kg")
            if isinstance(weight_ai, (int, float)) and weight_ai > 0:
                st.session_state["weight"] = float(weight_ai)
            st.success("ИИ успешно распознал данные груза!")

    # Шаг 2. Форма
    col_a, col_b = st.columns(2)
    with col_a:
        cargo = st.selectbox("Категория груза", CARGO_TYPES, key="cargo")
    with col_b:
        weight = st.number_input(
            "Вес груза (кг)", min_value=0.0, step=10.0, key="weight"
        )

    if st.button("🚀 Рассчитать маршрут и стоимость", type="primary"):
        if weight <= 0:
            st.error("Укажите корректный вес груза.")
        else:
            calc_row = estimate(cargo, weight)
            if calc_row is None:
                base_price = int(weight * 450)
                calc_row = {
                    "price_min_kzt": base_price,
                    "price_max_kzt": int(base_price * 1.25),
                    "days_min": 1,
                    "days_max": 3,
                    "source": "Базовый тариф Жолсерік",
                }
            st.session_state["result"] = {
                "cargo": cargo,
                "weight": weight,
                "row": calc_row,
            }

    # Шаг 3. Отображение результатов
    result = st.session_state.get("result")
    if result:
        row = result["row"]
        st.markdown("---")
        st.subheader("📊 Расчёт стоимости и сроков")

        m1, m2, m3 = st.columns(3)
        m1.metric(
            "Стоимость",
            f"{money(row['price_min_kzt'])}–{money(row['price_max_kzt'])} ₸",
        )
        m2.metric("Срок доставки", f"{row['days_min']}–{row['days_max']} дн.")
        m3.metric(
            "Маршрут",
            "125 км (Жибек Жолы)",
            delta="Пункт пропуска",
            delta_color="normal",
        )

        # Таможенный блок
        st.markdown("🛃 **Таможенный статус и рекомендации:**")
        if result["cargo"] == "электроника":
            st.info(
                "⚠️ **Требуется:** Нотификация РУз и сертификат соответствия ЕАЭС."
            )
        elif result["cargo"] == "продукты":
            st.warning(
                "🌡️ **Режим:** Требуется рефрижератор и фитосанитарный контроль."
            )
        else:
            st.success(
                "✅ **Зеленый коридор:** Упрощенное декларирование для коммерческих грузов."
            )

        # Документы
        st.markdown("**📄 Пакет сопроводительных документов:**")
        docs = (
            documents(result["cargo"])
            if callable(documents)
            else ["CMR накладная", "Инвойс", "Декларация"]
        )
        for doc in docs:
            st.markdown(f"- {doc}")
        st.caption(
            f"Источник тарифа: {row.get('source', 'Партнерская сеть MG Logistics')}."
        )

        # Интерактивная карта
        st.markdown("📍 **Гео-визуализация маршрута:**")
        map_df = pd.DataFrame(
            {
                "lat": [42.3417, 41.2995],
                "lon": [69.5901, 69.2401],
            }
        )
        st.map(map_df, zoom=6)

        # Шаг 4. Отправка заявки
        st.markdown("---")
        st.subheader("📨 Подать заявку перевозчикам")
        contact = st.text_input(
            "Ваш телефон или Telegram для связи",
            placeholder="+7 707 ... или @username",
        )
        if st.button("Передать заявку в логистический хаб"):
            if not contact:
                st.error("Пожалуйста, укажите контактные данные.")
            else:
                save_request(
                    {
                        "cargo": result["cargo"],
                        "weight_kg": result["weight"],
                        "contact": contact,
                        "status": "Новая",
                    }
                )
                st.success(
                    "🎉 Заявка размещена! Перевозчики в Ташкент уже видят ваш запрос."
                )

with carrier_tab:
    st.subheader("🔐 Вход для аккредитованных перевозчиков")
    password = st.text_input("Введите пароль доступа", type="password")

    if password == "aidana_true_feminist":
        st.success("Доступ разрешен. Активные заявки направления Шымкент–Ташкент:")
        items = load_requests()
        if not items:
            st.info("В данный момент нет необработанных заявок.")
        else:
            for idx, item in enumerate(reversed(items)):
                status = item.get("status", "Новая")
                with st.expander(
                    f"📦 Заявка #{len(items)-idx}: {item['cargo'].upper()} — {item['weight_kg']:g} кг ({status})"
                ):
                    st.write(f"⏱ **Время:** {item.get('time', 'Только что')}")
                    st.write(f"📞 **Контакт клиента:** `{item['contact']}`")
                    st.write(f"📌 **Статус:** {status}")
                    if st.button(f"Принять заказ #{len(items)-idx}", key=f"btn_{idx}"):
                        st.balloons()
                        st.success("Вы взяли заказ в работу! Свяжитесь с клиентом.")
    elif password:
        st.error("Ошибка авторизации. Неверный пароль.")
    else:
        st.info("Внимание: Панель предназначена только для проверенных водителей и ТК.")

# --- ФУТЕР ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #777; padding: 15px; font-size: 13px;'>"
    "🚀 <b>Жолсерік AI</b> • Платформа трансграничной логистики<br>"
    "Разработано <b>Айданой</b> специально для хакатона 2026 ❤️"
    "</div>",
    unsafe_allow_html=True,
)