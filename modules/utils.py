
import re
import random
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
        
    asociacion_nuevos_sentimientos = {
        'Innovador': 'happy',
        'Tradicional': 'happy',
        'Asombro': 'happy',
        'Ansiedad': 'happy',
        'Curiosidad': 'happy',
        'Indiferencia': 'happy',
        'Felicidad': 'happy',
        'Alegría': 'happy',
        'Energizado': 'happy',
        'Eufórico': 'happy',
        'Agradecido': 'happy',
        'Seguro': 'happy',
        'Paciente': 'happy',
        'Optimista': 'happy',
        'Motivación': 'happy',
        'Optimismo': 'happy',
        'Tranquilidad': 'happy',
        'Pasión': 'happy',
        'Simpatía': 'happy',
        'Empatía': 'happy',
        'Gratitud': 'happy',
        'Euforia': 'happy',
        'Generoso': 'happy',
        'Creativo': 'happy',
        'Amistoso': 'happy',
        'Sensible': 'happy',
        'Humilde': 'happy',
        'Valiente': 'happy',
        'Independiente': 'happy',
        'Alivio': 'happy',
        'Amor': 'happy',
        'Esperanza': 'happy',
        'Satisfecho': 'happy',
        'Confirmación': 'happy',
        'Entusiasmo': 'happy',
        'Adulación': 'happy',
        'Ambicioso': 'happy',
        'Curioso': 'happy',
        'Compasivo': 'happy',
        'Aventurero': 'happy',
        'Jovial': 'happy',
        'Espontáneo': 'happy',
        'Confiable': 'happy',
        'Lógico': 'happy',
        'happy': 'happy',
        'Ironía': 'happy',
        'Sarcasmo': 'happy',
        'Divertido': 'happy',
        'Compasión': 'happy',
        'Tristeza': 'sad',
        'Aburrido': 'sad',
        'Decaído': 'sad',
        'Inseguro': 'sad',
        'Impaciente': 'sad',
        'Pesimista': 'sad',
        'Contento': 'sad',
        'Egoísta': 'sad',
        'Insensible': 'sad',
        'Arrogante': 'sad',
        'Rígido': 'sad',
        'Cobarde': 'sad',
        'Dependiente': 'sad',
        'Modesto': 'sad',
        'Indiferente': 'sad',
        'Cruel': 'sad',
        'Cauteloso': 'sad',
        'Serio': 'sad',
        'Predecible': 'sad',
        'Desconfiado': 'sad',
        'Emotivo': 'sad',
        'Desesperación': 'sad',
        'Culpa': 'sad',
        'Nostalgia': 'sad',
        'Melancolía': 'sad',
        'Apatía': 'sad',
        'Anhelo': 'sad',
        'Resignación': 'sad',
        'Pesimismo': 'sad',
        'Desmotivación': 'sad',
        'Desilusión': 'sad',
        'sad': 'sad',
        'Enojo': 'angry',
        'Inquieto': 'angry',
        'Celoso': 'angry',
        'Hostil': 'angry',
        'Traducional': 'angry',
        'Resentido': 'angry',
        'Frustración': 'angry',
        'Ira': 'angry',
        'Disgusto': 'angry',
        'Odio': 'angry',
        'Celos': 'angry',
        'Envidia': 'angry',
        'Antipatía': 'angry',
        'Rebelión': 'angry',
        'Orgullo': 'angry',
        'Autoritario': 'angry',
        'angy': 'angry',
        'Corrección': 'angry',
        'Defensa': 'angry',
        'Inquisitivo': 'angry',
        'Descarte': 'angry',
        'Exasperación': 'angry',
        'Inexpresivo': 'serious',
        'Calmado': 'serious',
        'Tolerante': 'serious',
        'Práctico': 'serious',
        'Flexible': 'serious',
        'serious': 'serious',
        'Dudoso': 'serious',
        'Seriedad': 'serious',
        'Preocupado': 'worried',
        'Miedo': 'worried',
        'Avergonzado': 'worried',
        'Vergüenza': 'worried',
        'Ansioso': 'worried',
        'Agitado': 'worried',
        'Vago': 'worried',
        'worried': 'worried',
        'Sorprendido': 'surprised',
        'Asombrado': 'surprised',
        'surprised': 'surprised',
        'Escepticismo': 'surprised',
        'Desconcertado': 'dizzy',
        'Mareado': 'dizzy',
        'dizzy': 'dizzy',
        'Confusión': 'confused',
        'Confundido': 'confused',
        'confused': 'confused',
        'Asustado': 'scared',
        'Atemorizado': 'scared',
        'scared': 'scared',
        'Pensativo': 'a',
        'Desepcionado': 'a',
        'a': 'a',
        'Conformidad': 'a',
        'Meditabundo': 'a',
        'Reflexivo': 'a',
        'Filosófico': 'a',
        'Crítico': 'a',
        'Exultante': 'happy',
        'Desolado': 'sad',
        'Furioso': 'angry',
        'Sereno': 'serious',
        'Realista': 'realistic',
        'Perplejo': 'confused',
        'Atónito': 'surprised',
        'Encantado': 'happy',
        'Abatido': 'sad',
        'Desorientado': 'confused',
        'Simpático': 'cute',
        'Espantado': 'scared',
        'Estupefacto': 'surprised',
        'Conmocionado': 'impressed',
        'Perturbado': 'worried',
        'Desanimado': 'sad',
        'Entusiasmado': 'happy',
        'Decidido': 'serious',
        'Desesperado': 'worried',
        'Agobiado': 'worried',
        'Irónico': 'happy',
        'Emocionado': 'happy',
        'Tímido': 'cute',
        'Confiado': 'happy',
        'Exasperado': 'angry',
        'Nostálgico': 'sad',
        'Radiante': 'happy',
        'Solemne': 'serious',
        'Estresado': 'worried',
        'Vacilante': 'confused',
        'Intrigado': 'impressed',
        'Animado': 'happy',
        'Impetuoso': 'angry',
        'Vibrante': 'happy',
        'Sosegado': 'serious'
    }

    return equivalencias_sentimientos, asociacion_nuevos_sentimientos

