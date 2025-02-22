"""
Módulo: image_processing.py
Este módulo contiene funciones relacionadas con el procesamiento de imágenes:
  - rotar_o_reflejar_imagen: Rota o refleja una imagen.
  - dividir_texto: Divide un texto en líneas para ajustarlo a un ancho máximo.
  - crear_imagen_con_lienzo: Compone una imagen final sobre un fondo insertando imágenes y textos.
  - get_img: Prepara la información de las imágenes (personajes) a colocar en el fondo.
  - get_txt: Prepara la información del texto a insertar en el fondo.
  - generar_imagen_ejemplo: Ejemplo de integración que utiliza las funciones anteriores para generar una imagen.
"""
import os
import zipfile
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter

def rotar_o_reflejar_imagen(imagen, accion='rotar', valor=None):
    """
    Rota o refleja una imagen utilizando PIL.

    Parámetros:
      - imagen: objeto PIL Image.
      - accion: 'rotar', 'reflejo_horizontal' o 'reflejo_vertical'.
      - valor: ángulo en grados para la rotación (si accion es 'rotar').

    Retorna:
      La imagen modificada.
    """
    if accion == 'rotar' and valor is not None:
        imagen = imagen.rotate(valor)
    elif accion == 'reflejo_horizontal':
        imagen = imagen.transpose(Image.FLIP_LEFT_RIGHT)
    elif accion == 'reflejo_vertical':
        imagen = imagen.transpose(Image.FLIP_TOP_BOTTOM)
    return imagen

def dividir_texto(texto, fuente, limite_ancho):
    """
    Divide un texto en múltiples líneas para que no exceda un ancho máximo.

    Parámetros:
      - texto: cadena de texto a dividir.
      - fuente: objeto ImageFont utilizado para medir el texto.
      - limite_ancho: ancho máximo permitido en píxeles.

    Retorna:
      Una lista de líneas resultantes.
    """
    palabras = texto.split()
    if not palabras:
        return []
    lineas = []
    linea_actual = palabras[0]
    for palabra in palabras[1:]:
        tamaño = fuente.getmask(linea_actual + ' ' + palabra).getbbox()
        if tamaño and (tamaño[2] - tamaño[0]) <= limite_ancho:
            linea_actual += ' ' + palabra
        else:
            lineas.append(linea_actual)
            linea_actual = palabra
    lineas.append(linea_actual)
    return lineas

def crear_imagen_con_lienzo(lienzo, imagenes, resolucion, textos, path_save, font=None, verbose=True):
    """
    Compone una imagen final sobre un fondo (lienzo) insertando imágenes y textos.

    Parámetros:
      - lienzo: ruta del archivo de fondo.
      - imagenes: lista de diccionarios con claves:
            'Imagen1': ruta de la imagen,
            'Posición': [left, top, width, height],
            'O': valor para rotación (por ejemplo, 0).
      - resolucion: tupla (ancho, alto) para redimensionar el fondo.
      - textos: lista de diccionarios con claves:
            'Texto': cadena a dibujar,
            'Posición': (left, top),
            'Tamaño': tamaño de fuente,
            'Color': color del texto,
            'Lim': ancho máximo en píxeles para el texto.
      - path_save: ruta donde se guardará la imagen final.
      - font: (opcional) ruta a la fuente para el texto.
      - verbose: si es True, imprime mensajes de progreso.
    
    Retorna:
      Ninguno, pero guarda la imagen final en 'path_save'.
    """
    imagen_fondo = Image.open(lienzo).resize(resolucion)
    draw = ImageDraw.Draw(imagen_fondo)

    # Procesar imágenes (personajes)
    for img_info in imagenes:
        try:
            img = Image.open(img_info['Imagen1'])
        except FileNotFoundError as fnf_error:
            if verbose:
                print(f"[ERROR] Imagen no encontrada: {img_info['Imagen1']}. Detalle: {fnf_error}")
            continue  # Saltamos esta imagen y continuamos con las demás
        except Exception as e:
            if verbose:
                print(f"[ERROR] Error al abrir la imagen {img_info['Imagen1']}: {e}")
            continue

        try:
            img = rotar_o_reflejar_imagen(img, 'rotar', img_info['O'])
            left, top, width, height = img_info['Posición']
            img = img.resize((width, height))
            imagen_fondo.paste(img, (left, top), img)
        except Exception as e:
            if verbose:
                print(f"[ERROR] Error al procesar la imagen {img_info['Imagen1']}: {e}")
    # Procesar textos
    for texto_info in textos:
        texto = texto_info['Texto']
        if not texto.strip():
            continue
        posicion = texto_info['Posición']
        tamaño_fuente = texto_info['Tamaño']
        color = texto_info.get('Color', 'black')
        limite_ancho = texto_info['Lim']
        fuente = ImageFont.load_default() if not font else ImageFont.truetype(font, tamaño_fuente)
        lineas = dividir_texto(texto, fuente, limite_ancho)
        y_actual = posicion[1]
        for linea in lineas:
            altura_linea = fuente.getmask(linea).getbbox()[3]
            draw.text((posicion[0], y_actual), linea, fill=color, font=fuente)
            y_actual += altura_linea

    imagen_fondo = imagen_fondo.convert("RGB")
    imagen_fondo.save(path_save)
    if verbose:
        print("Imagen generada y guardada en:", path_save)

