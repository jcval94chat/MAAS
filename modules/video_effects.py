import math
import numpy as np
import re
import time
import shutil
import os
import cv2
import random
import pandas as pd
from copy import deepcopy

from moviepy.video.fx.speedx import speedx
import moviepy.editor as mp
from moviepy.editor import VideoFileClip  # Se asume que se trabaja con clips de moviepy
from moviepy.editor import concatenate_videoclips, AudioFileClip, CompositeAudioClip

from modules.file_utils import buscar_archivos
from modules.audio_utils import extraer_informacion_audio
from config import (equivalencias_sentimientos, FONDOS_PATH, 
                    BASE_MEDIA_PATH, PERSONAJES_PATH, AUDIO_PATH,
                    CLIPS_PATH,
                    Posiciones_fondos, Posiciones_personajes, Posiciones_textos)

# Se importa create_folder desde file_utils para la función define_ruta_video.
from modules.file_utils import create_folder

from PIL import Image, ImageDraw, ImageFont

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


def crear_clips_de_imagenes(rutas_imagenes, duracion_por_imagen=1.9, 
                            ruta_audio=None, render = True, volumen_fondo = .5):
    clips = []

    for ruta in rutas_imagenes:

        clip = mp.ImageClip(ruta).set_fps(25).set_duration(duracion_por_imagen).resize((1920, 1080))

        ruta_audio = os.path.normpath(ruta_audio)
        # Si se proporciona una ruta de audio, agregar el audio al video
        if not ruta_audio is None:
            audio = AudioFileClip(ruta_audio).subclip(0, duracion_por_imagen).volumex(volumen_fondo)
            # Agregar fadeout al último segundo del audio
            audio = audio.audio_fadeout(.5)
            clip = clip.set_audio(audio)

        if render:
            rutas_video = ruta.replace('.png', '.mp4')
            clip.write_videofile(rutas_video, logger=None)
            clips.append(rutas_video)

        else:
            clips.append(clip)

    return clips


def generar_animacion_temblor(
    image_path,
    duration,
    fps=25,
    desplazamiento_max=5.0,
    umbral_bajo_canny=50,
    umbral_alto_canny=150,
    suavizado=True,
    color=True,
    escala_kernel_desplazamiento=9,
    extra_tremor_factor=1.0,
    blend_factor=0.4,
    size=(1920, 1080)
):
    """
    Crea un clip de MoviePy aplicando un efecto de temblor a la imagen `image_path`
    durante `duration` segundos a `fps` cuadros por segundo.

    El efecto se aplica desplazando la imagen original en áreas con bordes (detectados con Canny)
    y mezclándola con la imagen original para crear un sutil "temblor" sin alterar los colores originales.

    Parámetros
    ----------
    image_path : str
        Ruta de la imagen de entrada.
    duration : float
        Duración (en segundos) del clip resultante.
    fps : int
        Cuadros por segundo del video a generar.
    desplazamiento_max : float
        Desplazamiento máximo en píxeles para el temblor.
    umbral_bajo_canny : int
        Umbral inferior para el detector Canny.
    umbral_alto_canny : int
        Umbral superior para el detector Canny.
    suavizado : bool
        Si True, se aplica suavizado adicional al desplazamiento y a la imagen desplazada.
    color : bool
        Si True, se procesa en color (RGB); en caso contrario, se usa escala de grises.
    escala_kernel_desplazamiento : int
        Tamaño del kernel (impar) para suavizar el desplazamiento.
    extra_tremor_factor : float
        Factor multiplicativo extra para intensificar sutilmente el temblor.
    blend_factor : float
        Intensidad máxima de la mezcla en áreas con bordes.
    size : tuple (ancho, alto)
        Tamaño (en píxeles) de la salida.

    Retorna
    -------
    clip_temblor : mp.VideoClip
        Un clip de MoviePy con la animación de temblor aplicado.
    """
    # 1. Cargar la imagen y redimensionar usando LANCZOS para alta calidad
    img_pil = Image.open(image_path).convert("RGBA")
    img_pil = img_pil.resize(size, Image.LANCZOS)
    img_array = np.array(img_pil, dtype=np.uint8)

    # 2. Convertir a RGB (manteniendo los colores originales)
    img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
    # Obtener la imagen en escala de grises para detectar bordes
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    alto, ancho = img_gray.shape[:2]

    # 3. Detectar bordes con Canny (sobre la imagen en escala de grises)
    bordes = cv2.Canny(img_gray, umbral_bajo_canny, umbral_alto_canny)

    # 4. Asegurar que el kernel de suavizado tenga tamaño impar
    if escala_kernel_desplazamiento % 2 == 0:
        escala_kernel_desplazamiento += 1

    # 5. Crear malla de coordenadas
    coords_x, coords_y = np.meshgrid(np.arange(ancho), np.arange(alto))

    def make_frame(t):
        # Índice del fotograma actual
        n = int(np.floor(t * fps))
        # Generar desplazamientos aleatorios (usando n como semilla para reproducibilidad)
        rng = np.random.RandomState(n)
        dx = rng.uniform(-desplazamiento_max, desplazamiento_max, size=(alto, ancho)).astype(np.float32)
        dy = rng.uniform(-desplazamiento_max, desplazamiento_max, size=(alto, ancho)).astype(np.float32)
        dx *= extra_tremor_factor
        dy *= extra_tremor_factor

        # Suavizar los desplazamientos
        dx = cv2.GaussianBlur(dx, (escala_kernel_desplazamiento, escala_kernel_desplazamiento), 0)
        dy = cv2.GaussianBlur(dy, (escala_kernel_desplazamiento, escala_kernel_desplazamiento), 0)
        map_x = (coords_x + dx).astype(np.float32)
        map_y = (coords_y + dy).astype(np.float32)

        # Aplicar el desplazamiento a la imagen original para obtener la versión "temblorosa"
        img_displaced = cv2.remap(img_rgb, map_x, map_y,
                                  interpolation=cv2.INTER_LINEAR,
                                  borderMode=cv2.BORDER_REFLECT)
        if suavizado:
            img_displaced = cv2.GaussianBlur(img_displaced, (3, 3), 0)

        # Crear una máscara a partir de los bordes (valores entre 0 y 1)
        mask = (bordes.astype(np.float32) / 255.0)
        mask = cv2.GaussianBlur(mask, (3, 3), 0)
        mask_3 = np.stack([mask, mask, mask], axis=-1)

        # Mezclar la imagen original y la desplazada en función de la máscara
        # De esta forma, solo en las áreas con bordes (donde mask es alto) se aplica el temblor
        frame_f32 = img_rgb.astype(np.float32) * (1 - blend_factor * mask_3) + \
                    img_displaced.astype(np.float32) * (blend_factor * mask_3)
        frame_out = np.clip(frame_f32, 0, 255).astype(np.uint8)

        return frame_out

    # 6. Crear el VideoClip con la función make_frame
    clip_temblor = mp.VideoClip(make_frame, duration=duration).set_fps(fps)

    return clip_temblor

