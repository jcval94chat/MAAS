import os
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,  # Cambia a logging.DEBUG para ver más detalles
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def authenticate_drive_service(credentials_file, scopes=None):
    """
    Autentica y devuelve el servicio de Google Drive.
    
    Args:
        credentials_file (str): Ruta al archivo JSON con las credenciales.
        scopes (list, opcional): Lista de scopes a usar. Por defecto, se usa 'https://www.googleapis.com/auth/drive'.
    
    Returns:
        googleapiclient.discovery.Resource: Servicio autenticado de Google Drive.
    """
    if scopes is None:
        scopes = ['https://www.googleapis.com/auth/drive']
    try:
        creds = service_account.Credentials.from_service_account_file(credentials_file, scopes=scopes)
        service = build('drive', 'v3', credentials=creds)
        logger.info("Servicio de Google Drive autenticado correctamente.")
        return service
    except Exception as e:
        logger.error(f"Error autenticando el servicio de Drive: {e}")
        raise

def upload_and_rename_file_to_drive(file_path, folder_id, new_file_name, credentials_file='service_account.json'):
    """
    Sube un archivo desde 'file_path' a la carpeta de Google Drive identificada por 'folder_id'
    y lo renombra a 'new_file_name' usando la API de Google Drive.
    
    Args:
        file_path (str): Ruta local del archivo.
        folder_id (str): ID de la carpeta de Google Drive donde se subirá el archivo.
        new_file_name (str): Nuevo nombre para el archivo en Google Drive.
        credentials_file (str): Ruta al archivo JSON con las credenciales de la cuenta de servicio.
    
    Returns:
        str: El ID del archivo subido en Google Drive.
    """
    # Verifica que el archivo exista antes de proceder
    if not os.path.isfile(file_path):
        logger.error(f"El archivo {file_path} no existe.")
        raise FileNotFoundError(f"El archivo {file_path} no existe.")
    
    # Autentica y obtiene el servicio de Google Drive
    service = authenticate_drive_service(credentials_file)
    
    # Define la metadata para la creación del archivo en Drive
    file_metadata = {
        'name': new_file_name,
        'parents': [folder_id]
    }
    
    try:
        # Prepara el archivo para su subida
        media = MediaFileUpload(file_path, resumable=True)
        logger.info(f"Subiendo el archivo '{file_path}' a la carpeta '{folder_id}' con el nuevo nombre '{new_file_name}'.")
        response = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = response.get('id')
        logger.info(f"Archivo subido con éxito. ID: {file_id}")
        return file_id
    except Exception as e:
        logger.error(f"Error al subir el archivo: {e}")
        raise
