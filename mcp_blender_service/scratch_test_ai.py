# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.error
import sys
import io

# Forzar codificación UTF-8 en flujos estándar de consola para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen"

def test_question(pregunta):
    print("=" * 80)
    print(f"Pregunta a validar: '{pregunta}'")
    print("-" * 80)
    
    # Prompt ultra optimizado y estructurado para modelos locales pequeños (3B)
    prompt_moby = (
        "INSTRUCCIONES DE ROL:\n"
        "- Eres Moby, la ballena mascota oficial de Docker. Tu cerebro está lleno de contenedores y barcos.\n"
        "- Responde de forma muy breve (máximo 2 oraciones) y súper alegre.\n"
        "- REGLA DE SEGURIDAD CRÍTICA: Tu conocimiento está estrictamente limitado a Docker, contenedores, Kubernetes, DevOps y virtualización. "
        "Si la pregunta del usuario es sobre CUALQUIER otro tema (como cocina, recetas, deportes, chistes, etc.), "
        "debes declinar responder diciendo exactamente de forma muy tierna: '¡Ups! Como la ballena mascota de Docker, "
        "mi cerebro solo tiene espacio para contenedores y barcos. ¡Pregúntame sobre Docker! 🐳💙'. No respondas nada del tema fuera de foco.\n\n"
        f"PREGUNTA DEL USUARIO: {pregunta}"
    )
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt_moby,
        "stream": False
    }
    
    headers = {"Content-Type": "application/json"}
    
    req = urllib.request.Request(
        OLLAMA_API_URL, 
        data=json.dumps(payload).encode('utf-8'), 
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read().decode('utf-8')
            res_json = json.loads(res_data)
            respuesta = res_json.get("response", "")
            print("Respuesta de Moby (Ollama):")
            print(f"-> \"{respuesta}\"")
            print("=" * 80)
            return respuesta
    except urllib.error.URLError as e:
        print(f"[ERROR] No se pudo conectar a Ollama: {str(e)}", file=sys.stderr)
        return None

def main():
    print("Iniciando validación de respuestas de Moby AI (Ollama)...")
    
    # 1. Caso de prueba 1: Pregunta legítima de Docker
    pregunta_docker = "¿Qué es una imagen de Docker y para qué sirve?"
    test_question(pregunta_docker)
    
    # 2. Caso de prueba 2: Pregunta fuera de tema (Filtro Antidesvíos)
    pregunta_offtopic = "¿Cómo puedo preparar una pizza napolitana en casa?"
    test_question(pregunta_offtopic)

if __name__ == "__main__":
    main()
