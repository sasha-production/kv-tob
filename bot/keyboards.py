# keyboards.py
# Здесь собраны все функции, которые генерируют клавиатуры VK.
# --------------------------------------------------------------------
import json  # превращаем dict -> JSON-строку
from typing import List, Dict, Any  # подсказки типов

Color = str  # для короткой записи
PRIMARY = "primary"
SECONDARY = "secondary"
POSITIVE = "positive"
NEGATIVE = "negative"


# Что можно прикрутить - UX-улучшение - Листалки FAQ/проектов сейчас «висят» внизу до конца диалога.
# При желании добавить
# make_kb_inline и использовать его для стрелок — клавиатура будет исчезать вместе с сообщением.
# def make_kb_inline(rows):
# return json.dumps({"inline": True, "buttons": rows}, ensure_ascii=False)


def _paginate(items: list, page: int, page_size: int):
    max_page = max((len(items) - 1) // page_size, 0)
    page = max(0, min(page, max_page))
    start = page * page_size
    return items[start:start + page_size]


def make_btn(
        label: str,  # надпись на кнопке
        cmd: str,  # команда, которую увидит bot_logic
        depth: int = 0,  # текущая «глубина» меню
        color: Color = PRIMARY,  # цвет кнопки (по умолчанию синий)
        data: Dict[str, Any] | None = None,  # доп. данные payload'а
        is_link_button: bool = False
) -> Dict[str, Any]:
    """
    Возвращает dict в формате VK «готовая кнопка».
    """
    # формируем payload, который уйдёт бот-логике
    payload: Dict[str, Any] = {"cmd": cmd, "depth": depth}
    if data:  # если есть доп. данные…
        payload["data"] = data  # …добавляем их
    button = {
        "action": {
            "type": "text",  # обычная кнопка-текст
            "label": label,  # подпись
            "payload": json.dumps(payload, ensure_ascii=False)  # JSON-payload
        },
        "color": color  # цвет кнопки
    }
    if is_link_button:  # для ссылки в кнопке
        button['action']['type'] = "open_link"
        title, link = label.split('|')  # label=f"Cсылка на проект:{proj['link_to_project']}",
        button['action']['link'] = link
        button['action']['label'] = title
        button.pop('color')
    return button


def make_kb(rows: List[List[Dict[str, Any]]],
            one_time: bool = False) -> str:
    """
    Преобразует список рядов кнопок в строку-JSON,
    которая напрямую передаётся в messages.send(..., keyboard=...)
    """
    kb_dict = {"one_time": one_time, "buttons": rows}  # структура клавиатуры VK
    return json.dumps(kb_dict, ensure_ascii=False)


# --------------------------------------------------------------------
# 3. Навигационный хвост («Назад» / «Главное меню»)
# --------------------------------------------------------------------


def nav_tail(depth: int) -> List[Dict[str, Any]]:
    buttons: List[Dict[str, Any]] = []

    if depth >= 1:
        buttons.append(
            make_btn("<- Назад", cmd="go_back",
                     depth=max(depth - 1, 0),  # уменьшаем глубину на 1
                     color=NEGATIVE)
        )

    if depth >= 2:
        buttons.append(
            make_btn("🏠 Главное меню", cmd="go_home",
                     depth=0,  # прыжок в корень
                     color=POSITIVE)
        )

    return buttons


def kb_main_menu() -> str:
    """
    Корневая клавиатура, которую показываем после /start.
    depth = 0, поэтому навигационных кнопок нет.
    """
    rows: List[List[Dict[str, Any]]] = [
        [make_btn("✍️ Задать вопрос",
                  cmd="menu_ask",
                  depth=0,
                  color=POSITIVE)],
        [make_btn("Посмотреть проекты",
                  cmd="menu_find",
                  depth=0,
                  color=PRIMARY)],

        [make_btn("❓ Частые вопросы",
                  cmd="menu_faq",
                  depth=0,
                  color=SECONDARY)],

        [make_btn("Контактная информация",
                  cmd="menu_help",
                  depth=0,
                  color=SECONDARY)]
    ]

    return make_kb(rows)


def kb_find_menu(depth: int = 1) -> str:
    """
    Экран, появляющийся после клика «Посмотреть проекты».
    Принимаем depth (по умолчанию 1), чтобы хвост рассчитывался правильно.
    """
    rows: List[List[Dict[str, Any]]] = [[make_btn("Посмотреть все проекты",
                                                  cmd="find_all_projects",
                                                  depth=depth,
                                                  data={"page": 0})],
                                        [make_btn("Фильтрация по направлению",
                                                  cmd="find_by_direction",
                                                  depth=depth)],
                                        [make_btn("Фильтрация по длительности",
                                                  cmd="find_by_duration",
                                                  depth=depth)], nav_tail(depth)]

    # добавляем хвост навигации («Назад» появится, «Главное меню» — нет)

    return make_kb(rows)


def kb_faq_page(faq_list: List[dict],
                page: int,
                page_size: int,
                depth: int = 1) -> str:
    """
    Клавиатура списка FAQ на заданной странице (page ≥ 0).
    Показывает ≤5 вопросов + навигацию.
    """

    start = page * page_size
    slice_ = faq_list[start:start + page_size]
    max_page = (len(faq_list) - 1) // page_size
    rows: List[List[Dict[str, Any]]] = [
        [make_btn(
            label=str(item["question"])[:35] + "…" if len(item["question"]) > 35 else item["question"],
            cmd="faq_answer",
            depth=depth,
            data={"id": start + idx}  # абсолютный индекс вопроса
        )] for idx, item in enumerate(slice_)
    ]

    # ← / → навигация
    nav_row: List[Dict[str, Any]] = []
    if page > 0:
        nav_row.append(make_btn("<- Предыдущие вопросы", "faq_page", depth,
                                color=SECONDARY, data={"page": page - 1}))
    if page < max_page:
        nav_row.append(make_btn("Следующие вопросы ->", "faq_page", depth,
                                color=SECONDARY, data={"page": page + 1}))
    if nav_row:
        rows.append(nav_row)

    # только «Назад» из хвоста
    rows.append(nav_tail(depth))  # depth=1 → одна кнопка «Назад»

    return json.dumps({"buttons": rows, "one_time": False}, ensure_ascii=False)


def list_to_rows(items: List[Dict[str, Any]],
                 cmd: str,
                 depth: int,
                 key_name: str = "value") -> List[List[Dict[str, Any]]]:
    """
    Превращает список dict'ов (directions/durations) в ряды кнопок:
    два столбца в ряд. cmd – команда, которая должна быть в payload
    """
    rows, row = [], []
    for it in items:
        label = f"{it[key_name]}"
        row.append(make_btn(label, cmd, depth, data={"value": it[key_name]}))
        if len(row) == 2:  # 2 кнопки – перенос строки
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return rows


def kb_directions_menu(directions: List[Dict[str, Any]],
                       depth: int = 1) -> str:
    """Клавиатура выбора направления"""
    rows = list_to_rows(directions, "direction_selected", depth)
    rows.append(nav_tail(depth))  # «Назад» появится автоматически
    return json.dumps({"buttons": rows, "one_time": False}, ensure_ascii=False)


def kb_durations_menu(durations: List[Dict[str, Any]],
                      depth: int = 1) -> str:
    """Клавиатура выбора длительности"""
    rows = list_to_rows(durations, "duration_selected", depth)
    rows.append(nav_tail(depth))
    return json.dumps({"buttons": rows, "one_time": False}, ensure_ascii=False)


def kb_projects_page(projects: List[Dict[str, Any]],
                     page: int,
                     page_size: int,
                     depth: int,
                     extra_filter: Dict[str, str] | None = None) -> str:
    """
    Формирует клавиатуру со списком проектов (по кнопке «Подробнее» каждый).
    """
    rows = []
    for p in _paginate(projects, page, page_size):
        rows.append([
            make_btn(
                label=(p["title"][:36] + "…") if len(p["title"]) > 36 else p["title"],
                cmd="project_details",
                depth=depth,  # остаёмся на том же уровне
                data={  # передаём КОНТЕКСТ
                    "title": p["title"],
                    **(extra_filter or {}),
                    "page": page
                }
            )
        ])

    # Кнопки «← Пред» | «След →»
    nav_row: List[Dict[str, Any]] = []
    if page > 0:
        # передаём те же фильтры + уменьшенный page
        nav_row.append(
            make_btn("<- Предыдущие", "projects_page",
                     depth=depth,
                     color=SECONDARY,
                     data={"page": page - 1, **(extra_filter or {})})
        )
    if (page + 1) * page_size < len(projects):
        nav_row.append(
            make_btn("Следующие ->", "projects_page",
                     depth=depth,
                     color=SECONDARY,
                     data={"page": page + 1, **(extra_filter or {})})
        )
    if nav_row:
        rows.append(nav_row)

    # Добавляем «Назад / Главное меню»
    tail = [make_btn("🔙 Назад",
                     cmd="go_back",
                     depth=depth - 1,
                     color=NEGATIVE,
                     data={**(extra_filter or {}), "page": page})]
    if depth >= 2:  # глубина ≥2 → показываем «Главное меню»
        tail.append(
            make_btn("🏠 Главное меню",
                     cmd="go_home",
                     depth=0,
                     color=POSITIVE)
        )
    rows.append(tail)
    return json.dumps({"buttons": rows, "one_time": False}, ensure_ascii=False)


def kb_ask_page(depth: int = 1) -> str:
    """
    Клавиатура появляется если пользователь выбрал Задать вопрос
    """
    rows: List[List[Dict[str, Any]]] = [nav_tail(depth)]
    return make_kb(rows)


__all__ = [
    "kb_main_menu",
    "kb_find_menu",
    "kb_faq_page",
    "kb_directions_menu",
    "kb_durations_menu",
    "kb_projects_page",
    "make_btn",
    "nav_tail",
    "list_to_rows",
    "PRIMARY",
    "SECONDARY",
    "POSITIVE",
    "NEGATIVE",
]
