"""
Validadores reutilizables para todo el sistema.

validar_ruc_peru: algoritmo modulo 11 (SUNAT).
validar_dni_peru: longitud + solo digitos.
"""


def validar_ruc_peru(ruc: str) -> tuple[bool, str]:
    """
    Valida RUC peruano con algoritmo modulo 11.
    Retorna (es_valido, mensaje_error_o_vacio).
    """
    if not ruc:
        return False, "RUC vacio"
    ruc = ruc.strip()
    if not ruc.isdigit():
        return False, "RUC debe contener solo digitos"
    if len(ruc) != 11:
        return False, "RUC debe tener 11 digitos"
    if ruc[0:2] not in ("10", "15", "16", "17", "20"):
        return False, "RUC debe empezar con 10, 15, 16, 17 o 20"

    # Algoritmo modulo 11
    factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(ruc[i]) * factores[i] for i in range(10))
    resto = suma % 11
    digito_esperado = (11 - resto) % 10
    digito_real = int(ruc[10])

    if digito_esperado != digito_real:
        return False, "RUC invalido (digito verificador no coincide)"

    return True, ""


def validar_dni_peru(dni: str) -> tuple[bool, str]:
    """
    Valida DNI peruano: 8 digitos numericos.
    Retorna (es_valido, mensaje_error_o_vacio).
    """
    if not dni:
        return False, "DNI vacio"
    dni = dni.strip()
    if not dni.isdigit():
        return False, "DNI debe contener solo digitos"
    if len(dni) != 8:
        return False, "DNI debe tener 8 digitos"
    return True, ""
