from catalog.services import ComparedProducts


def sort_convert(session, sort):
    temp = ""
    if "-" in sort:
        sort_param = sort[1:]
        sort = sort[1:]
        temp = "Sort-sortBy_inc"
    else:
        sort_param = f"-{sort}"
        temp = "Sort-sortBy_dec"
    session["sort_catalog"] = generate_sort_param()
    session["sort_catalog"][sort] = {
        "param": sort_param,
        "style": temp,
    }


def generate_sort_param():
    return {
        "price": {
            "param": "price",
            "style": "",
        },
        "rating": {
            "param": "rating",
            "style": "",
        },
        "date": {
            "param": "date",
            "style": "",
        },
        "quantity": {
            "param": "quantity",
            "style": "",
        },
    }


def matched_items_for_comparison_view(comparison_list: ComparedProducts):
    """
    Функция для нахождения одинаковых характеристик в сравниваемых товарах
    Args:
    comparison_list: ComparedProducts объект сессии сравнивания

    return:
    matched_values_characteristics: list список с совпадающими характеристиками
    """
    characteristics_and_values = list()
    all_characteristics = list()
    matched_names_characteristics = list()
    matched_values_characteristics = list()
    flag_not_matching = False

    for product, price in comparison_list:
        characteristics = product.characteristics
        characteristics_and_values.append(characteristics)
    item_num = len(characteristics_and_values)
    for item in characteristics_and_values:
        all_characteristics.extend(item)

    for one_prod in characteristics_and_values:
        count = 0
        for char_one in one_prod:
            if all_characteristics.count(char_one) == 1:
                count += 1
            if count == len(one_prod):
                flag_not_matching = True
    all_characteristics_unic = set(all_characteristics)

    for u_char in all_characteristics_unic:
        if all_characteristics.count(u_char) == item_num:
            matched_names_characteristics.append(u_char)

    for char in matched_names_characteristics:
        matched_values_characteristics.append(char)
        curr_char = characteristics_and_values[0].get(char)
        for item in characteristics_and_values:
            if item.get(char) != curr_char:
                matched_values_characteristics.remove(char)
                break
    return matched_values_characteristics, flag_not_matching