def extract_duration_from_filename(filename):
    # Dividir el nombre del archivo por "_"
    parts = filename.split("_")

    # Extraer la parte que contiene la duración
    duration_part = parts[5]

    # Extraer el número de la cadena de duración (asumiendo que siempre termina en ' segundos')
    duration = int(re.findall(r'\d+', duration_part)[0])

    return duration

def extraer_ultimo_parentesis(texto):
    # Busca todos los conjuntos de paréntesis en el texto
    matches = re.findall(r'\([^)]*\)', texto)
    # Devuelve el último conjunto encontrado, o una cadena vacía si no hay ninguno
    return matches[-1] if matches else ''


def get_path_info(image_path, img_por_escena):
    actividad_camara = extraer_ultimo_parentesis(image_path).replace('ala','*')
    parametros = extraer_parametros_de_lista([actividad_camara])
    poss___ = [dir.split('.')[0] for dir in image_path.split('_') if 'izq' in dir or 'dere' in dir][0]
    duration = extract_duration_from_filename(image_path)
    dur_app = max(2,int(round(duration,1)))

    return [b for a, b in parametros[0].items()]+[dur_app, poss___]



def Create_Scene_Media(
    escenas_info,
    lugar='Sala',
    chap_n=2,
    gen_vid=True,
    sounds='',
    verbose=False,
    apply_temblor_effect=False,
    sust_dd='',
):
    """
    Versión adaptada de la función original, en la que se puede aplicar un efecto de temblor
    en el mismo lugar donde se crea el ImageClip, respetando la duración, fotogramas,
    y la lógica de appends.
    """

    carpeta_h = BASE_MEDIA_PATH+f'/Caps/BetaH/Cap{chap_n}'
    create_folder(carpeta_h)
    carpeta_v = BASE_MEDIA_PATH+f'/Caps/BetaV/Cap{chap_n}'
    create_folder(carpeta_v)

    if verbose:
        print('Creando carpeta de recursos...')
    time.sleep(2)

    onomato_idea, Ambiente, sonidos_personas = get_onomatos()

    slides = []
    clips = []
    textos = []
    size = (1920, 1080)
    horizontal = True

    for carpeta_s in [carpeta_h, carpeta_v]:
        for escena in escenas_info.keys():
            # Copia de equivalencias
            eqqq = deepcopy(equivalencias_sentimientos)
            rutas_img_text = get_escena(escenas_info, escena, carpeta_s, lugar, 
                                        sonidos_personas, False, horizontal, 
                                        CLIPS_PATH+"/imagen_final.jpeg", sust_dd)
            rutas_img = list(rutas_img_text.keys())

            img_por_escena = len(rutas_img)

            for n, image_path in enumerate(rutas_img):
                accc__, inten___, addd__, duracion, posi = get_path_info(image_path, img_por_escena)
                if verbose:
                    print('Params:', accc__, inten___, addd__, duracion)

                # Crear un clip estático en primer lugar
                # (Se aplica la acción para las transformaciones internas)
                static_clip = mp.ImageClip(image_path).set_duration(duracion).resize(size).set_fps(25)
                static_clip = aplicar_accion(static_clip, accc__, inten___, posi)

                video_path = define_ruta_video(image_path)
                time.sleep(1)

                if apply_temblor_effect:
                    # Si se activa el efecto, generamos un clip con temblor
                    # usando la misma duración y fps
                    # 1. Guardar el fotograma resultante de static_clip en disco
                    #    (ya que la función de temblor parte de un 'image_path')
                    temp_image = CLIPS_PATH+"/temp_image.png"
                    # Extraer primer frame (es estático, así que cualquiera es igual)
                    frame = static_clip.get_frame(0)
                    Image.fromarray(frame).save(temp_image)

                    # 2. Llamar a función con los parámetros que desees
                    #    Ajusta desplazamiento_max o lo que consideres
                    clip_temblor = generar_animacion_temblor(
                        image_path=temp_image,
                        duration=duracion,
                        fps=25,
                        desplazamiento_max=10.0,   # Ajusta a tu gusto
                        umbral_bajo_canny=30,
                        umbral_alto_canny=120,
                        suavizado=True,
                        color=True,
                        escala_kernel_desplazamiento=10,
                        extra_tremor_factor=1.1,
                        blend_factor=0.8,
                        size=size
                    )

                    # 3. Si se desea generar el video en disco
                    if gen_vid:
                        clip_temblor.write_videofile(video_path,
                                                     codec='libx264',
                                                     fps=25, audio=False,
                                                     preset='ultrafast')

                    # 4. Añadir el clip a la lista
                    slides.append(video_path)
                    clips.append(clip_temblor)

                else:
                    # Flujo original (sin temblor): se escribe el clip
                    if gen_vid:
                        static_clip.write_videofile(video_path, ffmpeg_params=['-preset', 'ultrafast'])

                    slides.append(video_path)
                    clips.append(static_clip)

            textos.append(rutas_img_text)
        horizontal = False

    return slides, clips, textos



