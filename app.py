"""Главный файл сайта. Запуск: streamlit run app.py"""
import streamlit as st

from ai import parse_request
from calc import documents, estimate
from storage import load_requests, save_request

st.set_page_config(
    page_title="Жолсерік — доставка в Ташкент", 
    page_icon="🚚",
    layout="centered"
)

CARGO_TYPES = ["одежда", "продукты", "стройматериалы", "электроника", "другое"]


def money(value):
    return f"{value:,}".replace(",", " ")  # 120000 -> "120 000"


# Заголовок и баннер
st.title("🚚 Жолсерік")
st.caption("Шымкент → Ташкент: цена, срок и документы за 1 минуту")

# Красивое тематическое фото
st.image("my_banner.png", use_container_width=True)

seller_tab, carrier_tab = st.tabs(["📦 Продавцу", "🚛 Перевозчику"])

with seller_tab:
    # Шаг 1. ИИ понимает обычный текст и заполняет форму
    text = st.text_input("Опишите груз своими словами", placeholder="300 кг детской одежды в Ташкент")
    if st.button("✨ Заполнить с помощью ИИ") and text:
        data = parse_request(text, st.secrets["GEMINI_API_KEY"], st.secrets.get("GEMINI_MODEL", "gemini-3.1-flash-lite"))
        if data is None:
            st.warning("ИИ сейчас недоступен. Выберите тип груза и вес вручную.")
        else:
            cargo = data.get("cargo_type")
            st.session_state["cargo"] = cargo if cargo in CARGO_TYPES else "другое"
            weight_ai = data.get("weight_kg")
            if isinstance(weight_ai, (int, float)) and weight_ai > 0:
                st.session_state["weight"] = float(weight_ai)

    # Шаг 2. Продавец проверяет форму
    cargo = st.selectbox("Тип груза", CARGO_TYPES, key="cargo")
    weight = st.number_input("Вес, кг", min_value=0.0, step=10.0, key="weight")

    if st.button("🚀 Рассчитать", type="primary"):
        if weight <= 0:
            st.error("Укажите вес груза.")
        else:
            calc_row = estimate(cargo, weight)
            if calc_row is None:
                base_price = int(weight * 450)
                calc_row = {
                    'price_min_kzt': base_price,
                    'price_max_kzt': int(base_price * 1.25),
                    'days_min': 1,
                    'days_max': 3,
                    'source': 'Базовый тариф Жолсерік'
                }
            st.session_state["result"] = {"cargo": cargo, "weight": weight, "row": calc_row}

    # Шаг 3. Результат
    result = st.session_state.get("result")
    if result:
        row = result["row"]
        st.subheader("📊 Ориентировочно")
        col1, col2 = st.columns(2)
        col1.metric("Цена", f"{money(row['price_min_kzt'])}–{money(row['price_max_kzt'])} ₸")
        col2.metric("Срок", f"{row['days_min']}–{row['days_max']} дн.")
        st.markdown("**📄 Нужные документы:**")
        docs = documents(result["cargo"]) if callable(documents) else ["CMR накладная", "Декларация", "Сертификат"]
        for doc in docs:
            st.markdown(f"- {doc}")
        st.caption(f"Источник: {row.get('source', 'Базовый тариф')}. Цены ориентировочные.")

        # Шаг 4. Заявка перевозчику
        contact = st.text_input("Телефон или @telegram, чтобы перевозчик связался с вами")
        if st.button("📨 Отправить заявку перевозчику"):
            if not contact:
                st.error("Укажите контакт.")
            else:
                save_request({"cargo": result["cargo"], "weight_kg": result["weight"], "contact": contact})
                st.success("Заявка отправлена! Перевозчик свяжется с вами.")

with carrier_tab:
    password = st.text_input("Пароль перевозчика", type="password")
    
    if password == "aidana_true_feminist":
        st.success("Авторизация успешна!")
        items = load_requests()
        if not items:
            st.write("Заявок пока нет.")
        else:
            for item in reversed(items):
                st.markdown(f"📦 **{item['time']}** — {item['cargo']}, {item['weight_kg']:g} кг | 📱 Контакт: `{item['contact']}`")
    elif password:
        st.error("Неверный пароль")
    else:
        st.info("Введите пароль, чтобы увидеть заявки.")

# Футер
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 15px; font-size: 14px;'>"
    "🚚 <b>Жолсерік</b> • Разработано <b>Айданой</b> специально для хакатона ❤️"
    "</div>", 
    unsafe_allow_html=True
)