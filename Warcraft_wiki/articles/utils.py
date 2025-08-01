# articles/utils.py

def split_text_logic(value, delimiter=","):
    """
    Принимает строку value и возвращает список, полученный путём разбиения строки по разделителю delimiter.
    Если value не является строкой, возвращает его без изменений.
    """
    if not isinstance(value, str):
        return value
    return value.split(delimiter)