# Asociaciones y roles
def get_escena(escenas_info, escena_numb, carpeta_s, lugar,
               sonidos_personas_, verbose=True, orient=True, path_save = "", sust_dd=''):

  personaje_, tiempo_, emocion_, posic_, dialog_ = escenas_info[escena_numb]
  persona = sust_dd[personaje_]
  imagenes_guardadas = {}

  for i in range(len(dialog_)):
    if verbose:
      print('Parte: ', str(i))
    eqqq = deepcopy(equivalencias_sentimientos)
    text_d = dialog_[i]['Diálogo']

    es_onomato = text_d.replace("\'","") in list(sonidos_personas_.keys())

    det_ddd = dialog_[i]['Detalles']
    text_detalles = det_ddd.replace('*','ala')
    text_detalles = f'%s%s%s'%('(',text_detalles,')')
    # posiccc = 'izquierda'
    escena_numb = ' '.join([x if i==0 else x.zfill(8)
    for i, x in enumerate(escena_numb.split(' '))])
    dialog_u_onomato = 'ON' if es_onomato else 'DI'
    spth=f'%s_%s_%s_%s_%s_%s_%s_%s_%s.jpeg'%(escena_numb,str(i),
                                              persona, emocion_[1],
                                              lugar, str(tiempo_[i]+.2),
                                              text_detalles, emocion_[2],
                                             dialog_u_onomato)
    posiccc = emocion_[2]

    eqqq = deepcopy(equivalencias_sentimientos)
    if verbose:
      print('Obteneiendo IMG', persona, emocion_[1])

    grande = det_ddd.startswith('PP')

    gen_imagen(escenario=lugar,person=[persona],
            sentimiento=[emocion_[1]],texto=text_d,
              pos_fond = posiccc, save_path=path_save,
               verbose = verbose, grand = grande, horizontal=orient)

    if verbose:
      print('IMG obtenida')
    move_and_rename_file(path_save,carpeta_s, spth)
    # Guardar el texto en el nombre de la imagen
    imagenes_guardadas[carpeta_s+'/'+spth] = text_d.replace("\'","")
  return imagenes_guardadas

def gen_imagen(escenario='Sala', pos_fond = 'centro', person = ['Pollo','Pata'],
               sentimiento=['a','a'], texto = ' ', save_path="imagen_final.jpeg",
               horizontal=True, verbose=True, grand=False, resolucion = (1920, 1080)):


  dict_asss = {('centro',True):'',
  ('izquierda',True):' (1)',
  ('derecha',True):' (2)',
  ('centro',False):' (3)',
  ('izquierda',False):' (4)',
  ('derecha',False):' (5)'}

  pos_fondo = dict_asss[(pos_fond,horizontal)]
  ofi = f'/%s/Fondos de personajes%s.png'%(escenario, pos_fondo)
  lienzo2 = FONDOS_PATH+ofi

  df_personajes = get_dfpersonajes(PERSONAJES_PATH+'/personajes_animales',
                                   False,
                                   equivalencias_sentimientos)
  
#   df_personajes.to_csv(BASE_MEDIA_PATH+'/personajes.csv', 
#                        index=False)

  eqqq = deepcopy(equivalencias_sentimientos)
  # for person in personajes:
  if len(person) == 1:
    person.append(person[0])
    sentimiento.append(sentimiento[0])

  personajes = []
  for p, s in zip(person, sentimiento):
    if verbose:
      print('Obtener imagen', p, s)
    ruta_personaje = get_personaje_path(p, s, df_personajes, eqqq)
    if verbose:
      print('Imagen Obtenida: ', ruta_personaje)
    personajes.append(ruta_personaje)

  # print('Personajes: ',personajes)
  imagenes = get_img(lienzo2, personajes, grande=grand)
  # print('Img: ',imagenes)
  if verbose:
    print(imagenes)
  textos = get_txt(lienzo2, texto)
  crear_imagen_con_lienzo(lienzo2, imagenes, resolucion, textos, save_path, verbose)

