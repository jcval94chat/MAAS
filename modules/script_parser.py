"""
script_parser.py

Módulo para el procesamiento y parseo de guiones.
Contiene funciones para convertir scripts en diccionarios,
extraer y limpiar diálogos, y eliminar duplicados o prefijos.
"""

from config import asociacion_nuevos_sentimientos
import re
import pandas as pd
import random
from langdetect import detect, DetectorFactory

def parse_script_to_dict(script):
    """
    Convierte un script en un diccionario de escenas.
    Cada escena se representa de la forma:
      "Escena XX": [personaje, duración, sentimiento, acción, [líneas de diálogo]]
    """
    lines = script.strip().replace("'", "").split('\n')
    scenes = {}
    scene_number = 0
    for line in lines:
        if line.startswith('[') and line.endswith(']'):
            continue
        if line.startswith('['):  # Inicio de una nueva escena
            scene_number += 1
            # Se asume formato: [Personaje](duración | sentimiento | acción)
            person_info = line.split(']')[0].strip('[')
            actions = line.split(']')[1].strip().strip('()')
            actions_parts = actions.split('|')
            duration = actions_parts[0].strip()
            sentiment = actions_parts[1].strip()
            action = actions_parts[2].strip()
            scenes[f'Escena {str(scene_number).zfill(8)}'] = [
                person_info, duration, sentiment, action, []
            ]
        else:
            if line:
                scenes[f'Escena {str(scene_number).zfill(8)}'][-1].append(line)
    return scenes

def extraer_ultimo_parentesis(texto):
    """
    Extrae el último grupo de caracteres que esté entre paréntesis.
    """
    matches = re.findall(r'\([^)]*\)', texto)
    return matches[-1] if matches else ''

def split_dialogos_detalles(dialogo):
    """
    Separa cada línea de diálogo en dos partes:
      - "Diálogo": el contenido del diálogo (sin los paréntesis finales)
      - "Detalles": el contenido extraído del último grupo entre paréntesis
    Retorna una lista de diccionarios.
    """
    list_dial = []
    for text in dialogo:
        paren_content = extraer_ultimo_parentesis(text)
        content = paren_content[1:-1]  # sin paréntesis
        accion_camara = content.split(',')[0]
        dialogo_part = '('.join(text.split('(')[:-1])
        if dialogo_part.startswith('OSD'):
            dialogue = extraer_ultimo_parentesis(dialogo_part)[1:-1]
        else:
            dialogue = dialogo_part
        list_dial.append({
            "Diálogo": dialogue,
            "Detalles": accion_camara
        })
    return list_dial

def limpiar_dialogo(lista):
    """
    Elimina cualquier texto entre paréntesis en el contenido del diálogo.
    """
    regex = r'\s*\([^)]*\)'
    for elemento in lista:
        elemento['Diálogo'] = re.sub(regex, '', elemento['Diálogo']).strip()
    return lista

def remove_duplicates_preserve_order(lista):
    """
    Elimina duplicados en una lista preservando el orden original.
    """
    seen = set()
    result = []
    for item in lista:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result

def remove_number_prefix(text):
    """
    Elimina prefijos numéricos (por ejemplo, "1. " o "2 ") al inicio de cada línea.
    """
    lines = text.split("\n")
    new_lines = []
    for line in lines:
        new_line = re.sub(r'^\d+(\. |\s)', '', line)
        new_lines.append(new_line)
    return "\n".join(new_lines)

def eliminar_osd_duplicados(texto):
    """
    Elimina líneas duplicadas que comienzan con "OSD " consecutivamente.
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
    Busca la primera línea que representa un sujeto (línea que inicia con '[' y contiene ']')
    y elimina el segundo renglón no vacío posterior si comienza con "OSD".
    """
    lineas = texto.splitlines()
    sujeto_index = None
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


def get_ESCENAS(script_inicial, l_disp = []):
  script_inicial = eliminar_osd_duplicados(script_inicial)
  script_inicial = eliminar_segundo_osd_tras_sujeto(script_inicial)
  script_inicial = remove_number_prefix(script_inicial)

  import datetime
  import os
    # Creamos el timestamp con el formato solicitado
  timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
  nombre_archivo = f"script_{timestamp}.txt"
  print('Guardando archivo: '+ nombre_archivo)
  folder_path = os.path.join("Guiones", "scripts")
  os.makedirs(folder_path, exist_ok=True)
  # Guardamos el contenido de 'script_inicial' en el archivo de texto
  full_path = os.path.join(folder_path, nombre_archivo)

  with open(full_path, 'w', encoding='utf-8') as f:
    f.write(script_inicial)

    # Detenemos la ejecución
    # exit()

  script_split = script_inicial.split('---')

  escenas_ = {}
  texto_cambio_escena = {}
  nn_ = 0
  for i, script in enumerate(script_split):
    if script.count('\n')==0:
      texto_cambio_escena[nn_] = script
    elif '**' in script:
      escenas_[nn_] = script
      nn_+=1

  ESCENAS = []
  LUGARES = []
  for numero_escena, script_inicial in escenas_.items():

    ultimas_lineas = [x.lower().strip().replace('*','') for x in script_inicial.split('\n')[-3:]]

    lugar_elegido = [x for x in ultimas_lineas if x in l_disp]

    if len(lugar_elegido)==0:
      print('Se asignará un lugar genérico')
      lugar___ = random.choice(l_disp)
    else:
      lugar___ = lugar_elegido[0]
    LUGARES.append(lugar___)
    ESCENAS.append(script_to_dict(script_inicial))

  return ESCENAS, LUGARES, texto_cambio_escena

