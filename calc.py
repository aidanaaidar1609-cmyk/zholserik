"""Модуль расчета стоимости, сроков и документов."""


def estimate(cargo_type, weight_kg):
    """Возвращает примерную цену, сроки, источник и оптовые условия."""

    # Если вес от 3 тонн (согласно данным MG Logistics из WhatsApp)
    if weight_kg >= 3000:
        base_price = int(weight_kg * 350)
        return {
            "price_min_kzt": base_price,
            "price_max_kzt": int(base_price * 1.2),
            "days_min": 1,
            "days_max": 2,
            "source": "MG Logistics (опт от 3 тонн)",
        }

    # Для сборных грузов (розница/мелкий опт)
    rates = {
        "одежда": 400,
        "продукты": 350,
        "стройматериалы": 300,
        "электроника": 450,
        "другое": 380,
    }

    price_per_kg = rates.get(cargo_type, 380)
    base_price = int(weight_kg * price_per_kg)

    return {
        "price_min_kzt": base_price,
        "price_max_kzt": int(base_price * 1.25),
        "days_min": 1,
        "days_max": 3,
        "source": "Сборный тариф Жолсерік",
    }


def documents(cargo_type):
    """Список документов для таможенного оформления."""
    base_docs = ["CMR-накладная", "Инвойс / Договор купли-продажи"]
    if cargo_type == "продукты":
        base_docs.append("Фитосанитарный сертификат")
    elif cargo_type == "электроника":
        base_docs.append("Сертификат соответствия ЕАЭС / Нотификация")
    elif cargo_type == "стройматериалы":
        base_docs.append("Паспорт качества производителя")
    return base_docs