def crear_imagen_con_lienzo(lienzo, imagenes, resolucion, 
                            textos, path_save, verbose=True):
    # Abrir el lienzo
    imagen_fondo = Image.open(lienzo)
    imagen_fondo = imagen_fondo.resize(resolucion)
    rotar = imagenes[0]['O']
    # Procesar cada texto
    draw = ImageDraw.Draw(imagen_fondo)

    oritentac_ = Posiciones_fondos[lienzo.split('/')[-1].replace('.png','')]
    # Procesar cada imagen
    if verbose:
      print('Gen image')
    for enn, img_info in enumerate(imagenes):
        # print('Leer img', img_info['Imagen1'])
        img = Image.open(img_info['Imagen1'])
        # print('Img leida')
        if img is None:
          print('Imagen no encontrada', img_info['Imagen1'])
        # print('NHE 01')
        img = rotar_o_reflejar_imagen(img, 'rotar', img_info['O'])

        if oritentac_ in ['H C']:
            # Si es la segunda imagen del centro
            if not (((len(imagenes)-1)==enn) and oritentac_ == 'H C'):
                pass
            else:
                img = rotar_o_reflejar_imagen(img, 'reflejo_horizontal')

        if oritentac_ in ['H D']:
            img = rotar_o_reflejar_imagen(img, 'reflejo_horizontal')

        if oritentac_ in ['V D','V C']:
            img = rotar_o_reflejar_imagen(img, 'reflejo_vertical')

        left, top, width, height = img_info['Posición']
        # left, top, width, height  = int(left), int(top), int(width), int(height)
        # print('Valores:',left, top, width, height, 'Tipos:',type(left), type(top), type(width), type(height))
        img = img.resize((width, height))
        imagen_fondo.paste(img, (left, top), img)

    if verbose:
      print('Gen TXT')
    for texto_info in textos:
        texto = texto_info['Texto']
        if texto == '':
          continue
        # texto[0] = int(texto[0])
        # texto[1] = int(texto[1])
        # print('A:', texto_info['Posición'])
        posicion = texto_info['Posición']
        tamaño_fuente = texto_info['Tamaño']
        color = texto_info.get('Color', 'black')
        limite_ancho = texto_info['Lim']

        # Configurar la fuente
        # if font is None:
        #     fuente = ImageFont.load_default()  # o ImageFont.truetype con una fuente específica
        # else:
        #     fuente = ImageFont.truetype(font, tamaño_fuente)
        fuente = ImageFont.load_default()
        # Dividir el texto en líneas si es necesario
        lineas = dividir_texto(texto, fuente, limite_ancho)
        # print(lineas)

        # Dibujar cada línea del texto
        if rotar == 0:
            y_actual = posicion[1]
            for linea in lineas:
                # Usar getbbox para obtener la altura de la línea de texto
                altura_linea = fuente.getmask(linea).getbbox()[3]
                draw.text((posicion[0], y_actual), linea, fill=color, font=fuente)
                y_actual += altura_linea

        elif rotar == 270:
            # lineas.append('________')
            # Calcular el tamaño de la imagen temporal basándose en la cantidad de líneas y el tamaño de la fuente
            altura_texto_total = sum(fuente.getmask(linea).getbbox()[3] for linea in lineas)
            ancho_texto_total = max(fuente.getmask(linea).getbbox()[2] for linea in lineas)

            # Calcula el margen que quieras añadir, por ejemplo 10 píxeles en cada dirección
            margen = 10
            # Calcular el tamaño de la imagen temporal basándose en la cantidad de líneas y el tamaño de la fuente
            altura_texto_total = sum(fuente.getmask(linea).getbbox()[3] for linea in lineas) + margen * len(lineas)
            ancho_texto_total = max(fuente.getmask(linea).getbbox()[2] for linea in lineas) + margen * 2


            # Crear una imagen temporal para todo el texto
            imagen_temporal = Image.new('RGBA', (ancho_texto_total, altura_texto_total), (255, 255, 255, 0))
            draw_temporal = ImageDraw.Draw(imagen_temporal)

            # Dibujar cada línea del texto en la imagen temporal usando el fragmento de código proporcionado
            y_actual = 0
            for linea in lineas:
                # Usar getbbox para obtener la altura de la línea de texto
                altura_linea = fuente.getmask(linea).getbbox()[3]
                draw_temporal.text((0, y_actual), linea, fill=color, font=fuente)
                y_actual += altura_linea

            # Rotar la imagen completa del texto
            imagen_texto_rotada = imagen_temporal.rotate(270, expand=True)

            # Calcular la nueva posición después de la rotación
            # La nueva posición es el punto de la esquina superior izquierda donde se quiere colocar el texto rotado
            posicion_rotada = (posicion[0]+60, posicion[1]+15)

            # Pegar la imagen rotada en la imagen principal
            imagen_fondo.paste(imagen_texto_rotada, posicion_rotada, imagen_texto_rotada)


    if verbose:
      print('imagen finalizada')
    # Guardar la imagen final
    imagen_fondo = imagen_fondo.convert("RGB")
    imagen_fondo.save(CLIPS_PATH+"/imagen_final.jpeg")

def dividir_texto(texto, fuente, limite_ancho):
    palabras = texto.split()
    lineas = []
    linea_actual = palabras[0]

    for palabra in palabras[1:]:
        # Verificar si la nueva palabra cabe en la línea actual
        # Usar getbbox para obtener la caja delimitadora del texto
        tamaño = fuente.getmask(linea_actual + ' ' + palabra).getbbox()
        if tamaño[2] - tamaño[0] <= limite_ancho:  # tamaño[2] - tamaño[0] es el ancho del texto
            linea_actual += ' ' + palabra
        else:
            # Si no cabe, añadir la línea actual a la lista y comenzar una nueva
            lineas.append(linea_actual)
            linea_actual = palabra

    # Añadir la última línea a la lista
    lineas.append(linea_actual)
    return lineas


def get_img(lienzo2, personajes, grande=False):
  # (left, top, ancho, alto)
  Posiciones_, pos_fondo = get_p_o(lienzo2, Posiciones_personajes)

  # print('Ifo posiciones\n',Posiciones_)
  # print('info pos_fondo\n', pos_fondo)

  if pos_fondo == 'H C':
    imagenes = [{'Imagen1': personajes[0], 'Posición': Posiciones_['I'],'O':Posiciones_['O']},
  {'Imagen1': personajes[1], 'Posición': Posiciones_['D'],'O':Posiciones_['O']}]
  elif  pos_fondo == 'H D':
    aumento = 'G' if grande else 'I'
    imagenes = [{'Imagen1': personajes[0], 'Posición': Posiciones_[aumento],'O':Posiciones_['O']}]
  elif  pos_fondo == 'H I':
    aumento = 'G' if grande else 'D'
    imagenes = [{'Imagen1': personajes[0], 'Posición': Posiciones_[aumento],'O':Posiciones_['O']}]
  elif  pos_fondo == 'V C':
    aumento = 'G' if grande else 'D'
    imagenes = [{'Imagen1': personajes[0], 'Posición': Posiciones_[aumento],'O':Posiciones_['O']}]
  elif  pos_fondo == 'V D':
    aumento = 'G' if grande else 'I'
    imagenes = [{'Imagen1': personajes[0], 'Posición': Posiciones_[aumento],'O':Posiciones_['O']}]
  elif  pos_fondo == 'V I':
    aumento = 'G' if grande else 'D'
    imagenes = [{'Imagen1': personajes[0], 'Posición': Posiciones_[aumento],'O':Posiciones_['O']}]

  return imagenes

def get_txt(lienzo, texto, grande=False):
  # (left, top, ancho, alto)
  Posiciones_, pos_fondo = get_p_o(lienzo, Posiciones_textos)

  if texto=='Bip bip':
    texto = '%!&$&# >:('

  aumento = 'G' if grande else 'I'
  left, top, ancho, alto = Posiciones_[aumento]
  text_rep = texto.replace(' ','')
  if text_rep=='':
    textos = [{'Texto': text_rep,
              'Posición': (left, top),
              'Tamaño': Posiciones_['T'],
              'Color': 'black',
              'Lim': Posiciones_['L']}]
  else:
    textos = [{'Texto': texto,
              'Posición': (left, top),
              'Tamaño': Posiciones_['T'],
              'Color': 'black',
              'Lim': Posiciones_['L']}]

  return textos

