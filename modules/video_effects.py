import math
import numpy as np
import re
import os
from PIL import Image
from moviepy.editor import VideoFileClip  # Se asume que se trabaja con clips de moviepy

# Se importa create_folder desde file_utils para la función define_ruta_video.
from file_utils import create_folder


def zoom_in_effect(clip, zoom_ratio=0.04, start_time=0):
    """
    Aplica un efecto de zoom in a un clip de video.
    
    Args:
        clip: Objeto VideoFileClip de moviepy.
        zoom_ratio: Tasa de aumento del zoom.
        start_time: Tiempo en segundos a partir del cual iniciar el zoom.
        
    Returns:
        Clip de video modificado con efecto de zoom in.
    """
    def effect(get_frame, t):
        if t < start_time:
            return get_frame(t)
        effective_t = t - start_time
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        new_size = [
            math.ceil(base_size[0] * (1 + (zoom_ratio * effective_t))),
            math.ceil(base_size[1] * (1 + (zoom_ratio * effective_t)))
        ]
        # Asegurar que las dimensiones sean pares
        new_size[0] += new_size[0] % 2
        new_size[1] += new_size[1] % 2

        img = img.resize(new_size, Image.LANCZOS)
        x = math.ceil((new_size[0] - base_size[0]) / 2)
        y = math.ceil((new_size[1] - base_size[1]) / 2)
        img = img.crop([x, y, new_size[0] - x, new_size[1] - y]).resize(base_size, Image.LANCZOS)
        return np.array(img)

    return clip.fl(effect)


def pan_effect(clip, direction="right", pan_ratio=0.01, start_time=0):
    """
    Aplica un efecto de paneo (desplazamiento) a un clip de video.
    
    Args:
        clip: Objeto VideoFileClip de moviepy.
        direction: Dirección del paneo ("left", "right", "up" o "down").
        pan_ratio: Tasa de desplazamiento en función del tamaño del clip.
        start_time: Tiempo en segundos a partir del cual iniciar el paneo.
        
    Returns:
        Clip de video modificado con efecto de paneo.
    """
    def effect(get_frame, t):
        if t < start_time:
            return get_frame(t)
        effective_t = t - start_time
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        if direction in ["left", "right"]:
            pan_length = int(base_size[0] * pan_ratio * effective_t)
            if direction == "left":
                pan_length = -pan_length
            new_box = (pan_length, 0, base_size[0] + pan_length, base_size[1])
        else:  # Para "up" o "down"
            pan_length = int(base_size[1] * pan_ratio * effective_t)
            if direction == "up":
                pan_length = -pan_length
            new_box = (0, pan_length, base_size[0], base_size[1] + pan_length)

        img = img.crop(new_box).resize(base_size, Image.LANCZOS)
        return np.array(img)

    return clip.fl(effect)


def aplicar_accion(clip, accion, intensidad=1.0, posicion='izquierda'):
    """
    Aplica una acción sobre un clip de video en función del tipo de efecto indicado.
    
    Args:
        clip: Objeto VideoFileClip de moviepy.
        accion: Código de acción ("ES", "ZI", "ZO", "TI-A", "TI-B", o que empiece con "PP").
        intensidad: Valor numérico que determina la fuerza del efecto.
        posicion: Indica la posición (ej. 'izquierda') para ajustar el efecto.
        
    Returns:
        Clip de video modificado según la acción aplicada.
    """
    if intensidad <= 0:
        intensidad = 1.0

    factor = 0.05
    if accion in ['PA-I', 'PA-D']:
        factor /= 2
        accion = 'ZI'
    factor_inten = factor * intensidad

    if accion == "ES":  # Estático: sin modificación
        return clip
    elif accion == "ZI":  # Zoom In
        if posicion != 'izquierda':
            clip = pan_effect(clip, direction="right", pan_ratio=factor_inten/2)
        else:
            clip = pan_effect(clip, direction="left", pan_ratio=factor_inten/2)
        return zoom_in_effect(clip, zoom_ratio=factor_inten)
    elif accion == "ZO":  # Zoom Out
        if posicion != 'izquierda':
            clip = pan_effect(clip, direction="right", pan_ratio=factor_inten/2)
        else:
            clip = pan_effect(clip, direction="left", pan_ratio=factor_inten/2)
        return zoom_in_effect(clip, zoom_ratio=-factor_inten)
    elif accion == "TI-A":  # Tilt Arriba
        return pan_effect(clip, direction="down", pan_ratio=factor_inten)
    elif accion == "TI-B":  # Tilt Abajo
        return pan_effect(clip, direction="up", pan_ratio=factor_inten)
    elif accion.startswith('PP'):  # Primer Plano
        return zoom_in_effect(clip, zoom_ratio=factor_inten)
    else:
        return clip  # Acción no reconocida; se devuelve el clip original


def extraer_parametros_de_lista(lista_actividades):
    """
    Extrae parámetros de una lista de actividades representadas como cadenas.
    
    Cada actividad debe tener el formato:
        (tipo_accion *factor)
    donde *factor es opcional. Se devuelve una lista de diccionarios con:
        - 'accion': Tipo de acción.
        - 'intensidad': Factor numérico (1.0 por defecto).
        - 'Texto Adicional': Texto extra (si existe).
    
    Args:
        lista_actividades: Lista de cadenas con actividades.
        
    Returns:
        Lista de diccionarios con los parámetros extraídos.
    """
    patron = r'\(([^*]*)(?:\*([^)]+))?\)'
    resultados = []
    for actividad_camara in lista_actividades:
        acciones = re.findall(patron, actividad_camara)
        parametros_acciones = []
        for accion in acciones:
            tipo, factor = accion[0].strip(), accion[1].strip()
            factor = factor.split(' ')[0]
            if ' ' in tipo:
                tipo, texto_adicional = tipo.split(' ', 1)
            else:
                texto_adicional = ''
            parametros_acciones.append({
                'accion': tipo,
                'intensidad': float(factor) if factor else 1.0,
                'Texto Adicional': texto_adicional
            })
        resultados.extend(parametros_acciones)
    return resultados


def define_ruta_video(image_path):
    """
    Define la ruta de un video a partir de la ruta de una imagen.
    
    Reemplaza la extensión 'jpeg' por 'mp4' y modifica ciertos directorios.
    Se crea la carpeta destino si no existe.
    
    Args:
        image_path: Ruta original de la imagen.
        
    Returns:
        Nueva ruta generada para el video.
    """
    spl_ = image_path.split('/')
    spl_l = len(spl_)
    ruta_vid = '/'.join([x.replace('jpeg', 'mp4') if (i+1) == spl_l else
                         x.replace('Cap', 'Cap_video_') if (i+2) == spl_l else x
                         for i, x in enumerate(spl_)])
    carpeta_vid = '/'.join(ruta_vid.split('/')[:-1])
    create_folder(carpeta_vid)
    return ruta_vid
