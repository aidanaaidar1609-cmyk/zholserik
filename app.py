"""Главный файл сайта с поддержкой 3 языков (KZ, UZ, RU) и команды DayOne."""

import pandas as pd
import streamlit as st

from ai import parse_request
from calc import documents, estimate
from storage import load_requests, save_request

st.set_page_config(
    page_title="Zholserik AI — Cross-Border Logistics",
    page_icon="🚚",
    layout="centered",
)

CARGO_TYPES = ["одежда", "продукты", "стройматериалы", "электроника", "другое"]

# --- СЛОВАРЬ ПЕРЕВОДОВ (KZ / UZ / RU) ---
TRANSLATIONS = {
    "🇰🇿 Қазақша": {
        "title": "🚚 Жолсерік AI",
        "caption": (
            "Шымкент 🇰🇿 ➔ 🇺🇿 Ташкент шекаралық интеллектуалды логистикалық"
            " хабы"
        ),
        "tab_seller": "📦 Жөнелтушіге (Тапсырыс беруші)",
        "tab_carrier": "🚛 Тасымалдаушыға (Панель)",
        "input_label": "Жүгіңізді еркін түрде сипаттаңыз",
        "input_ph": "Мысалы: Ташкентке 500 кг тұрмыстық техника мен электроника",
        "ai_btn": "✨ AI арқылы тану",
        "category": "Жүк санаты",
        "weight": "Жүк салмағы (кг)",
        "calc_btn": "🚀 Маршрут пен құнын есептеу",
        "metrics_price": "Жеткізу құны",
        "metrics_time": "Жеткізу мерзімі",
        "metrics_route": "Маршрут",
        "customs_title": "🛃 Кедендік мәртебе мен ұсыныстар:",
        "docs_title": "📄 Ілеспе құжаттар топтамасы:",
        "map_title": "📍 Маршрутты гео-визуализациялау:",
        "send_title": "📨 Тасымалдаушыларға өтінім беру",
        "contact_label": "Байланыс телефоны немесе Telegram",
        "send_btn": "Өтінімді логистикалық хабқа жіберу",
        "carrier_auth": "🔐 Аккредиттелген тасымалдаушылар үшін кіру",
        "pass_label": "Құпия сөзді енгізіңіз",
        "take_order": "Тапсырысты қабылдау",
    },
    "🇺🇿 Oʻzbekcha": {
        "title": "🚚 Zholserik AI",
        "caption": (
            "Chimkent 🇰🇿 ➔ 🇺🇿 Toshkent chegaralararo intellektual logistika"
            " xabi"
        ),
        "tab_seller": "📦 Yuboruvchiga (Buyurtmachi)",
        "tab_carrier": "🚛 Tashuvchiga (Panel)",
        "input_label": "Yukingizni erkin shaklda tasvirlang",
        "input_ph": (
            "Masalan: Toshkentga 500 kg maishiy texnika va elektronika"
        ),
        "ai_btn": "✨ AI orqali aniqlash",
        "category": "Yuk toifasi",
        "weight": "Yuk vazni (kg)",
        "calc_btn": "🚀 Yo'nalish va narxni hisoblash",
        "metrics_price": "Etkazib berish narxi",
        "metrics_time": "Etkazib berish muddati",
        "metrics_route": "Yo'nalish",
        "customs_title": "🛃 Bojxona maqomi va tavsiyalar:",
        "docs_title": "📄 Hamrohlik hujjatlari toplami:",
        "map_title": "📍 Yo'nalishni geo-vizuallashtirish:",
        "send_title": "📨 Tashuvchilarga ariza yuborish",
        "contact_label": "Aloqa telefoni yoki Telegram",
        "send_btn": "Arizani logistika xabiga yuborish",
        "carrier_auth": "🔐 Akkreditatsiyalangan tashuvchilar uchun kirish",
        "pass_label": "Parolni kiriting",
        "take_order": "Buyurtmani qabul qilish",
    },
    "🇷🇺 Русский": {
        "title": "🚚 Жолсерік AI",
        "caption": (
            "Умный логистический коридор Шымкент 🇰🇿 ➔ 🇺🇿 Ташкент: расчет"
            " тарифов, таможни и подбор машин"
        ),
        "tab_seller": "📦 Продавцу (Заказчику)",
        "tab_carrier": "🚛 Перевозчику (Панель)",
        "input_label": "Опишите ваш груз в свободной форме",
        "input_ph": (
            "Например: 500 кг бытовой техники и электроники в Ташкент"
        ),
        "ai_btn": "✨ Распознать через ИИ",
        "category": "Категория груза",
        "weight": "Вес груза (кг)",
        "calc_btn": "🚀 Рассчитать маршрут и стоимость",
        "metrics_price": "Стоимость",
        "metrics_time": "Срок доставки",
        "metrics_route": "Маршрут",
        "customs_title": "🛃 Таможенный статус и рекомендации:",
        "docs_title": "📄 Пакет сопроводительных документов:",
        "map_title": "📍 Гео-визуализация маршрута:",
        "send_title": "📨 Подать заявку перевозчикам",
        "contact_label": "Ваш телефон или Telegram для связи",
        "send_btn": "Передать заявку в логистический хаб",
        "carrier_auth": "🔐 Вход для аккредитованных перевозчиков",
        "pass_label": "Введите пароль доступа",
        "take_order": "Принять заказ",
    },
}


def money(value):
    return f"{value:,}".replace(",", " ")