def get_p_o(lienzo_p, Posiciones):
    tipo_fondo = lienzo_p.split('/')[-1].split('.')[0]

    pf = Posiciones_fondos[tipo_fondo]
    # print(pf)
    orient = 0 if pf.split(' ')[0].upper() == 'H' else \
    (270 if pf.split(' ')[0].upper() =='V' else 0)
    try:
      Posiciones[pf]['O'] = orient
    except:
      pass

    return Posiciones[pf], pf


def rotar_o_reflejar_imagen(imagen, accion='rotar', valor=None):

    # Aplicar la acción elegida
    if accion == 'rotar':
        # Rotar la imagen n grados
        if valor is not None:
            imagen = imagen.rotate(valor)
    elif accion == 'reflejo_horizontal':
        # Reflejar la imagen horizontalmente
        imagen = imagen.transpose(Image.FLIP_LEFT_RIGHT)
    elif accion == 'reflejo_vertical':
        # Reflejar la imagen verticalmente
        imagen = imagen.transpose(Image.FLIP_TOP_BOTTOM)

    return imagen




def get_folder_content(folder_path):
  """Gets the content of a folder and sorts it by creation time.

  Args:
    folder_path: The path to the folder.

  Returns:
    A list of files and folders in the folder, sorted by creation time.
  """

  files = []
  for entry in os.listdir(folder_path):
    full_path = os.path.join(folder_path, entry)
    if os.path.isfile(full_path) or os.path.isdir(full_path):
      files.append(full_path)

  # Extender recursivamente para carpetas
  extended_files = []
  for file in files:
    if os.path.isdir(file):
      extended_files.extend(get_folder_content(file))
    else:
      extended_files.append(file)

  # Ordenar los archivos por momento de creación
  files_sorted_by_creation = sorted(extended_files, key=os.path.getctime)

  return files_sorted_by_creation



# Definiendo la función que procesa las imágenes
def reflejar_imagenes(df):
    for _, row in df.iterrows():
        if row['Mirada'] == 'right':
            ruta_imagen = row['Ruta']
            nombre_imagen = row['Nombre']
            # Leer la imagen
            try:
                imagen = Image.open(ruta_imagen)
            except FileNotFoundError:
                print(f"No se encontró la imagen en la ruta {ruta_imagen}")
                continue
            # Reflejar la imagen horizontalmente
            imagen_reflejada = imagen.transpose(Image.FLIP_LEFT_RIGHT)
            # Construir la nueva ruta con 'Correct_' al principio
            ruta_carpeta, archivo = os.path.split(ruta_imagen)
            nuevo_nombre = 'Correct_' + nombre_imagen.replace('right','left')
            nueva_ruta = os.path.join(ruta_carpeta, nuevo_nombre)

            if os.path.exists(nueva_ruta):
                print(f"La imagen ya existe: {nueva_ruta}")
                continue
            # Guardar la imagen reflejada
            imagen_reflejada.save(nueva_ruta, 'PNG')


def get_personaje_path(personaje, sentimiento, df_personajes, eqqq):
    df_pers = df_personajes[df_personajes['Mirada'] == 'left']
    df_personaje = df_pers[df_pers['Personaje'] == personaje]
    
    # Copia del diccionario para evitar modificar el original
    nuevo_eqqq = eqqq.copy()
    current_sentimiento = sentimiento
    
    while True:
        if current_sentimiento in df_personaje['Sentimiento'].tolist():
            df_personaje_sent = df_personaje[df_personaje['Sentimiento'] == current_sentimiento]
            return df_personaje_sent['Ruta'].values[0]
        else:
            # Si no existe un sentimiento alternativo, retorna None
            if current_sentimiento not in nuevo_eqqq:
                return None
            # Actualiza el sentimiento con el valor más cercano y lo elimina del diccionario
            current_sentimiento = nuevo_eqqq.pop(current_sentimiento)


def move_and_rename_file(file_path, new_directory, new_file_name):
    """Moves a file to a new directory and then renames it.

    Args:
      file_path: The current path of the file.
      new_directory: The new directory where the file will be moved.
      new_file_name: The new name for the file after moving.

    Returns:
      The new path to the file.
    """

    # Mueve el archivo al nuevo directorio manteniendo el mismo nombre
    new_path_with_old_name = shutil.move(file_path, new_directory)

    # Construye la ruta completa del nuevo archivo
    new_file_path = os.path.join(new_directory, new_file_name)

    # Renombra el archivo en la nueva ubicación
    os.rename(new_path_with_old_name, new_file_path)

    return new_file_path


