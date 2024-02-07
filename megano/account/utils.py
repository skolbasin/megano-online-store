from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_fullname(user: type(User)):
    surname = ""
    first_name = ""
    last_name = ""
    if hasattr(user, "surname"):
        surname = user.surname
    if hasattr(user, "last_name"):
        last_name = user.last_name
    if hasattr(user, "first_name"):
        first_name = user.first_name

    return f"{last_name} {first_name} {surname}".strip()
