import os
import pandas as pd
from PIL import Image

# Se asume que estos módulos se han creado en la estructura propuesta
from modules.file_utils import get_folder_content
from modules.utils import get_sentimientos

def get_personaje_path(personaje, sentimiento, df_personajes, eqqq):
    """
    Retorna la ruta de la imagen de un personaje dada su mirada 'left' y
    un sentimiento. Si el sentimiento exacto no se encuentra, busca el
    sentimiento más cercano (usando el diccionario 'eqqq').
    """
    df_pers = df_personajes[df_personajes['Mirada'] == 'left']
    df_personaje = df_pers[df_pers['Personaje'] == personaje]
    if sentimiento in df_personaje['Sentimiento'].tolist():
        df_personaje_sent = df_personaje[df_personaje['Sentimiento'] == sentimiento]
        return df_personaje_sent['Ruta'].values[0]
    else:
        # Buscar el sentimiento más cercano
        if sentimiento not in eqqq:
            return None
        nuevo_eqqq = eqqq.copy()
        sentimiento_cercano = nuevo_eqqq.pop(sentimiento)
        return get_personaje_path(personaje, sentimiento_cercano, df_personajes, nuevo_eqqq)

def reflejar_imagenes(df):
    """
    Recorre el DataFrame de personajes y, para aquellos cuya columna 'Mirada'
    sea 'right', crea una versión reflejada horizontalmente. Guarda la nueva
    imagen con el prefijo 'Correct_'.
    """
    for _, row in df.iterrows():
        if row['Mirada'] == 'right':
            ruta_imagen = row['Ruta']
            nombre_imagen = row['Nombre']
            try:
                imagen = Image.open(ruta_imagen)
            except FileNotFoundError:
                print(f"No se encontró la imagen en la ruta {ruta_imagen}")
                continue
            imagen_reflejada = imagen.transpose(Image.FLIP_LEFT_RIGHT)
            ruta_carpeta, _ = os.path.split(ruta_imagen)
            nuevo_nombre = 'Correct_' + nombre_imagen.replace('right', 'left')
            nueva_ruta = os.path.join(ruta_carpeta, nuevo_nombre)
            if os.path.exists(nueva_ruta):
                print(f"La imagen ya existe: {nueva_ruta}")
                continue
            imagen_reflejada.save(nueva_ruta, 'PNG')

def get_dfpersonajes(ruta_personajes='/content/drive/MyDrive/MAAS/Media/Personajes/', nuevas_img_right=False):
    """
    Genera un DataFrame con la información de los personajes (nombre, ruta, sentimiento,
    mirada) a partir del contenido de la carpeta indicada. Si 'nuevas_img_right' es True,
    se aplicará el reflejo a las imágenes cuya mirada sea 'right'.
    """
    # Se utiliza get_folder_content para obtener las rutas de archivos
    personajes_rutas = get_folder_content(ruta_personajes)
    personajes_rutas = [x.replace('Correct_', '') for x in personajes_rutas]
    df_personajes = pd.DataFrame(
        [(x.split(os.sep)[-2], x.split(os.sep)[-1], x)
         for x in personajes_rutas if not x.endswith('.rar')],
        columns=['Personaje', 'Nombre', 'Ruta']
    )
    df_personajes = df_personajes[~df_personajes['Personaje'].isin(['Tortuga', 'Cabeza'])]
    df_personajes['Sentimiento'] = df_personajes['Nombre'].apply(lambda x: x.split('_')[0])
    df_personajes['Mirada'] = df_personajes['Nombre'].apply(lambda x: x.split('_')[-1].replace('.png', ''))
    df_personajes['Sentimiento'] = df_personajes['Sentimiento'].apply(lambda x: x.replace('angy', 'angry').lower())
    
    if nuevas_img_right:
        reflejar_imagenes(df_personajes)
    
    # Se crea una tabla pivote (opcional, para ciertos usos)
    df_personajes_agg = pd.pivot_table(
        df_personajes, index=['Personaje', 'Mirada'],
        columns=['Sentimiento'], values='Ruta', aggfunc='first'
    ).reset_index()
    
    # Se obtienen las equivalencias de sentimientos
    equivalencias_sentimientos, _ = get_sentimientos()
    df_personajes['Sentimiento_1'] = df_personajes['Sentimiento'].map(equivalencias_sentimientos)
    df_personajes.reset_index(drop=True, inplace=True)
    
    # Corregir rutas que no existen: se le antepone 'Correct_' al nombre del archivo
    for x in range(len(df_personajes)):
        ruta_p = df_personajes.loc[x, 'Ruta']
        if not os.path.isfile(ruta_p):
            ruta_p_ls = ruta_p.split(os.sep)
            nueva_ruta = os.sep.join([
                item if i != (len(ruta_p_ls) - 1) else 'Correct_' + item
                for i, item in enumerate(ruta_p_ls)
            ])
            df_personajes.loc[x, 'Ruta'] = nueva_ruta
    return df_personajes

def get_personajes_features():
    """
    Retorna un DataFrame con las características de los personajes a partir de un CSV.
    """
    path_per = '/content/drive/MyDrive/MAAS/Media/Personajes/Descripciones/Avances Personajes Memorias de 7 - Personajes.csv'
    personajes_car = pd.read_csv(path_per)
    return personajes_car
