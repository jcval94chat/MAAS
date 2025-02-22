import re
import os
import shutil
import unicodedata
import random

def normalizar_cadena(cadena):
    """
    Convierte la cadena a minúsculas, normaliza caracteres (NFKD) y elimina diacríticos.
    Retorna la cadena limpia sin espacios adicionales.
    """
    cadena = cadena.lower()
    cadena = ''.join(c for c in unicodedata.normalize('NFKD', cadena) if unicodedata.category(c) != 'Mn')
    return cadena.strip()

def buscar_archivos(directorio, string_busqueda):
    """
    Busca de forma recursiva en 'directorio' archivos cuyo nombre contenga 'string_busqueda'
    (tras normalizar ambos). Retorna una lista de rutas encontradas.
    """
    archivos_encontrados = []
    busq_norm = normalizar_cadena(string_busqueda)
    for raiz, _, archivos in os.walk(directorio):
        for archivo in archivos:
            if busq_norm in normalizar_cadena(archivo):
                archivos_encontrados.append(os.path.join(raiz, archivo))
    return archivos_encontrados

def get_folder_content(folder_path):
    """
    Obtiene el contenido de una carpeta (archivos y subcarpetas) de forma recursiva
    y lo retorna ordenado por la fecha de creación.
    """
    files = []
    for entry in os.listdir(folder_path):
        full_path = os.path.join(folder_path, entry)
        if os.path.isfile(full_path) or os.path.isdir(full_path):
            files.append(full_path)

    extended_files = []
    for file in files:
        if os.path.isdir(file):
            extended_files.extend(get_folder_content(file))
        else:
            extended_files.append(file)

    files_sorted_by_creation = sorted(extended_files, key=os.path.getctime)
    return files_sorted_by_creation

def move_and_rename_file(file_path, new_directory, new_file_name):
    """
    Mueve un archivo desde 'file_path' a 'new_directory' y luego lo renombra a 'new_file_name'.
    
    Args:
        file_path (str): Ruta actual del archivo.
        new_directory (str): Nuevo directorio donde se moverá el archivo.
        new_file_name (str): Nuevo nombre para el archivo.
    
    Returns:
        str: La ruta completa del archivo renombrado.
    """
    new_path_with_old_name = shutil.move(file_path, new_directory)
    new_file_path = os.path.join(new_directory, new_file_name)
    os.rename(new_path_with_old_name, new_file_path)
    return new_file_path

def create_folder(path):
    """
    Crea la carpeta especificada en 'path' si no existe.
    
    Args:
        path (str): Ruta de la carpeta a crear.
    """
    if not os.path.exists(path):
        os.makedirs(path)


def get_chapter_number(path):
    # Lista todos los archivos en el directorio especificado
    archivos = os.listdir(path)

    max_num = 0
    pattern = re.compile(r'Caps_(\d+)')

    for archivo in archivos:
        match = pattern.match(archivo)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num

    return max_num + 1

def get_paths_save(rutas_vid, n_chapter=random.randint(1, 1000000)):
    # 10 minutos por un video de
    ruta_audio = '/content/drive/MyDrive/MAAS/Media/Eff Sonido/Background/background.mp3'
    ruta_audio = '/content/drive/MyDrive/MAAS/Media/Eff Sonido/Background/Acelerado_Sonic The Hedgehog OST - Green Hill Zone.mp3'
    ruta_audio = '/content/drive/MyDrive/MAAS/Media/Eff Sonido/Background/Pasarla bien_Menu - Cooking Mama Soundtrack.mp3'
    ruta_audio = '/content/drive/MyDrive/MAAS/Media/Eff Sonido/Background/background.mp3'  # Actualiza esto con la ruta de tu archivo de audio


    rutas_horizontal = [ruta for ruta in rutas_vid if '/BetaH/' in ruta]
    rutas_vertical = [ruta for ruta in rutas_vid if '/BetaV/' in ruta]

    output_paths = ['/content/drive/MyDrive/MAAS/Render/Horizontal/',
                    '/content/drive/MyDrive/MAAS/Render/Vertical/',]

    rutas_ending = ['/content/drive/MyDrive/MAAS/Media/Eff Sonido/Endings/END1.mp4',
                  '/content/drive/MyDrive/MAAS/Media/Eff Sonido/Endings/END1_V.mp4']

    output_paths_start = ['Caps_'+str(n_chapter)+'.mp4' for x in output_paths]
    output_paths = [x+'Caps_'+str(n_chapter)+'.mp4' for x in output_paths]

    return ruta_audio, output_paths, output_paths_start, rutas_ending