def get_img(pos_fondo, personas, pos_personajes, grande=False):
    """
    Prepara la información de las imágenes (por ejemplo, personajes) a pegar en el fondo.

    Parámetros:
      - pos_fondo: clave para determinar la posición (por ejemplo, 'H C').
      - personas: lista de rutas de imágenes.
      - pos_personajes: diccionario con las posiciones base para personajes.
      - grande: bool, indica si se utiliza la posición "grande" ('G').

    Retorna:
      Una lista de diccionarios con información de cada imagen.
    """
    if pos_fondo in pos_personajes:
        base = pos_personajes[pos_fondo]
    else:
        base = pos_personajes.get('H C', {})

    if pos_fondo == 'H C' and len(personas) == 2:
        return [
            {'Imagen1': personas[0], 'Posición': base['I'], 'O': 0},
            {'Imagen1': personas[1], 'Posición': base['D'], 'O': 0},
        ]
    else:
        pos_key = 'G' if grande else 'I'
        if pos_key not in base:
            pos_key = 'D'
        return [{'Imagen1': personas[0], 'Posición': base[pos_key], 'O': 0}]

def get_txt(pos_fondo, texto, pos_textos, grande=False):
    """
    Prepara la información del texto a dibujar sobre el fondo.

    Parámetros:
      - pos_fondo: clave para determinar la posición en el fondo.
      - texto: cadena de texto a insertar.
      - pos_textos: diccionario con las posiciones base para textos.
      - grande: bool, indica si se usa la posición "grande" ('G').

    Retorna:
      Una lista con un diccionario que contiene la configuración del texto.
    """
    if pos_fondo in pos_textos:
        base = pos_textos[pos_fondo]
    else:
        base = pos_textos.get('H C', {})
    pos_key = 'G' if grande else 'I'
    left, top, ancho, alto = base.get(pos_key, [150, 150, 300, 300])
    return [{
        'Texto': texto,
        'Posición': (left, top),
        'Tamaño': base.get('T', 40),
        'Color': 'black',
        'Lim': base.get('L', 250)
    }]

