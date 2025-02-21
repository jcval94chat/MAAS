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



def get_sentimientos():
    """
    Genera dos diccionarios:
      1. equivalencias_sentimientos: Asocia ciertos sentimientos a otros (por ejemplo, para normalizar o agrupar).
      2. asociacion_nuevos_sentimientos: Asigna a cada sentimiento nuevo (de una lista predefinida)
         una categoría estándar basada en listas predefinidas de sentimientos.
    
    Retorna:
      (equivalencias_sentimientos, asociacion_nuevos_sentimientos)
    """
    # Diccionario de equivalencias basado en la lista original.
    equivalencias_sentimientos = {
        'happy': 'a',
        'a': 'serious',
        'serious': 'realistic',
        'angry': 'confused',
        'realistic': 'a',
        'sad': 'serious',
        'confused': 'surprised',
        'surprised': 'a',
        'cute': 'happy',
        'scared': 'angry',
        'dizzy': 'confused',
        'impressed': 'happy',
        'worried': 'sad'
    }

    # Lista de nuevos sentimientos a asociar.
    nuevos_sentimientos = [
        'Innovador', 'Tradicional', 'Asombro', 'Ansiedad', 'Curiosidad', 'Indiferencia'
    ]

    # Listas de sentimientos de referencia para cada categoría.
    sent_happy = [
        'Felicidad', 'Alegría', 'Energizado', 'Eufórico', 'Agradecido', 'Seguro', 'Paciente', 'Optimista',
        'Motivación', 'Optimismo', 'Tranquilidad', 'Pasión', 'Simpatía', 'Empatía', 'Gratitud', 'Euforia',
        'Generoso', 'Creativo', 'Amistoso', 'Sensible', 'Humilde', 'Valiente', 'Independiente',
        'Alivio', 'Amor', 'Esperanza', 'Satisfecho', 'Confirmación', 'Entusiasmo', 'Adulación',
        'Ambicioso', 'Curioso', 'Compasivo', 'Aventurero', 'Jovial', 'Espontáneo', 'Confiable', 'Lógico',
        'happy', 'Ironía', 'Sarcasmo', 'Divertido', 'Compasión'
    ]
    sent_sad = [
        'Tristeza', 'Aburrido', 'Decaído', 'Inseguro', 'Impaciente', 'Pesimista', 'Contento',
        'Egoísta', 'Insensible', 'Arrogante', 'Rígido', 'Cobarde', 'Dependiente', 'Modesto',
        'Indiferente', 'Cruel', 'Cauteloso', 'Serio', 'Predecible', 'Desconfiado', 'Emotivo',
        'Desesperación', 'Culpa', 'Nostalgia', 'Melancolía', 'Apatía', 'Anhelo',
        'Resignación', 'Pesimismo', 'Desmotivación', 'Desilusión', 'sad'
    ]
    sent_angry = [
        'Enojo', 'Inquieto', 'Celoso', 'Hostil', 'Traducional', 'Resentido', 'Frustración',
        'Ira', 'Disgusto', 'Odio', 'Celos', 'Envidia', 'Antipatía', 'Rebelión', 'Orgullo',
        'Autoritario', 'angy', 'Corrección', 'Defensa', 'Inquisitivo', 'Descarte', 'Exasperación'
    ]
    sent_serious = [
        'Serio', 'Inexpresivo', 'Calmado', 'Tolerante', 'Práctico', 'Flexible', 'serious',
        'Dudoso', 'Seriedad'
    ]
    sent_worr = [
        'Preocupado', 'Miedo', 'Avergonzado', 'Vergüenza', 'Ansioso', 'Agitado', 'Vago', 'worried'
    ]
    sent_surp = [
        'Sorprendido', 'Asombrado', 'Curioso', 'surprised', 'Escepticismo'
    ]
    sent_diz = [
        'Desconcertado', 'Mareado', 'dizzy'
    ]
    sent_conf = [
        'Confusión', 'Confundido', 'confused'
    ]
    sent_scar = [
        'Asustado', 'Atemorizado', 'scared'
    ]
    sent_a = [
        'Indiferente', 'Pensativo', 'Decepcionado', 'a', 'Conformidad',
        'Meditabundo', 'Reflexivo', 'Filosófico', 'Crítico'
    ]

    # Diccionario para asociar los nuevos sentimientos con una categoría estándar.
    asociacion_nuevos_sentimientos = {}
    for sentimiento in nuevos_sentimientos:
        if sentimiento in sent_happy:
            asociacion_nuevos_sentimientos[sentimiento] = 'happy'
        elif sentimiento in sent_sad:
            asociacion_nuevos_sentimientos[sentimiento] = 'sad'
        elif sentimiento in sent_angry:
            asociacion_nuevos_sentimientos[sentimiento] = 'angry'
        elif sentimiento in sent_serious:
            asociacion_nuevos_sentimientos[sentimiento] = 'serious'
        elif sentimiento in sent_worr:
            asociacion_nuevos_sentimientos[sentimiento] = 'worried'
        elif sentimiento in sent_surp:
            asociacion_nuevos_sentimientos[sentimiento] = 'surprised'
        elif sentimiento in sent_diz:
            asociacion_nuevos_sentimientos[sentimiento] = 'dizzy'
        elif sentimiento in sent_conf:
            asociacion_nuevos_sentimientos[sentimiento] = 'confused'
        elif sentimiento in sent_scar:
            asociacion_nuevos_sentimientos[sentimiento] = 'scared'
        elif sentimiento in sent_a:
            asociacion_nuevos_sentimientos[sentimiento] = 'a'
        else:
            # Valor por defecto para sentimientos sin una correspondencia directa.
            asociacion_nuevos_sentimientos[sentimiento] = 'happy'

    return equivalencias_sentimientos, asociacion_nuevos_sentimientos

