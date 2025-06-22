from datetime import datetime


def format_date(date_str, input_format="%Y-%m-%d", output_format="%d/%m/%Y"):
    """Formatea una fecha de un formato a otro."""
    date_obj = datetime.strptime(date_str, input_format)
    return date_obj.strftime(output_format)


def calculate_age(birth_date, date_format="%Y-%m-%d"):
    """Calcula la edad a partir de la fecha de nacimiento."""
    birth_date = datetime.strptime(birth_date, date_format)
    today = datetime.today()
    age = (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )
    return age


def get_current_period():
    """Obtiene el período académico actual basado en la fecha."""
    today = datetime.today()
    year = today.year

    if 1 <= today.month <= 4:
        return f"{year}-1"
    elif 5 <= today.month <= 8:
        return f"{year}-2"
    else:
        return f"{year}-3"
