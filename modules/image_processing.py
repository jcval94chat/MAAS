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
            img = rotar_o_reflejar_imagen(img, 'rotar', img_info['O'])
            left, top, width, height = img_info['Posición']
            img = img.resize((width, height))
            imagen_fondo.paste(img, (left, top), img)
        except Exception as e:
            if verbose:
                print("Error al procesar la imagen:", img_info['Imagen1'], e)

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
