import re


def is_valid_username(username):
    # Проверяем, что имя пользователя состоит только из латинских букв
    pattern = r'^[a-zA-Z]+$'
    return bool(re.match(pattern, username))


def is_valid_email(email):
    """
    Проверяет, является ли переданная строка корректным email-адресом.
    :param email: Строка, содержащая email-адрес.
    :return: True, если email-адрес корректен, иначе False.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email))
