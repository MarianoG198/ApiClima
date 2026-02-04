import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from twilio.rest import Client

# --- CONFIGURACIÓN DE ENTORNO ---
BASE_DIR = Path(__file__).parent.absolute()
load_dotenv(dotenv_path=BASE_DIR / ".env")

def validar_configuracion():
    """Verifica que todas las variables de entorno necesarias estén presentes."""
    variables = [
        "WEATHER_API_KEY", "CIUDAD", "TWILIO_ACCOUNT_SID", 
        "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_NUMBER", "MI_TELEFONO"
    ]
    faltantes = [v for v in variables if not os.getenv(v)]
    if faltantes:
        raise EnvironmentError(f"Faltan variables en el .env: {', '.join(faltantes)}")

# --- MÓDULO DE CLIMA ---
def obtener_datos_clima(api_key, ciudad):
    """Consulta la API de WeatherAPI y devuelve los datos principales."""
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={ciudad}&lang=es"
    respuesta = requests.get(url)
    respuesta.raise_for_status() # Lanza un error si la API falla (ej. 401, 404)
    return respuesta.json()

# --- MÓDULO DE MENSAJERÍA ---
def enviar_notificacion_whatsapp(mensaje):
    """Gestiona el envío del mensaje a través de Twilio."""
    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    
    response = client.messages.create(
        from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
        body=mensaje,
        to=f"whatsapp:{os.getenv('MI_TELEFONO')}"
    )
    return response.sid

# --- LÓGICA PRINCIPAL ---
def main():
    try:
        validar_configuracion()
        
        api_key = os.getenv("WEATHER_API_KEY")
        ciudad = os.getenv("CIUDAD")
        
        # 1. Obtener clima
        datos = obtener_datos_clima(api_key, ciudad)
        temp = datos['current']['temp_c']
        condicion = datos['current']['condition']['text']
        
        # 2. Construir mensaje basado en lógica de entrenamiento
        recomendacion = "🏃 ¡Momento ideal para correr!" if temp < 28 and "lluvia" not in condicion.lower() else "🏠 Hoy se entrena en casa."
        mensaje_final = f"Hola, Reporte actual {ciudad}: {temp}°C, {condicion}. {recomendacion}"
        
        # 3. Enviar notificación
        print(f"Procesando: {mensaje_final}")
        sid = enviar_notificacion_whatsapp(mensaje_final)
        print(f"✅ Notificación enviada (ID: {sid})")

    except Exception as e:
        print(f"❌ Error en el sistema: {e}")

if __name__ == "__main__":
    main()