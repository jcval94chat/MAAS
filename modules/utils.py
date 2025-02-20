import re
import unicodedata

def normalizar_cadena(cadena):
    """
    Convierte la cadena a minúsculas, normaliza los caracteres para separar diacríticos y elimina espacios innecesarios.
    """
    cadena = cadena.lower()
    cadena = ''.join(c for c in unicodedata.normalize('NFKD', cadena) if unicodedata.category(c) != 'Mn')
    return cadena.strip()

def remove_duplicates_preserve_order(list1):
    """
    Elimina duplicados de una lista preservando el orden de aparición.
    """
    seen = set()
    result = []
    for item in list1:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result

def ordenar_diccionario_por_llave(diccionario):
    """
    Ordena un diccionario por sus llaves y retorna un nuevo diccionario ordenado.
    """
    llaves_ordenadas = sorted(diccionario.keys())
    diccionario_ordenado = {}
    for llave in llaves_ordenadas:
        diccionario_ordenado[llave] = diccionario[llave]
    return diccionario_ordenado

def remove_number_prefix(text):
    """
    Elimina prefijos numéricos al inicio de cada línea (números seguidos de un punto y un espacio o un espacio).
    """
    lines = text.split("\n")
    new_lines = []
    for line in lines:
        new_line = re.sub(r'^\d+(\. |\s)', '', line)
        new_lines.append(new_line)
    return "\n".join(new_lines)

def eliminar_osd_duplicados(texto):
    """
    Elimina líneas consecutivas duplicadas que comienzan con "OSD", conservando la primera aparición.
    """
    lineas = texto.splitlines()
    nuevas_lineas = []
    for linea in lineas:
        linea_stripped = linea.lstrip()
        if linea_stripped.startswith("OSD "):
            if nuevas_lineas and nuevas_lineas[-1].lstrip().startswith("OSD "):
                continue
        nuevas_lineas.append(linea)
    return "\n".join(nuevas_lineas)

def eliminar_segundo_osd_tras_sujeto(texto):
    """
    Busca la primera aparición de una línea de sujeto (que comienza con "[" y contiene "]") y,
    si el segundo renglón no vacío posterior es una línea OSD, la elimina. Se aplica solo a la primera aparición.
    """
    lineas = texto.splitlines()
    sujeto_index = None

    # Buscar la primera línea que inicia con "[" y contiene "]"
    for i, linea in enumerate(lineas):
        if linea.strip().startswith('[') and ']' in linea:
            sujeto_index = i
            break

    if sujeto_index is None:
        return texto

    contador = 0
    indice_candidato = None
    for i in range(sujeto_index + 1, len(lineas)):
        if lineas[i].strip():
            contador += 1
            if contador == 2:
                indice_candidato = i
                break

    if indice_candidato is not None:
        patron = re.compile(r'^\s*(\d+\.\s*)?OSD\b')
        if patron.match(lineas[indice_candidato]):
            del lineas[indice_candidato]

    return "\n".join(lineas)