def generar_imagen_ejemplo(
    fondo_path, pos_fondo, personajes_rutas, texto, pos_personajes=None, pos_textos=None,
    save_path="imagen_final.jpeg", resolucion=(960, 540), grande=False, verbose=True
):
    """
    Función de ejemplo que integra:
      - Obtención de información de imágenes mediante get_img.
      - Preparación del texto mediante get_txt.
      - Creación de la imagen final usando crear_imagen_con_lienzo.
    
    Parámetros:
      - fondo_path: ruta del fondo (lienzo).
      - pos_fondo: clave de posición en el fondo (ej. 'H C').
      - personajes_rutas: lista de rutas de imágenes de personajes.
      - texto: cadena de texto a insertar.
      - pos_personajes: diccionario con posiciones base para personajes. (Opcional)
      - pos_textos: diccionario con posiciones base para textos. (Opcional)
      - save_path: ruta donde se guardará la imagen final.
      - resolucion: tupla (ancho, alto) de la imagen final.
      - grande: bool, indica si se utiliza la posición "grande".
      - verbose: si True, imprime mensajes de progreso.
    """
    # Si no se han pasado los diccionarios de posiciones, obtenerlos según la resolución
    if pos_personajes is None or pos_textos is None:
        from modules.positions import get_Posiciones
        _, pos_personajes, pos_textos = get_Posiciones(resolucion[0], resolucion[1])
    
    # Obtener información de las imágenes y textos a insertar
    imgs_info = get_img(pos_fondo, personajes_rutas, pos_personajes, grande=grande)
    txt_info = get_txt(pos_fondo, texto, pos_textos, grande=grande)
    
    # Crear la imagen final
    crear_imagen_con_lienzo(
        lienzo=fondo_path,
        imagenes=imgs_info,
        resolucion=resolucion,
        textos=txt_info,
        path_save=save_path,
        verbose=verbose
    )


def get_img_transitions(textos_cambio_escena, verbb_ = True,
                        path='/content/drive/MyDrive/MAAS/Media/Transiciones', prefix=''):
    resolution = (960, 540)
    resolution = (1920, 1080)
    img_cambio = []
    for no_cambio, original_text in textos_cambio_escena.items():

        path_output = prefix+'output_%s.png'%(str(no_cambio))
        path_output_vertical = prefix+'output_%s_vertical.png'%(str(no_cambio))
        final_path__ = get_transicion(original_text, image_size = resolution,
                                      verbose = verbb_, output_path = path_output,
                                      horizontal = False, path = path)

        final_path__vertical = get_transicion(original_text, image_size = (resolution[1], resolution[0]),
                                              verbose = verbb_, output_path = path_output_vertical,
                                              horizontal = True, path = path)

        img_cambio.append((final_path__, final_path__vertical))

    return img_cambio


def get_ttf():
  dejavu = '/content/drive/MyDrive/MAAS/Media/Fuentes Letra/Nanum_Gothic.zip'

  # Ruta del archivo .zip
  zip_path = dejavu  # Cambia esto por el nombre de tu archivo .zip
  extract_path = 'Nanum_Gothic'

  # Descomprimir el archivo .zip
  with zipfile.ZipFile(zip_path, 'r') as zip_ref:
      zip_ref.extractall(extract_path)

  # Ruta a la fuente dentro de la carpeta descomprimida
  font_path = os.path.join(extract_path, 'static', 'Nanum_Gothic.ttf')  # Asegúrate de que esta ruta sea correcta

  return '/content/Nanum_Gothic/NanumGothic-ExtraBold.ttf'

def get_random_file(path):
  """
  Returns a random file from the given path.

  Args:
    path: The path to the directory containing the files.

  Returns:
    A random file from the given path.
  """
  files = os.listdir(path)
  return random.choice(files)

def split_text_into_lines(text, max_words=3, max_chars=17):
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        if len(' '.join(current_line + [word])) <= max_chars and len(current_line) < max_words:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines

def aplicar_filtro_a_imagen(imagen, tipo_filtro):
    # Abrir la imagen

    # Aplicar el filtro elegido
    if tipo_filtro == 'blanco_y_negro':
        imagen = imagen.convert('L')
    elif tipo_filtro == 'difuso':
        imagen = imagen.filter(ImageFilter.BLUR)
    elif tipo_filtro == 'sepia':
        sepia_filter = ImageOps.colorize(ImageOps.grayscale(imagen), (0, 0, 0), (255, 240, 192))
        imagen = sepia_filter
    elif tipo_filtro == 'contorno':
        imagen = imagen.filter(ImageFilter.CONTOUR)
    elif tipo_filtro == 'nitidez':
        imagen = imagen.filter(ImageFilter.SHARPEN)
    elif tipo_filtro == 'emboss':
        imagen = imagen.filter(ImageFilter.EMBOSS)
    elif tipo_filtro == 'inversion':
        imagen = ImageOps.invert(imagen)
    elif tipo_filtro == 'brillo':
        enhancer = ImageEnhance.Brightness(imagen)
        imagen = enhancer.enhance(1.5)  # Aumenta el brillo en un 50%
    elif tipo_filtro == 'contraste':
        enhancer = ImageEnhance.Contrast(imagen)
        imagen = enhancer.enhance(1.5)  # Aumenta el contraste en un 50%
    elif tipo_filtro == 'edge_enhance':
        imagen = imagen.filter(ImageFilter.EDGE_ENHANCE)

    return imagen

