#!/usr/bin/env python3
"""
transcribir_examen_cli.py

Herramienta de línea de comandos (CLI) independiente del bot de Telegram
para transcribir fotos o PDFs de exámenes a LaTeX utilizando Google Gemini (genai).

Requisitos:
    pip install google-genai python-dotenv httpx

Configuración:
    Crea un archivo .env o define la variable de entorno:
    GEMINI_API_KEY="tu-api-key"
"""

import os
import re
import sys
import time
import argparse
import mimetypes
from dotenv import load_dotenv
import httpx
from google import genai
from google.genai import types

load_dotenv()

URL_BASE = "https://raw.githubusercontent.com/LosDelDGIIM/LosDelDGIIM.github.io/main/subjects"
ARCHIVOS_PLANTILLAS = {
    "Plantilla_Ex.tex": f"{URL_BASE}/plantillas/Ex%C3%A1menes/Plantilla_Ex.tex",
    "preambulo.tex": f"{URL_BASE}/_assets/preambulo.tex"
}

PROMPT_DEFAULT = """Actúas como un transcriptor experto de exámenes universitarios a LaTeX.
Tu tarea es convertir las imágenes o páginas del examen adjunto a un documento LaTeX limpio, completo y compilable.

Utiliza como referencia la siguiente plantilla oficial:
<plantilla>
{texto_plantilla}
</plantilla>

Y ten en cuenta las macros/definiciones del preámbulo:
<preambulo>
{texto_preambulo}
</preambulo>

Instrucciones adicionales:
1. Extrae fielmente todos los enunciados matemáticos, preguntas y metadatos del examen.
2. Mantén exactamente la estructura de \documentclass hasta \end{{document}}.
3. Si algún metadato no aparece en el examen (como fecha, grupo o profesor), indícalo comentado con la sintaxis:
   % \item[NombreMetadato]
4. Responde ÚNICAMENTE con el código LaTeX del examen, sin explicaciones adicionales fuera del código.
"""


def descargar_plantillas(directorio: str) -> tuple[str, str]:
    """Descarga o carga las plantillas del repositorio."""
    os.makedirs(directorio, exist_ok=True)
    plantilla_path = os.path.join(directorio, "Plantilla_Ex.tex")
    preambulo_path = os.path.join(directorio, "preambulo.tex")

    for nombre, url in ARCHIVOS_PLANTILLAS.items():
        destino = os.path.join(directorio, nombre)
        if not os.path.exists(destino):
            print(f"[*] Descargando {nombre} desde GitHub...")
            try:
                r = httpx.get(url, timeout=15.0)
                r.raise_for_status()
                with open(destino, "w", encoding="utf-8") as f:
                    f.write(r.text)
            except Exception as e:
                print(f"[!] Advertencia al descargar {nombre}: {e}")

    texto_plantilla = ""
    if os.path.exists(plantilla_path):
        with open(plantilla_path, "r", encoding="utf-8") as f:
            texto_plantilla = f.read()

    texto_preambulo = ""
    if os.path.exists(preambulo_path):
        with open(preambulo_path, "r", encoding="utf-8") as f:
            contenido = f.read()
            partes = contenido.split("% IA")
            texto_preambulo = partes[1].strip() if len(partes) > 1 else contenido

    return texto_plantilla, texto_preambulo


def construir_instrucciones(plantillas_dir: str, prompt_custom_path: str = None) -> str:
    """Construye las instrucciones del sistema para Gemini."""
    texto_plantilla, texto_preambulo = descargar_plantillas(plantillas_dir)

    if prompt_custom_path and os.path.exists(prompt_custom_path):
        with open(prompt_custom_path, "r", encoding="utf-8") as f:
            plantilla_prompt = f.read()
    else:
        plantilla_prompt = PROMPT_DEFAULT

    return plantilla_prompt.format(
        texto_plantilla=texto_plantilla,
        texto_preambulo=texto_preambulo
    )


def procesar_archivos(rutas_archivos: list[str]) -> list[types.Part]:
    """Convierte los archivos de entrada en objetos types.Part para Gemini."""
    contenidos = []
    for ruta in rutas_archivos:
        if not os.path.exists(ruta):
            print(f"[!] Error: El archivo '{ruta}' no existe. Omitiendo.")
            continue

        mime_type, _ = mimetypes.guess_type(ruta)
        if not mime_type:
            if ruta.lower().endswith(".pdf"):
                mime_type = "application/pdf"
            elif ruta.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                mime_type = "image/jpeg"
            else:
                mime_type = "application/octet-stream"

        print(f"[*] Cargando: {os.path.basename(ruta)} ({mime_type})")
        with open(ruta, "rb") as f:
            contenidos.append(types.Part.from_bytes(data=f.read(), mime_type=mime_type))

    return contenidos


