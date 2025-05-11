import os
from dotenv import load_dotenv
import easyocr
from PIL import Image
import re
import time
import ollama
import requests
import base64
import json
import openai

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar la API key de OpenAI desde la variable de entorno
openai.api_key = os.getenv('OPENAI_API_KEY')

if not openai.api_key:
    print("Error: No se ha configurado la API key de OpenAI")
    print("Por favor, configura la variable OPENAI_API_KEY en el archivo .env")
    exit(1)

# Configurar la API key de OpenAI desde la variable de entorno
openai.api_key = os.getenv('OPENAI_API_KEY')

if not openai.api_key:
    print("Error: No se ha configurado la API key de OpenAI")
    print("Por favor, configura la variable de entorno OPENAI_API_KEY")
    exit(1)

def extraer_numeros(texto):
    """Extrae todos los números del texto y los devuelve como lista"""
    return [int(num) for num in re.findall(r'\d+', texto)]

def encode_image_to_base64(image_path):
    """Convert an image file to a base64 encoded string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def procesar_imagenes(ruta_origen, ruta_destino, con_gpu=False):
    """Procesa imágenes usando EasyOCR"""
    # Inicializar el lector de EasyOCR
    reader = easyocr.Reader(['en'], gpu=con_gpu)
    
    # Verificar y crear la carpeta de destino si no existe
    if not os.path.exists(ruta_destino):
        os.makedirs(ruta_destino)
    
    # Obtener todas las imágenes en el directorio origen
    imagenes = [f for f in os.listdir(ruta_origen) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    for imagen in imagenes:
        ruta_origen_imagen = os.path.join(ruta_origen, imagen)
        try:
            # Leer la imagen
            resultados = reader.readtext(ruta_origen_imagen)
            
            # Extraer todos los números encontrados
            numeros_encontrados = []
            for resultado in resultados:
                texto = resultado[1]
                numeros = extraer_numeros(texto)
                numeros_encontrados.extend(numeros)
            
            # Si se encontraron números
            if numeros_encontrados:
                # Ordenar los números y crear el nuevo nombre
                numeros_ordenados = sorted(set(numeros_encontrados))
                nuevo_nombre = '_'.join([f'n{num}' for num in numeros_ordenados])
                nuevo_nombre += os.path.splitext(imagen)[1]
                
                # Crear la nueva ruta en la carpeta destino
                nueva_ruta = os.path.join(ruta_destino, nuevo_nombre)
                
                # Copiar la imagen con el nuevo nombre
                import shutil
                shutil.copy2(ruta_origen_imagen, nueva_ruta)
                print(f"Creada copia: {imagen} -> {nuevo_nombre}")
            else:
                print(f"No se encontraron números en {imagen}")
                
        except Exception as e:
            print(f"Error procesando {imagen}: {str(e)}")

def procesar_con_ollama(ruta_origen, ruta_destino):
    """Procesa imágenes usando Ollama con el modelo llama3.2-vision"""
    # Verificar y crear la carpeta de destino si no existe
    if not os.path.exists(ruta_destino):
        os.makedirs(ruta_destino)
    
    # Obtener todas las imágenes en el directorio origen
    imagenes = [f for f in os.listdir(ruta_origen) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    for imagen in imagenes:
        ruta_origen_imagen = os.path.join(ruta_origen, imagen)
        try:
            image_base64 = encode_image_to_base64(ruta_origen_imagen)

            # Preparar el prompt para el modelo
            prompt = """Analiza esta imagen y encuentra todos los números visibles del primer plano. 
            No consideres números que estén en el segundo plano, numeros que estan desenfocados.
            Responde solo con los números encontrados separados por comas."""
            
            # Hacer la solicitud a Ollama
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2-vision",
                    "prompt": prompt,
                    "images": [image_base64],
                    "options": {
                        "temperature": 0.1
                    }
                }
            )
            
            # Procesar la respuesta
            if response.status_code == 200:
                try:
                    # Dividir la respuesta en múltiples mensajes
                    mensajes = response.text.split('\n')
                    texto_completo = ""
                    
                    # Procesar cada mensaje
                    for mensaje in mensajes:
                        if mensaje.strip():
                            try:
                                # Intentar decodificar cada mensaje por separado
                                resultado = json.loads(mensaje)
                                if "response" in resultado:
                                    texto_completo += resultado["response"]
                            except json.JSONDecodeError:
                                continue
                    
                    # Extraer los números del texto completo
                    if texto_completo:
                        numeros_encontrados = extraer_numeros(texto_completo)
                        
                        if numeros_encontrados:
                            # Ordenar los números y crear el nuevo nombre
                            numeros_ordenados = sorted(set(numeros_encontrados))
                            nuevo_nombre = '_'.join([f'n{num}' for num in numeros_ordenados])
                            nuevo_nombre += os.path.splitext(imagen)[1]
                            
                            # Crear la nueva ruta en la carpeta destino
                            nueva_ruta = os.path.join(ruta_destino, nuevo_nombre)
                            
                            # Copiar la imagen con el nuevo nombre
                            import shutil
                            shutil.copy2(ruta_origen_imagen, nueva_ruta)
                            print(f"\nCreada copia: {imagen} -> {nuevo_nombre}")
                        else:
                            print(f"No se encontraron números en {imagen}")
                    else:
                        print(f"No se recibió texto válido de Ollama")
                except Exception as e:
                    print(f"Error procesando la respuesta: {str(e)}")
        except Exception as e:
            print(f"Error procesando {imagen}: {str(e)}")

def procesar_con_openai(ruta_origen, ruta_destino):
    """Procesa imágenes usando la API de OpenAI con el modelo más básico"""
    # Verificar y crear la carpeta de destino si no existe
    if not os.path.exists(ruta_destino):
        os.makedirs(ruta_destino)
    
    # Obtener todas las imágenes en el directorio origen
    imagenes = [f for f in os.listdir(ruta_origen) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    for imagen in imagenes:
        ruta_origen_imagen = os.path.join(ruta_origen, imagen)
        try:
            # Codificar la imagen en base64
            base64_image = encode_image_to_base64(ruta_origen_imagen)
            
            # Preparar el prompt para el modelo
            prompt = """Analiza esta imagen y encuentra todos los números visibles del primer plano. 
            No consideres números que estén en el segundo plano, numeros que estan desenfocados.
            Responde solo con los números encontrados separados por comas."""
            
            # Hacer la solicitud a OpenAI
            response = openai.responses.create(
                model="gpt-4.1",
                input=[
                    {
                        "role": "user",
                        "content": [
                            { "type": "input_text", "text": prompt },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        ],
                    }
                ],
            )
            
            # Procesar la respuesta
            if response and hasattr(response, 'output_text'):
                # Extraer los números del texto
                numeros_encontrados = extraer_numeros(response.output_text)
                
                if numeros_encontrados:
                    # Ordenar los números y crear el nuevo nombre
                    numeros_ordenados = sorted(set(numeros_encontrados))
                    nuevo_nombre = '_'.join([f'n{num}' for num in numeros_ordenados])
                    nuevo_nombre += os.path.splitext(imagen)[1]
                    
                    # Crear la nueva ruta en la carpeta destino
                    nueva_ruta = os.path.join(ruta_destino, nuevo_nombre)
                    
                    # Copiar la imagen con el nuevo nombre
                    import shutil
                    shutil.copy2(ruta_origen_imagen, nueva_ruta)
                    print(f"\nCreada copia: {imagen} -> {nuevo_nombre}")
                else:
                    print(f"No se encontraron números en {imagen}")
        except Exception as e:
            print(f"Error procesando {imagen}: {str(e)}")
                

if __name__ == "__main__":
    ruta_origen = "media/maraton-test"
    ruta_destino_cpu = "media/procesadas-cpu"
    ruta_destino_gpu = "media/procesadas-gpu"
    ruta_destino_ollama = "media/procesadas-ollama"
    ruta_destino_openai = "media/procesadas-openai"
    
    # Procesar con CPU
    print("\n=== Procesando con CPU ===")
    inicio_cpu = time.time()
    procesar_imagenes(ruta_origen, ruta_destino_cpu, con_gpu=False)
    fin_cpu = time.time()
    tiempo_cpu = fin_cpu - inicio_cpu
    print(f"\nProceso completado con CPU en {tiempo_cpu:.2f} segundos")
    
    # # Procesar con GPU
    # print("\n=== Procesando con GPU ===")
    # inicio_gpu = time.time()
    # procesar_imagenes(ruta_origen, ruta_destino_gpu, con_gpu=True)
    # fin_gpu = time.time()
    # tiempo_gpu = fin_gpu - inicio_gpu
    # print(f"\nProceso completado con GPU en {tiempo_gpu:.2f} segundos")
    
    # Procesar con Ollama
    print("\n=== Procesando con Ollama ===")
    inicio_ollama = time.time()
    procesar_con_ollama(ruta_origen, ruta_destino_ollama)
    fin_ollama = time.time()
    tiempo_ollama = fin_ollama - inicio_ollama
    print(f"\nProceso completado con Ollama en {tiempo_ollama:.2f} segundos")
    
    # Procesar con OpenAI
    print("\n=== Procesando con OpenAI ===")
    inicio_openai = time.time()
    procesar_con_openai(ruta_origen, ruta_destino_openai)
    fin_openai = time.time()
    tiempo_openai = fin_openai - inicio_openai
    print(f"\nProceso completado con OpenAI en {tiempo_openai:.2f} segundos")
    
    # Mostrar comparación
    print("\n=== Resumen de tiempos ===")
    print(f"Tiempo CPU: {tiempo_cpu:.2f} segundos")
    # print(f"Tiempo GPU: {tiempo_gpu:.2f} segundos")
    print(f"Tiempo Ollama: {tiempo_ollama:.2f} segundos")
    print(f"Tiempo OpenAI: {tiempo_openai:.2f} segundos")
    # print(f"Mejora de rendimiento CPU vs GPU: {((tiempo_cpu - tiempo_gpu) / tiempo_cpu * 100):.1f}%")
    print(f"Mejora de rendimiento CPU vs Ollama: {((tiempo_cpu - tiempo_ollama) / tiempo_cpu * 100):.1f}%")
    print(f"Mejora de rendimiento CPU vs OpenAI: {((tiempo_cpu - tiempo_openai) / tiempo_cpu * 100):.1f}%")