def get_dfpersonajes(ruta_personajes, 
                     nuevas_img_right=False, 
                     eq_sent = equivalencias_sentimientos):
    """
    Recorre todos los archivos en 'ruta_base' y genera un DataFrame con las columnas:
    - Personaje (nombre de la penúltima carpeta, considerando '/' y '\')
    - Nombre (nombre del archivo)
    - Ruta (ruta completa normalizada)
    - Sentimiento (extraído del nombre del archivo si tiene el formato sentimiento_mirada.ext)
    - Mirada (extraído del nombre del archivo si tiene el formato sentimiento_mirada.ext)
    - Sentimiento_1 (asignado según reglas específicas)
    
    Parámetros:
    -----------
    ruta_base : str
        Ruta de la carpeta a inspeccionar. Ejemplo: '/content/drive/MyDrive/MAAS/Media/Personajes'

    Retorna:
    --------
    df : pd.DataFrame
        DataFrame con las columnas mencionadas.
    """

    data = []

    for root, dirs, files in os.walk(ruta_personajes):
        for file in files:
            # Ignoramos archivos ocultos o de sistema (que empiezan con '.')
            if file.startswith('.'):
                continue

            # Ruta completa normalizada para manejar '/' y '\'
            ruta_completa = os.path.normpath(os.path.join(root, file))

            # Dividimos la ruta usando el separador correcto del sistema operativo
            partes_ruta = ruta_completa.split(os.sep)

            # Obtenemos el "Personaje" como la penúltima carpeta
            personaje = partes_ruta[-2] if len(partes_ruta) > 1 else None

            # 'Nombre' será el nombre del archivo (ej. 'angry_left.png')
            nombre = file

            # Separamos la extensión para obtener 'sentimiento_mirada'
            nombre_sin_ext = os.path.splitext(file)[0]  # ej. 'angry_left'
            partes_nombre = nombre_sin_ext.split('_')

            # Extraemos "Sentimiento" y "Mirada" si el nombre sigue el patrón sentimiento_mirada
            if len(partes_nombre) == 2:
                sentimiento, mirada = partes_nombre
            else:
                sentimiento = partes_nombre[0] if len(partes_nombre) > 0 else None
                mirada = partes_nombre[1] if len(partes_nombre) > 1 else None

            # Guardamos la fila
            data.append({
                'Personaje': personaje,
                'Nombre': nombre,
                'Ruta': ruta_completa,
                'Sentimiento': sentimiento,
                'Mirada': mirada,
            })

    # Construimos el DataFrame
    df = pd.DataFrame(data, columns=[
        'Personaje',
        'Nombre',
        'Ruta',
        'Sentimiento',
        'Mirada',
    ])

    df['Sentimiento_1'] = df['Sentimiento'].map(eq_sent).fillna('a')
    
    # df['']

    return df


def ordenar_clips_audio(rutas_vid, clips_ls, text_in_img, personajes_car, ruta_audios, Dialogos_con_voz):

  per_se = personajes_car[['Personajes','Sexo']].copy()

  incorp_audio_dialogos = [(x.split('/')[-1].split('_')[2], y,z, i, '_'.join(x.split('/')[-1].split('_')[:2])) for i, (x, y, z) in
                  enumerate(zip(rutas_vid, clips_ls, text_in_img))
                  if (x.split('_')[-1].split('.')[0] != 'ON')]

  incorp_audio = [(x.split('/')[-1].split('_')[2], y,z, i, '_'.join(x.split('/')[-1].split('_')[:2])) for i, (x, y, z) in
                  enumerate(zip(rutas_vid, clips_ls, text_in_img))
                  if (x.split('_')[-1].split('.')[0] == 'ON')]

  onomato_idea, Ambiente, sonidos_personas = get_onomatos()
  sonidos_rutas = get_sonidos_rutas(sonidos_personas)
  onsx_per_ls = [(sonidos_rutas[ono], per_se[per_se['Personajes']==per]['Sexo'].values[0])
  for per, clip, ono, i, ll in incorp_audio]

  audios_validos = []
  for rutas, sx_voice, in onsx_per_ls:
    name_exclu = ' (man)' if sx_voice!='H' else ' (woman)'
    ls_auud = [ruta_info for ruta_info in rutas if (name_exclu not in ruta_info['ruta']) or
    (name_exclu.replace('man','men') not in ruta_info['ruta'])]
    audios_validos.append(random.choice(ls_auud))

  lista_clips = [y for x, y, z, i, ll in incorp_audio]
  lista_rutas_audio = [x['ruta'] for x in audios_validos]

  clips_con_audio = asignar_audio_a_clips(lista_clips, lista_rutas_audio)

  dialogo_key_audio__ = {(dd,'_'.join(ruta_audios[ll].split('/')[-1].split('-')[:2])):[ruta_audios[ll], ll]
                        for enu, (ll, dd) in enumerate(Dialogos_con_voz.items())}

  incorp_audio_dialogos_all = incorp_audio_dialogos+incorp_audio
  incorp_audio_dialogos_all = sorted(incorp_audio_dialogos_all, key=lambda x: x[3])

  #se salta las onomatos con if enu not in [x[3] for x in incorp_audio
  clip_audio_asign = [(clip[1], clip[3], dialogo_key_audio__[(clip[2], clip[4])])
  for enu, clip in enumerate(incorp_audio_dialogos_all) if enu not in [x[3] for x in incorp_audio]]

  lista_clips_dialogos = [a for a, b, c in clip_audio_asign]
  lista_rutas_audio_dialogos = [c[0] for a, b, c in clip_audio_asign]

  clips_con_audio_dialogos = asignar_audio_a_clips(lista_clips_dialogos, lista_rutas_audio_dialogos, 'audio corto')

  clips_con_dialogo, clips_con_onomato = [b for a, b, c in clip_audio_asign], [x[3] for x in incorp_audio]
  clips_otros = [i for i in range(len(clips_ls)) if i not in (clips_con_dialogo + clips_con_onomato)]

  clips_sin_audio = [clips_ls[nbr] for nbr in clips_otros]

  num_aud = [d for a, b, c, d, e in incorp_audio]

  clips_ordenados = {}
  Audio_fondo_activo = []

  for i , clip in enumerate(clips_ls):
    cond_audio_onomato = not (i in num_aud)

    if i in clips_con_dialogo:
      primer_clip = clips_con_audio_dialogos.pop(0)

    elif i in clips_con_onomato:
      primer_clip = clips_con_audio.pop(0)

    elif i in clips_otros:
      primer_clip = clips_sin_audio.pop(0)

    clips_ordenados[i] = primer_clip
    Audio_fondo_activo.append(cond_audio_onomato)

  len(clips_con_audio_dialogos), len(clips_con_audio), len(clips_sin_audio)

  # Audio_fondo_activo
  clips_ordered = list(clips_ordenados.values())

  return clips_ordered, Audio_fondo_activo