def transcribir_examen(
    archivos: list[str],
    salida_tex: str = "Examen_TranscritoIA.tex",
    modelo: str = "gemini-2.5-flash",
    plantillas_dir: str = "./plantillas_ia",
    prompt_path: str = None,
    pedir_metadatos: bool = True
):
    """Ejecuta la transcripción llamando a la API de Gemini."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[!] ERROR: No se ha encontrado la variable de entorno GEMINI_API_KEY.")
        print("    Asegúrate de definirla en el archivo .env o en el sistema:")
        print("    export GEMINI_API_KEY='tu_clave_aqui'")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    partes_archivos = procesar_archivos(archivos)
    if not partes_archivos:
        print("[!] No se cargaron archivos válidos para procesar.")
        sys.exit(1)

    instrucciones = construir_instrucciones(plantillas_dir, prompt_path)

    contenidos = list(partes_archivos)
    contenidos.append("Transcribe todo este examen en orden, respetando la plantilla.")

    print(f"\n[*] Enviando petición a Gemini ({modelo})...")
    max_intentos = 3
    response = None

    for intento in range(max_intentos):
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=contenidos,
                config=types.GenerateContentConfig(
                    system_instruction=instrucciones,
                    temperature=0.0
                )
            )
            break
        except Exception as e:
            error_str = str(e)
            if "503" in error_str or "UNAVAILABLE" in error_str:
                if intento < max_intentos - 1:
                    print(f"[!] Servidores saturados (503). Reintentando en 20s (intento {intento+1}/{max_intentos})...")
                    time.sleep(20)
                else:
                    print("[!] Se agotaron los reintentos debido a saturación del servidor.")
                    sys.exit(1)
            else:
                print(f"[!] Error en la llamada a Gemini: {e}")
                sys.exit(1)

    if not response or not response.text:
        print("[!] No se obtuvo respuesta de la IA.")
        sys.exit(1)

    # Filtrar solo el bloque LaTeX
    match = re.search(r"(\documentclass.*?\end\{document\})", response.text, re.DOTALL)
    if not match:
        print("[!] La IA no devolvió una estructura LaTeX completa (\documentclass ... \end{document}).")
        print("Respuesta recibida:")
        print(response.text[:500] + "...")
        sys.exit(1)

    codigo_limpio = match.group(1)

    # Comprobar si hay metadatos faltantes comentados (% \item[Clave])
    metadatos_faltantes = re.findall(r"%\s*\item\[(.*?)\]", codigo_limpio)
    if metadatos_faltantes and pedir_metadatos:
        print("\n" + "="*60)
        print("💡 Se han detectado metadatos incompletos en el examen.")
        print("Introduce los valores que conozcas (deja vacío para omitir):")
        print("="*60)

        for metadato in metadatos_faltantes:
            valor = input(f"• {metadato}: ").strip()
            if valor:
                if not valor.endswith("."):
                    valor += "."
                patron = re.compile(r"%\s*\item\[" + re.escape(metadato) + r"\].*")
                codigo_limpio = patron.sub(
                    lambda m, cl=metadato, vl=valor: f"\item[{cl}] {vl}",
                    codigo_limpio
                )

    # Guardar en archivo
    with open(salida_tex, "w", encoding="utf-8") as f:
        f.write(codigo_limpio)

    print(f"\n[✓] ¡Éxito! Archivo LaTeX generado correctamente en: {salida_tex}")


def main():
    parser = argparse.ArgumentParser(
        description="Transcriptor de exámenes a LaTeX usando Gemini AI (modo CLI independiente)"
    )
    parser.add_argument(
        "archivos",
        nargs="+",
        help="Rutas a las fotos (JPG, PNG, etc.) o archivo(s) PDF del examen"
    )
    parser.add_argument(
        "-o", "--output",
        default="Examen_TranscritoIA.tex",
        help="Ruta o nombre del archivo .tex de salida (defecto: Examen_TranscritoIA.tex)"
    )
    parser.add_argument(
        "-m", "--model",
        default="gemini-2.5-flash",
        help="Modelo de Gemini a utilizar (defecto: gemini-2.5-flash)"
    )
    parser.add_argument(
        "--plantillas-dir",
        default="./plantillas_ia",
        help="Carpeta donde se almacenan o descargan las plantillas .tex"
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="Ruta opcional a un archivo prompt_ocr.txt personalizado"
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="No solicitar metadatos faltantes de forma interactiva por consola"
    )

    args = parser.parse_args()

    transcribir_examen(
        archivos=args.archivos,
        salida_tex=args.output,
        modelo=args.model,
        plantillas_dir=args.plantillas_dir,
        prompt_path=args.prompt,
        pedir_metadatos=not args.no_interactive
    )


if __name__ == "__main__":
    main()