def create_text_image(original_text, background_path, font_path, output_path='output_image2.png',
                      image_size=(1080, 1920), rotar=0):
    texts = [""]+split_text_into_lines(original_text)+[""]

    # Cargar imagen de fondo
    background = Image.open(background_path)
    for i in range(9):
        background = aplicar_filtro_a_imagen(background, 'difuso')

    # Redimensionar la imagen manteniendo la relación de aspecto
    bg_ratio = background.width / background.height
    target_ratio = image_size[0] / image_size[1]

    if bg_ratio > target_ratio:
        # Si la imagen es más ancha que el target, ajustamos la altura y recortamos los bordes laterales
        new_height = image_size[1]
        new_width = int(new_height * bg_ratio)
    else:
        # Si la imagen es más alta que el target, ajustamos el ancho y recortamos los bordes superiores/inferiores
        new_width = image_size[0]
        new_height = int(new_width / bg_ratio)

    # background = background.resize((new_width, new_height), Image.ANTIALIAS)
    background = background.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Recortar la imagen para que coincida con el tamaño objetivo
    left = (new_width - image_size[0]) // 2
    top = (new_height - image_size[1]) // 2
    right = left + image_size[0]
    bottom = top + image_size[1]
    background = background.crop((left, top, right, bottom))

    # Crear objeto de dibujo
    draw = ImageDraw.Draw(background)

    # Obtener el tamaño de la imagen de fondo
    image_width, image_height = background.size

    # Inicializar tamaño de fuente grande y ajustar
    max_font_size = image_height // len(texts)  # Calcular un tamaño base grande

    # Función para ajustar el tamaño de la fuente según el ancho
    def adjust_font_size(draw, text, image_width, font_path, max_font_size):
        font_size = max_font_size
        font = ImageFont.truetype(font_path, font_size)
        while draw.textbbox((0, 0), text, font=font)[2] > image_width - 40:
            font_size -= 1
            font = ImageFont.truetype(font_path, font_size)
        return font

    # Calcular el tamaño de la fuente que se ajusta al ancho de la imagen para cada texto
    fonts = [adjust_font_size(draw, text, image_width, font_path, max_font_size) for text in texts]

    # Coordenadas iniciales para el texto, centrado verticalmente
    total_text_height = sum(draw.textbbox((0, 0), text, font=font)[3]
                            for text, font in zip(texts, fonts)) + (len(texts) - 1) * 20
    y = (image_height - total_text_height) // 2

    # Dibujar cada texto en la imagen con color blanco, centrado
    for text, font in zip(texts, fonts):
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2]
        text_height = text_bbox[3]
        x = (image_width - text_width) // 2  # Centrando horizontalmente
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        y += text_height + 20  # Ajustar la posición vertical para el siguiente texto con un espaciado

    # Rotar la imagen si el ángulo de rotación es diferente de 0
    if rotar != 0:
        background = background.rotate(rotar, expand=True)

    # Guardar la imagen
    background.save(output_path)

    return output_path

def get_transicion(original_text, image_size = (1920, 1080), verbose = False,
                   output_path = 'output_image2.png', horizontal = False,
                    path=''):
  font_path = get_ttf()
  rot_const = 270 if horizontal else 0


  random_file = get_random_file(path)
  background_path = path + '/' + random_file

  final_path = create_text_image(original_text, background_path, font_path, output_path, image_size, rot_const)

  # if verbose:
  #   # Mostrar la imagen en Colab (si estás usando Colab)
  #   background = Image.open(final_path)
  #   plt.imshow(background)
  #   plt.axis('off')  # Ocultar los ejes
  #   plt.show()

    # print(f"Image saved at: {final_path}")
  return final_path