def script_to_dict(script_inicial):
  dic_escenas = parse_script_to_dict(script_inicial)
  personajes = remove_duplicates_preserve_order([it[0] for key, it in dic_escenas.items()])

  # Ordenarlos por jerarquía personajes, y al revés si es de un país oriental
  # posiciones_per = {p:'izquierda' if i==0 else 'derecha' for i, p in enumerate(personajes)}
  posiciones__ = pd.pivot_table(pd.DataFrame([vl[0] for i, (k, vl) in enumerate(dic_escenas.items())]).reset_index(),
                index=[0], aggfunc='first').reset_index()

  posiciones__['index'] = posiciones__['index'].apply(lambda x: 'izquierda' if x%2==0 else 'derecha')
  posiciones_per = {per:pos for per, pos in posiciones__.values}

  escenas_info = {}
  for k, v in dic_escenas.items():
    personaje, tiempo, sentimiento, accion, dialogo = v
    if sentimiento.split(' ')[0] in asociacion_nuevos_sentimientos.keys():
      sentimiento_re = asociacion_nuevos_sentimientos[sentimiento.split(' ')[0]]
    else:
      print('Registrar:',sentimiento)
      sentimiento_re = 'happy'

    processed_texts = split_dialogos_detalles(dialogo)
    processed_texts = limpiar_dialogo(processed_texts)

    escenas_info[k] = [personaje, tiempo,
     (sentimiento, sentimiento_re,  posiciones_per[personaje]),
                       accion, processed_texts]
  sentimientos = list(set([it[2][0].split(' ')[0] for key, it in escenas_info.items()]))

  return escenas_info, sentimientos, personajes



# ------------------------------- Secciones sobre el idioma
def obtener_idioma(script_inicial: str, df_personajes) -> str:

    """
    Detecta el idioma del 'script_inicial' usando langdetect y retorna el nombre de la columna de apellidos
    correspondiente, basándose en las columnas disponibles en df_personajes.

    Se asume que las columnas siguen el formato 'Apellido_XX', donde XX es el código de idioma.
    Se mapea el código detectado (por ejemplo, 'es', 'en', 'ja', etc.) a los códigos internos (por ejemplo, 'ES', 'EN', 'JP').
    
    Si la detección falla o el idioma detectado no se encuentra entre las columnas permitidas,
    se utiliza por defecto 'Apellido_ES'. Si tampoco existe, se retorna la primera columna que cumpla el formato.
    """

    # 1. Extraer de df_personajes las columnas que empiezan con "Apellido_"

    DetectorFactory.seed = 0

    columnas_apellido = [col for col in df_personajes.columns if col.startswith("Apellido_")]
    if not columnas_apellido:
        return None  # o lanza una excepción si prefieres

    # Construir un diccionario: código interno -> nombre de columna
    idiomas_permitidos = {}
    for col in columnas_apellido:
        # Se espera que el nombre tenga el formato "Apellido_XX"
        code = col.split("_")[1].upper()  # p.ej.: "ES", "EN", "JP", etc.
        idiomas_permitidos[code] = col

    # 2. Detectar el idioma del script utilizando langdetect
    try:
        lang_detected = detect(script_inicial)  # retorna códigos como "es", "en", "ja", etc.
    except Exception:
        lang_detected = "es"  # Si falla la detección, se asume español

    # 3. Mapear el código detectado a nuestro formato interno
    mapping = {
        "es": "ES",
        "en": "EN",
        "ja": "JP",
        "ar": "AR",
        "el": "GR",   # Griego
        "zh-cn": "CH",
        "zh-tw": "CH",
        "zh": "CH"
    }
    codigo_interno = mapping.get(lang_detected.lower(), "ES")  # Por defecto español

    # 4. Si el código interno detectado está entre los permitidos, lo usamos
    if codigo_interno in idiomas_permitidos:
        return idiomas_permitidos[codigo_interno]
    
    # 5. Si no, se utiliza 'Apellido_ES' si existe
    if "ES" in idiomas_permitidos:
        return idiomas_permitidos["ES"]
    
    # 6. Como última opción, se retorna la primera columna disponible
    return columnas_apellido[0]


def generar_diccionario_apellidos(sust_dd: dict, df_personajes, columna_apellido: str) -> dict:
    """
    Genera un diccionario que mapea las mismas claves de sust_dd
    (e.g. 'empleado_1', 'jefe') a los apellidos correctos según la columna dada
    (por ejemplo, 'Apellido_ES').
    """
    dicc_apellidos = {}
    
    for clave, nombre_personaje in sust_dd.items():
        # Filtramos el DataFrame para encontrar la fila que coincida con 'nombre_personaje'
        fila = df_personajes[df_personajes["Personajes"] == nombre_personaje]
        if not fila.empty:
            # Obtenemos el apellido de la columna correspondiente
            apellido = fila[columna_apellido].values[0]
        else:
            # Si no encontramos al personaje, podríamos poner un valor por defecto
            apellido = "Desconocido"
        
        dicc_apellidos[clave] = apellido
    
    return dicc_apellidos


def reemplazar_dialogo(script_inicial: str, dicc_apellidos: dict) -> str:
    """
    Reemplaza en el texto todas las apariciones de las claves en dicc_apellidos
    por su respectivo valor (apellido), excepto en las líneas que empiecen con '['.
    """
    lineas = script_inicial.split("\n")
    nuevas_lineas = []
    
    for linea in lineas:
        # Verificamos si la línea empieza con "["
        if linea.startswith("["):
            # No reemplazamos nada en esta línea
            nuevas_lineas.append(linea)
        else:
            # Reemplazamos cada clave por su apellido correspondiente
            linea_modificada = linea
            for clave, apellido in dicc_apellidos.items():
                linea_modificada = linea_modificada.replace(clave, apellido)
            nuevas_lineas.append(linea_modificada)
    
    # Volvemos a unir el texto
    return "\n".join(nuevas_lineas)
