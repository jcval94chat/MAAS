"""
positions.py

Módulo encargado de gestionar las posiciones de fondos, personajes y textos.
Contiene los diccionarios originales y la función get_Posiciones para escalar
las posiciones de acuerdo a la resolución deseada.
"""

def get_Posiciones(ancho=960, alto=540):
    """
    Calcula y retorna las posiciones escaladas para fondos, personajes y textos
    en función de la resolución dada.
    
    Retorna:
      - Posiciones_fondos: Diccionario con la referencia del tipo de fondo.
      - personajes_escalados: Diccionario con las posiciones (left, top, ancho, alto)
        escaladas para cada fondo.
      - textos_escalados: Diccionario con las posiciones y offsets escalados para textos.
    """
    # Resolución base para las posiciones definidas
    base_ancho = 960
    base_alto = 540
    escala_x = ancho / base_ancho
    escala_y = alto / base_alto

    # Posiciones de fondos: solo referencias de posicionamiento
    Posiciones_fondos = {
        'Fondos de personajes': 'H C',
        'Fondos de personajes (1)': 'H D',
        'Fondos de personajes (2)': 'H I',
        'Fondos de personajes (3)': 'V C',
        'Fondos de personajes (4)': 'V D',
        'Fondos de personajes (5)': 'V I',
    }

    # Posiciones de personajes en la resolución base (left, top, ancho, alto)
    Posiciones_personajes = {
        'H C': {
            'I': [572, 182, 427, 427],
            'D': [60, 182, 427, 427],
            'G': [46, -31, 750, 750]
        },
        'H D': {
            'I': [150, 154, 427, 427],
            'G': [46, -31, 750, 750]
        },
        'H I': {
            'D': [484, 154, 427, 427],  # 220+264 = 484
            'G': [310, -31, 750, 750]    # 46+264 = 310
        },
        'V C': {
            'D': [126, 93, 407, 407],
            'G': [-68, -75, 691, 691]
        },
        'V D': {
            'I': [126, 93, 407, 407],
            'G': [-68, -75, 691, 691]
        },
        'V I': {
            'D': [85, 117, 346, 346],
            'G': [-155, -91, 737, 737]
        }
    }

    # Posiciones de textos en la resolución base.
    # 'I' es una lista [left, top, ancho, alto], 'L' y 'T' son offsets.
    Posiciones_textos = {
        'H C': {
            'I': [381, 6, 197, 261],
            'L': 250,
            'T': 40
        },
        'H D': {
            'I': [527, 49, 321, 298],
            'L': 250,
            'T': 40,
            'G': [681, 66, 321, 213]
        },
        'H I': {
            'I': [174, 35, 321, 314],  # 438-264 = 174
            'L': 250,
            'T': 42,
            'G': [415, 68, 321, 213]   # 679-264 = 415
        },
        'V C': {
            'I': [546, 116, 351, 321],
            'L': 300,
            'T': 42,
            'G': [546, 116, 351, 321]
        },
        'V D': {
            'I': [546, 116, 351, 321],
            'L': 300,
            'T': 42,
            'G': [546, 116, 351, 321]
        },
        'V I': {
            'I': [546, 116, 351, 321],
            'L': 300,
            'T': 42,
            'G': [546, 116, 351, 321]
        }
    }

    # Función auxiliar para escalar una lista de 4 valores (coordenadas y dimensiones)
    def escalar_lista(coord):
        return [
            int(round(coord[0] * escala_x)),  # left
            int(round(coord[1] * escala_y)),  # top
            int(round(coord[2] * escala_x)),  # ancho
            int(round(coord[3] * escala_y))   # alto
        ]

    # Escalar las posiciones de los personajes
    personajes_escalados = {}
    for key, subdict in Posiciones_personajes.items():
        subdict_escalado = {}
        for subkey, valor in subdict.items():
            if isinstance(valor, list) and len(valor) == 4:
                subdict_escalado[subkey] = escalar_lista(valor)
            else:
                subdict_escalado[subkey] = valor
        personajes_escalados[key] = subdict_escalado

    # Escalar las posiciones de los textos
    textos_escalados = {}
    for key, subdict in Posiciones_textos.items():
        subdict_escalado = {}
        for subkey, valor in subdict.items():
            if isinstance(valor, list) and len(valor) == 4:
                subdict_escalado[subkey] = escalar_lista(valor)
            elif subkey == 'L':
                subdict_escalado[subkey] = int(round(valor * escala_x))
            elif subkey == 'T':
                subdict_escalado[subkey] = int(round(valor * escala_y))
            else:
                subdict_escalado[subkey] = int(valor)
        textos_escalados[key] = subdict_escalado

    return Posiciones_fondos, personajes_escalados, textos_escalados