# --- ВЫБОР ЯЗЫКА ---
lang_choice = st.sidebar.selectbox(
    "🌐 Тіл / Tillar / Язык",
    ["🇰🇿 Қазақша", "🇺🇿 Oʻzbekcha", "🇷🇺 Русский"],
    index=2,
)
t = TRANSLATIONS[lang_choice]

# --- ШАПКА И БАННЕР ---
st.title(t["title"])
st.caption(t["caption"])

# Баннер
st.image("my_banner.png", use_container_width=True)

seller_tab, carrier_tab = st.tabs([t["tab_seller"], t["tab_carrier"]])

with seller_tab:
    # Шаг 1. ИИ парсер
    text = st.text_input(
        t["input_label"],
        placeholder=t["input_ph"],
    )
    if st.button(t["ai_btn"]) and text:
        data = parse_request(
            text,
            st.secrets["GEMINI_API_KEY"],
            st.secrets.get("GEMINI_MODEL", "gemini-3.1-flash-lite"),
        )
        if data is None:
            st.warning("AI временно недоступен.")
        else:
            cargo = data.get("cargo_type")
            st.session_state["cargo"] = (
                cargo if cargo in CARGO_TYPES else "другое"
            )
            weight_ai = data.get("weight_kg")
            if isinstance(weight_ai, (int, float)) and weight_ai > 0:
                st.session_state["weight"] = float(weight_ai)
            st.success("✅ AI success!")

    # Шаг 2. Форма
    col_a, col_b = st.columns(2)
    with col_a:
        cargo = st.selectbox(t["category"], CARGO_TYPES, key="cargo")
    with col_b:
        weight = st.number_input(
            t["weight"], min_value=0.0, step=10.0, key="weight"
        )

    if st.button(t["calc_btn"], type="primary"):
        if weight <= 0:
            st.error("Укажите вес.")
        else:
            calc_row = estimate(cargo, weight)
            if calc_row is None:
                base_price = int(weight * 450)
                calc_row = {
                    "price_min_kzt": base_price,
                    "price_max_kzt": int(base_price * 1.25),
                    "days_min": 1,
                    "days_max": 3,
                    "source": "Базовый тариф Zholserik",
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

        m1, m2, m3 = st.columns(3)
        m1.metric(
            t["metrics_price"],
            f"{money(row['price_min_kzt'])}–{money(row['price_max_kzt'])} ₸",
        )
        m2.metric(t["metrics_time"], f"{row['days_min']}–{row['days_max']} дн.")
        m3.metric(
            t["metrics_route"],
            "125 км (Жибек Жолы)",
            delta="Пункт пропуска",
            delta_color="normal",
        )

        # Таможенный блок
        st.markdown(t["customs_title"])
        if result["cargo"] == "электроника":
            st.info(
                "⚠️ **Талап / Talab:** Нотификация РУз & Сертификат ЕАЭС."
            )
        elif result["cargo"] == "продукты":
            st.warning(
                "🌡️ **Режим:** Рефрижератор & Фитосанитарный контроль."
            )
        else:
            st.success(
                "✅ **Зеленый коридор / Yaşıl koridor:** Упрощенный порядок."
            )

        # Документы
        st.markdown(t["docs_title"])
        docs = (
            documents(result["cargo"])
            if callable(documents)
            else ["CMR накладная", "Инвойс", "Декларация"]
        )
        for doc in docs:
            st.markdown(f"- {doc}")

        # Интерактивная карта
        st.markdown(t["map_title"])
        map_df = pd.DataFrame(
            {
                "lat": [42.3417, 41.2995],
                "lon": [69.5901, 69.2401],
            }
        )
        st.map(map_df, zoom=6)

        # Шаг 4. Отправка заявки
        st.markdown("---")
        st.subheader(t["send_title"])
        contact = st.text_input(
            t["contact_label"],
            placeholder="+7 707 ... / +998 90 ...",
        )
        if st.button(t["send_btn"]):
            if not contact:
                st.error("Укажите контакт.")
            else:
                save_request(
                    {
                        "cargo": result["cargo"],
                        "weight_kg": result["weight"],
                        "contact": contact,
                        "status": "Новая",
                    }
                )
                st.success("🎉 Заявка отправлена / Ariza yuborildi!")

with carrier_tab:
    st.subheader(t["carrier_auth"])
    password = st.text_input(t["pass_label"], type="password")

    if password == "aidana_true_feminist":
        st.success("Доступ разрешен / Kirishga ruxsat berildi:")
        items = load_requests()
        if not items:
            st.info("Нет необработанных заявок.")
        else:
            for idx, item in enumerate(reversed(items)):
                status = item.get("status", "Новая")
                with st.expander(
                    f"📦 Заявка #{len(items)-idx}: {item['cargo'].upper()} —"
                    f" {item['weight_kg']:g} кг ({status})"
                ):
                    st.write(f"📞 **Контакт:** `{item['contact']}`")
                    st.write(f"📌 **Статус:** {status}")
                    if st.button(
                        f"{t['take_order']} #{len(items)-idx}", key=f"btn_{idx}"
                    ):
                        st.balloons()
                        st.success("Заказ принят в работу!")
    elif password:
        st.error("Неверный пароль.")

# --- ФУТЕР ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #777; padding: 15px; font-size:"
    " 13px;'>🚀 <b>Zholserik AI</b> • Shymkent–Tashkent Cross-Border AI"
    " Platform<br>Разработано командой <b>DayOne</b> специально для хакатона"
    " 2026 ❤️</div>",
    unsafe_allow_html=True,
)