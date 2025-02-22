import os
import pandas as pd
import re
import json
from PIL import Image

# Se asume que estos módulos se han creado en la estructura propuesta
from modules.file_utils import get_folder_content
from modules.utils import get_sentimientos
from modules.audio_utils import get_onomatos

from openai import OpenAI

from config import PERSONAJES_PATH

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

def get_dfpersonajes(ruta_personajes=PERSONAJES_PATH, nuevas_img_right=False):
    """
    Genera un DataFrame con la información de los personajes a partir del contenido
    de la carpeta indicada. Si 'nuevas_img_right' es True, se aplicará el reflejo
    a las imágenes cuya mirada sea 'right'.
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
    
    # Se obtienen las equivalencias de sentimientos (asegúrate de tener la función get_sentimientos definida)
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
    path_per = './media/personajes/Descripciones/Avances_Personajes_Memorias_de_7.csv'
    personajes_car = pd.read_csv(path_per)
    return personajes_car

def get_dict_personajes_(ESCENAS_, verbose=True):
    OPENAI_API_KEY = 'sk-proj--...'
    client = OpenAI(api_key=OPENAI_API_KEY,)
    personajes = list(set([item for sublist in [c for a, b, c in ESCENAS_] for item in sublist]))
    pepepersonas = ', '.join(personajes)

    Dialogo_completo = '\n'.join([extraer_dialogos_con_sentimientos(escenas_info_)
    for escenas_info_, sentimientos, personajes in ESCENAS_])

    # Dialogo_completo = Dialogo_completo+' bueno jefazo'
    # Crear el mensaje para el modelo

    mensajes_jerarquia = [
        {"role": "system", "content": "Eres un asistente que ayuda a identificar la jerarquía laboral entre personajes según el contexto del diálogo. Analiza el tono, el contenido y las interacciones para determinar la jerarquía. Los personajes pueden tener la misma jerarquía."},
        {"role": "user", "content": f"Basándote en el siguiente diálogo, asigna una jerarquía laboral a los personajes {pepepersonas}. Usa números donde 0 es el nivel más bajo y 9 es el nivel más alto. Solo devuelve el diccionario tipo python con la asignación de jerarquías y nada más.\n\nDiálogo:\n{Dialogo_completo}"}
    ]

    diccionario_jerarquico = get_diccionario_jerarquico(mensajes_jerarquia)


    descripcion_personajes = "\n".join([f"{p[0]} (Sexo: {p[1]}, Rango: {p[2]}): {p[3]}" for p in personajes])

    contexto = f"Aquí está la lista de personajes (LP):\n{descripcion_personajes}\n"

    mensajes = [
        {"role": "system", "content": "Eres un asistente que ayuda a emparejar diálogos con los personajes que mejor se ajusten según sus características, rango laboral y sentimientos"},
        {"role": "user", "content": f"{contexto}"},
        {"role": "user", "content": f"Crea un diccionario donde las llaves sean los personajes del diálogo ({pepepersonas}) y los valores sean los nombres de la lista de personajes (LP) que mejor se ajusten a cada parte del diálogo. Solo devuelve el diccionario y solo el diccionario, sin explicaciones adicionales.\nLas posiciones son:\n{str(diccionario_jerarquico).replace('{','').replace('}','')}.\nDiálogo:\n{Dialogo_completo}"}
    ]
    
    # Crear una solicitud de finalización de chat
    respuesta = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=mensajes
    )
    if verbose:
      print(respuesta.choices[0].message.content)

    sust_dd = json.loads(respuesta.choices[0].message.content)

    return sust_dd

def get_diccionario_jerarquico(mensajes_jerarquia):
    OPENAI_API_KEY = 'sk-proj--...'
    client = OpenAI(api_key=OPENAI_API_KEY,)
    # Crear una solicitud de finalización de chat
    respuesta_jerarquia = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=mensajes_jerarquia,
        temperature=0.05
    )

    # Convertir jerarquía
    diccionario_jerarquico = convertir_jerarquia(respuesta_jerarquia.choices[0].message.content)
    return diccionario_jerarquico

def convertir_jerarquia(string):
    # Limpiar el string utilizando una expresión regular para mantener solo el contenido dentro de {}
    match = re.search(r'\{.*\}', string, re.DOTALL)
    if match:
        string_limpio = match.group(0)
    else:
        raise ValueError("No se encontró un contenido válido entre llaves {} en el string proporcionado.")

    # Convertir el string limpio en un diccionario
    # diccionario = json.loads(string_limpio)

    diccionario = json.loads(string_limpio)

    # Ordenar los nombres por los valores de mayor a menor
    ordenados = sorted(diccionario.items(), key=lambda item: item[1], reverse=False)

    # Crear una lista de etiquetas jerárquicas
    etiquetas_base = ["inferior", "superior", "superior superior"]

    # Generar etiquetas adicionales si es necesario
    while len(etiquetas_base) < len(ordenados):
        etiquetas_base.append(f"superior {'superior ' * (len(etiquetas_base) - 1)}")

    # Crear el nuevo diccionario jerárquico
    diccionario_jerarquico = {}

    # Asignar etiquetas jerárquicas
    last_value = None
    etiqueta_index = 0

    for i, (nombre, valor) in enumerate(ordenados):
        if last_value is not None and valor == last_value:
            diccionario_jerarquico[nombre] = etiquetas_base[etiqueta_index - 1]
        else:
            diccionario_jerarquico[nombre] = etiquetas_base[etiqueta_index]
            etiqueta_index += 1
        last_value = valor

    return diccionario_jerarquico

def extraer_dialogos_con_sentimientos(lista_escenas):
    onomato_idea, Ambiente, sonidos_personas = get_onomatos()
    dialogos = []
    onomats = list(onomato_idea.keys())
    for escena, detalles in lista_escenas.items():
        personaje = detalles[0]
        sentimiento = detalles[2][0]  # Sentimiento principal
        dialogos_escena = detalles[4]

        for dialogo in dialogos_escena:
            dialogo_texto = dialogo['Diálogo']
            if dialogo_texto in onomats:
                continue

            dialogos.append(f"{personaje} ({sentimiento}) : {dialogo_texto}")

    return "\n".join(dialogos)