def concatenar_clips_segun_audio(clips, audio_activos):
    """Concatena clips seguidos donde el audio esté activo."""
    clips_procesados = []
    i = 0
    while i < len(clips):
        if audio_activos[i]:
            temp_clips = [clips[i]]
            i += 1
            while i < len(audio_activos) and audio_activos[i]:
                temp_clips.append(clips[i])
                i += 1
            clips_procesados.append((concatenate_videoclips(temp_clips), True))
        else:
            clips_procesados.append((clips[i], False))
            i += 1
    return clips_procesados


def asignar_audio_a_clips(lista_clips, lista_rutas_audio, modo_audio='cortar'):
    """
    Asigna audios a clips de video con la opción de buclear o cortar el audio.

    :param lista_clips: Lista de objetos VideoFileClip.
    :param lista_rutas_audio: Lista de rutas a los archivos de audio.
    :param modo_audio: 'bucle' para buclear el audio, 'cortar' para cortar el audio. Por defecto es 'cortar'.
    :return: Lista de clips de video con audio asignado.
    """
    clips_con_audio = []

    for clip, ruta_audio in zip(lista_clips, lista_rutas_audio):
        audio_clip = AudioFileClip(ruta_audio)

        if modo_audio == 'cortar':
            # Si la duración del audio es más larga que la del video, corta el audio
            if audio_clip.duration > clip.duration:
                audio_clip = audio_clip.subclip(0, clip.duration)
        elif modo_audio == 'bucle':
            # Si la duración del audio es más corta que la del video, buclea el audio
            audio_clip = audio_clip.loop(duration=clip.duration)
        elif modo_audio == 'audio corto':
            audio_clip = audio_clip

        clip = clip.set_audio(audio_clip)
        clips_con_audio.append(clip)

    return clips_con_audio

def get_chapter_render(clips_ordenamiento_aa, ruta_audio, lugar_quivalente, no_escena):
  rutas_escenas_render = []
  for i, videos_finales_clips in enumerate(clips_ordenamiento_aa):
      video_final = aplicar_audio_de_fondo(videos_finales_clips, ruta_audio)
      print('Renderizando Escena')
      orrntccn = 'hori_' if i == 0 else 'vert_'
      path_escena_video = CLIPS_PATH+'/Escena_'+orrntccn+str(no_escena)+'-'+lugar_quivalente+'.mp4'
      rutas_escenas_render.append(path_escena_video)

      video_final.write_videofile(path_escena_video,
                                  ffmpeg_params=['-preset', 'ultrafast'],
                                  logger=None)

  return rutas_escenas_render

def aplicar_audio_de_fondo(clips, ruta_audio, volumen_fondo=0.15):
    """Aplica audio de fondo a los clips indicados, ajustando el volumen del audio de fondo."""
    audio_background = AudioFileClip(ruta_audio)
    tiempo_acumulado = 0
    clips_finales = []

    for clip, audio_activo in clips:
        t_start = tiempo_acumulado
        if audio_activo and t_start < audio_background.duration:
            t_end = min(tiempo_acumulado + clip.duration, audio_background.duration)
            # if tiempo_acumulado>
            # Selecciona el subclip de audio de fondo correspondiente al tiempo acumulado y la duración del clip.
            # Ajusta el FPS de acuerdo a lo necesario y aplica el ajuste de volumen solo al audio de fondo.
            clip_audio_fondo = audio_background.subclip(t_start, t_end).set_fps(44100).volumex(volumen_fondo)

            if clip.audio:
                # Combina el audio original del clip con el audio de fondo ya ajustado en volumen.
                clip_audio = CompositeAudioClip([clip.audio, clip_audio_fondo])
            else:
                # Si el clip no tiene audio original, solo se usa el audio de fondo ajustado.
                clip_audio = clip_audio_fondo

            clip = clip.set_audio(clip_audio)
        clips_finales.append(clip)
        tiempo_acumulado += clip.duration

    return concatenate_videoclips(clips_finales)


def create_ordered_video(video_dict_list, clip_transicion, subl_clip,
                         ruta_ending, output_path, render=False, subl=True,
                         vertical=True, speed_factor=1.05):
    # Obtener la lista de videos en el orden correcto
    video_files = [list(d.values())[0] for d in video_dict_list]

    # Crear una lista de VideoFileClip objetos y ajustar la velocidad
    video_clips = [VideoFileClip(video).fx(speedx, factor=speed_factor) for video in video_files]

    # Crear una lista que contendrá los videos y las transiciones intercaladas
    ordered_clips = []

    for i, clip in enumerate(video_clips):
        ordered_clips.append(clip)
        # No agregar transición después del último video y manejar si solo hay un clip
        if i < len(video_clips) - 1 and len(video_clips) > 1:
            # Aplicar también el efecto de velocidad a las transiciones
            transition_clip = VideoFileClip(clip_transicion[i]).fx(speedx, factor=speed_factor)
            ordered_clips.append(transition_clip)

    if vertical:
        ordered_clips = [vid.rotate(90) for vid in ordered_clips]

    if subl:
        ordered_clips.append(VideoFileClip(subl_clip[0]))
    # Agregar el ending clip al final y ajustar la velocidad
    ending_clip = VideoFileClip(ruta_ending).fx(speedx, factor=speed_factor)
    ordered_clips.append(ending_clip)

    # print(ordered_clips)

    if render:
        # Concatenar todos los clips en uno solo
        final_clip = concatenate_videoclips(ordered_clips, method="compose")

        # Escribir el archivo de video resultante
        final_clip.write_videofile(output_path, verbose=True, logger=None)