def reorganize_dict_by_format(original_dict):
    """
    Reorganiza un diccionario basado en la posición de los elementos en las listas.
    El primer elemento se considera Horizontal y el segundo Vertical.

    Parameters:
    original_dict (dict): Diccionario original con las escenas y las rutas de los archivos.

    Returns:
    dict: Diccionario reorganizado con las claves 'Horizontal' y 'Vertical'.
    """
    # Inicializar nuevos diccionarios
    vertical_dict = {}
    horizontal_dict = {}

    # Reorganizar el diccionario basado en la posición
    for scene, paths in original_dict.items():
        if len(paths) >= 2:
            horizontal_path = paths[0]
            vertical_path = paths[1]

            if 'Horizontal' not in horizontal_dict:
                horizontal_dict['Horizontal'] = []
            horizontal_dict['Horizontal'].append({scene: horizontal_path})

            if 'Vertical' not in vertical_dict:
                vertical_dict['Vertical'] = []
            vertical_dict['Vertical'].append({scene: vertical_path})

    # Combinar los diccionarios vertical y horizontal en uno solo
    reorganized_dict = {**vertical_dict, **horizontal_dict}

    return reorganized_dict



def get_random_advice():
  todas_las_frases = [
    "Recuerda que después de la tormenta siempre llega la calma. ¡Tú puedes con esto!",
    "Eres más fuerte de lo que crees. Cada desafío te hace más grande.",
    "Hoy puede ser difícil, pero mañana es una nueva oportunidad para brillar.",
    "No estás solo/a. Tienes personas que te quieren y apoyan.",
    "Las cosas buenas llegan a los que saben esperar. ¡Mantén la esperanza!",
    "Cada pequeño paso cuenta. Sigue adelante, no te rindas.",
    "Nadie nació en el mundo para estar solo. ¡Nunca lo olvides!",
    "Tú salud es importante, procúrate",
    "A veces, lo que parece un final es solo un nuevo comienzo.",
    "Tu sonrisa es capaz de iluminar cualquier día oscuro. ¡Sonríe!",
    "Confía en ti y en tu capacidad para superar cualquier obstáculo.",
    "Cada día es una nueva oportunidad para empezar de nuevo. ¡Tú puedes!",
    "Tus esfuerzos no pasan desapercibidos. ¡Sigue adelante!",
    "Eres valiente y capaz. Este desafío es solo un paso más en tu camino.",
    "No importa cuán oscuro sea el cielo, siempre hay una estrella que brilla para ti.",
    "Tienes el poder de transformar los momentos difíciles en oportunidades.",
    "Cada experiencia te hace más fuerte. ¡Sigue aprendiendo!",
    "Tu valor y determinación son inspiradores. ¡Nunca te des por vencido/a!",
    "Las dificultades son temporales, pero tu perseverancia es permanente.",
    "Tu esfuerzo será en vano… Solo si no crees en ti mismo/a",
    "A veces se vale estar triste y llorar, sácalo de tu sistema. Abrazos",
    "Estás bien pinshi wapo/a",
    "Eres una persona increíblemente fuerte y capaz. ¡Ánimo!",
    "Recuerda que hay alguien que te ama",
    "A veces los obstáculos son oportunidades. ¡Enfréntalos con valentía!",
    "Las batallas se ganan antes de entrar al campo de batalla",
    "Conócete a ti mismo/a, recuerda algo bonito que te pasó este año",
    "Tu perseverancia te llevará a lugares maravillosos. ¡Sigue avanzando!",
    "Eres una fuente de inspiración para quienes te rodean. ¡Nunca lo olvides!",
    "Cada pequeño paso que das te acerca a tus sueños. ¡No te detengas!",
    "El mundo necesita tu luz y tu energía. -CFE",
    "¡Cree en ti, y en mí, que yo también creo en ti!",
    "Tu bondad y generosidad tienen un impacto positivo en quienes te rodean.",
    "Cada día es una nueva página en tu historia. -Kira",
    "Eres un ser único y especial. ¡El mundo es mejor contigo en él!",
    "No tomes decisiones permanentes basado en emociones temporales.",
    "Si el plan A no funciona, el abecedario tiene muchas más letras.",
    "A veces, lo mejor que puedes hacer es respirar y seguir adelante.",
    "Las pequeñas victorias son igual de importantes que las grandes.",
    "Si dudas de ti mismo/a, recuerda todo lo que has superado hasta ahora.",
    "No necesitas permiso de nadie para brillar.",
    "El cambio es difícil al principio, pero vale la pena al final.",
    "Si quieres resultados distintos, haz cosas diferentes.",
    "Recuerda que la motivación se agota, pero la disciplina te lleva lejos.",
    "Rodéate de personas que te hagan crecer, no de las que te desgasten.",
    "Tu energía es valiosa, no la gastes en cosas que no importan.",
    "Si sientes que todo va mal, recuerda que las tormentas también pasan.",
    "Dormir bien es un superpoder infravalorado.",
    "Si nadie te ha dicho algo bonito hoy, aquí va: ¡Eres increíble!",
    "No compares tu capítulo 1 con el capítulo 20 de alguien más.",
    "A veces, un descanso es la mejor forma de seguir avanzando.",
    "Los mejores recuerdos se crean cuando menos lo planeas.",
    "Descansa cuando lo necesites, pero no te rindas.",
    "No te tomes la vida tan en serio, nadie sale vivo de ella.",
    "Eres increíble, mucho ánimo.",
    "Los lunes no son tan malos si los acompañas con buena música.",
    "Las mejores ideas llegan en los momentos más inesperados.",
    "Cuida tu espalda, es el soporte de tu grandeza.",
    "La paciencia es una virtud, pero a veces una acción rápida es la mejor opción.",
    "Ser constante es mejor que ser perfecto.",
    "No todo es blanco o negro, a veces hay tonos de gris interesantes.",
    "No necesitas tener todo resuelto para empezar.",
    "Siempre hay tiempo para aprender algo nuevo.",
    "Tómate la vida en serio, pero no demasiado.",
    "Ríe mucho, porque la vida es más divertida con humor.",
    "Si fallas hoy, inténtalo de nuevo mañana.",
    "Si estás perdido, encuentra el camino.",
    "Si tienes sed, bebe agua.",
    "No es normal trabajar 2 horas extras cada día sin paga.",
    "Hacer 3 horas de viaje al trabajo diario no es normal.",
    "El tiempo extra no se paga con pizza.",
    "Cada error es una lección disfrazada, ¡aprende y sigue adelante!",
    "La adversidad es el trampolín que te impulsa hacia el éxito.",
    "La vida es un viaje; disfruta cada paso y cada pausa en el camino.",
    "Las pequeñas acciones de hoy se transformarán en los grandes logros de mañana.",
    "Tu actitud es la brújula que dirige tu destino.",
    "No temas tropezar; cada caída te enseña a levantarte con más fuerza.",
    "La constancia es la llave que abre las puertas del cambio.",
    "Si sientes miedo, recuerda que el coraje nace al enfrentarlo.",
    "Los desafíos son oportunidades disfrazadas para crecer y aprender.",
    "El verdadero éxito se construye con paciencia, esfuerzo y perseverancia."
]


  random_choice = random.choice(todas_las_frases)

  return random_choice
