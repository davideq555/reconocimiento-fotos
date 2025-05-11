# Sistema de Reconocimiento de Números en Imágenes de Carreras

Este proyecto implementa un sistema de reconocimiento de números en imágenes de participantes de carreras utilizando múltiples métodos de procesamiento:

- EasyOCR (CPU)
- EasyOCR con GPU
- Ollama con el modelo llama3.2-vision
- OpenAI GPT-4.1

El sistema analiza imágenes de participantes, reconoce los números visibles en el primer plano y renombra las imágenes con los números encontrados en el formato `n123_n456.jpg`.

## Características

- Procesamiento de imágenes en lote
- Múltiples métodos de procesamiento para comparación de rendimiento
- Filtros para ignorar números en segundo plano o desenfocados
- Comparación de tiempos de procesamiento entre métodos
- Configuración de API key de OpenAI a través de archivo .env

## Requisitos

- Python 3.8+
- GPU compatible (para procesamiento con GPU)
- OpenAI API key (para uso de GPT-4.1)

## Instalación

1. Crear y activar un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
```

2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar la API key de OpenAI:
   - Crear un archivo `.env` en la raíz del proyecto
   - Agregar la siguiente línea con tu API key:
   ```
   OPENAI_API_KEY=tu_api_key_aqui
   ```

## Estructura de Carpetas

```
media/
├── maraton-test/        # Carpeta con las imágenes originales
├── procesadas-cpu/      # Resultados del procesamiento con CPU
├── procesadas-gpu/      # Resultados del procesamiento con GPU
├── procesadas-ollama/   # Resultados del procesamiento con Ollama
└── procesadas-openai/   # Resultados del procesamiento con OpenAI
```

## Uso

1. Colocar las imágenes a procesar en la carpeta `media/maraton-test`
2. Ejecutar el script:
```bash
python renombrar_fotos.py
```

El script procesará las imágenes usando todos los métodos disponibles y mostrará un resumen comparativo de los tiempos de procesamiento.


## Funcionalidad

- Reconoce números en las imágenes usando EasyOCR, Ollama y OpenAI
- Renombra los archivos con el patrón `n{numero_encontrado}_n{Siguiente_numero_encontrado}`
- Maneja múltiples números en una misma imagen
- Mantiene la extensión original del archivo