def get_onomatos():
  onomato_idea = {'Snif, snif': 'Llorar o sollozar.',
                  'Cof, cof': 'Toser.',
                  '¿Eh?': 'Confusión.',
                  'Zzzz': 'Dormir.',
                  'Hmm': 'Duda o pensamiento.',
                  'Shhh': 'Pedir silencio.',
                  'Jaja': 'Risa en texto.',
                  'Ay': 'Sorpresa o dolor leve.',
                  'Eh': 'Llamar la atención o sorpresa.',
                  '¡Uh!': 'Golpe',
                  'Bu': 'Asustar o indicar sorpresa.',
                  'Uh-oh': 'Preocupación o error.',
                  'Tsk, tsk': 'Desaprobación o disgusto.',
                  'Huh': 'Confusión o sorpresa leve.',
                  'Brrr': 'Indicar frío.',
                  'Achoo': 'Estornudo.',
                  'Boo': 'Desaprobación o abucheo.',
                  'Ahhhh': 'Descanso o placer.',
                  'Yay': 'Alegría o celebración.',
                  'Eek': 'Miedo o sorpresa.',
                  'Psst': 'Llamar la atención sigilosamente.',
                  'Ugh': 'Desagrado.',
                  '¡Aha!': 'Surge una idea',
                  'Wow': 'Sorprendente',
                  '¡Ah...!': 'Bostezo',
                  'Gruñido': 'Expresión de disgusto o enfado.',
                  'Braaaack': 'Eructo',
                  'Prrrrt': 'Sonido de pedo',
                  'Dum!': 'Suspenso',
                  'Bip bip': 'Censura',
                  ':(':'Tristeza',
                  '...':'Silencio',
                  '':'Silencio'}

  Ambiente = {'Bosque':'ambiente de bosque por la mañana',
              'Teclados': 'Efecto de sonido escribiendo en teclado pc',
              'Poco Tráfico':'ambiente de ciudad poco trafico',
              'Ciudad noche':'ambiente de ciudad residencial de noche',
              'Tráfico pesado': 'ambiente de ciudad, trafico',
              'Oficina':'ambiente de oficina 2',
              'Correos':'ambiente de correos',
              'Gente pasando':'ambiente peatonal pasos',
              'Se abre puerta': 'puerta de madera chirrido',
              'Sala de juntas':'proyector de diapositiva'}

  sonidos_personas = {'Snif, snif': 'Sniffing Sound Effect',
  'Cof, cof': ['cof_corto_hombre (man)',
    'cof_woman (woman)'],
  '¿Eh?': ['Microsoft Windows XP Error'],
  'Zzzz': ['Roncar Ronquidos Efecto (man)',
    'Mujer que Ronca - Efecto de Sonido (HD) (woman)'],
  'Hmm': ['Minecraft Villager (huh) - Sound Effect',
    'KAHOOT Music (10 Second Countdown) 3_3'],
  'Shhh': 'shhhhhhhhh sound',
  'Jaja': ['Ha Sound Effect (man)', 'Risa de ibai'],
  'Ay': 'Duck Toy Squeak Dog Toy Sound Effect (download)',
  'Eh': ['Eh', 'MSN Sound'],
  '¡Uh!': ['ROBLOX Oof Sound Effect', 'Impact sound shitpost'],
  'Bu': 'Spongebob Boo-womp Sound Effect',
  'Uh-oh': ['ROBLOX Oof Sound Effect', 'MSN Sound'],
  'Tsk, tsk': 'Tsk Tsk (Solo el final)',
  'Huh': ['Duck Quack Sound Effect', 'Playstation 2 Startup Noise'],
  'Brrr': 'Freezing cold (Sound Effect)',
  'Achoo': ['mujer que estornuda (women)', 'Sneeze Sound Effect #2 (men)'],
  'Boo': 'SpongeBob Music Hawaiian',
  'Ahhhh': ['Funny Turtle Vine', 'Panting', 'Old Spice Silbido - Efecto de sonido'],
  'Yay': 'Angel - Sound Effect (HD)',
  'Eek': ['Moai sound', 'música perturbadora', 'FNAF ambiente 2'],
  'Psst': 'Psst sound effect (DOORS)',
  'Ugh': ['Diarrea - efecto de sonido (shitpost)',
    'Sonido de perturbación-incomodidad'],
  '¡Aha!': ['Microsoft Windows XP Startup Sound',
    'Windows 11 Startup Sound',
    'Microsoft Windows 95 sonido de inicio'],
  'Wow': 'Wow sound effect',
  '¡Ah...!': ['Sonido bostezo (women)', 'Hombre bostezando (man)'],
  'Gruñido': 'Gruñido de Monstruo Sonido',
  'Braaaack': 'eructos',
  'Prrrrt': ['Fart with reverb sound effect'],
  'Dum!': 'Impact sound shitpost',
  'Bip bip': 'Censor - Sound Effect (HD)',
  ':(': 'Poppy Playtime Theme',
                  '...':'Cricket Sound',
                  '':'Cricket Sound'}

  return onomato_idea, Ambiente, sonidos_personas

def get_sonidos_rutas(sonidos_personas, audio_path = AUDIO_PATH):
    """
    Dado un diccionario de sonidos (con nombres y rutas o lista de rutas),
    busca los archivos de audio en la ruta especificada en 'audio_path' utilizando
    la función buscar_archivos y retorna un diccionario con la información extraída.

    Parámetros:
      - sonidos_personas: Diccionario con claves que representan nombres y valores
                          que pueden ser una cadena o una lista de cadenas (nombres de sonidos).
      - audio_path: Ruta base donde buscar los archivos de audio.

    Retorna:
      Diccionario donde cada clave corresponde a una entrada de sonidos y el valor es
      una lista con la información extraída de cada archivo.
    """
    sonidos_rutas = {}
    for key, v in sonidos_personas.items():
        ls_rutas = []
        if isinstance(v, list):
            for x in v:
                x_agender = x.replace(' (man)', '').replace(' (woman)', '') \
                             .replace(' (men)', '').replace(' (women)', '')
                res_ = buscar_archivos(audio_path, x_agender)
                if len(res_) == 0:
                    print(key, ":_", x)
                else:
                    ls_rutas.append(extraer_informacion_audio(res_[0]))
        else:
            v_agender = v.replace(' (man)', '').replace(' (woman)', '') \
                         .replace(' (men)', '').replace(' (women)', '')
            res_ = buscar_archivos(audio_path, v_agender)
            if len(res_) == 0:
                print(key, ":", v)
            else:
                ls_rutas.append(extraer_informacion_audio(res_[0]))
        sonidos_rutas[key] = ls_rutas
    return sonidos_rutas

