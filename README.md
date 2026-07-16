# 🤖 Bot de Telegram - LosDelDGIIM

Este es el repositorio oficial del bot de Telegram de la comunidad de **LosDelDGIIM** (Doble Grado en Ingeniería Informática y Matemáticas de la Universidad de Granada). 

El bot (`@Colaboracion_LosDelDGIIM_Bot`) actúa como el puente principal entre los estudiantes y la plataforma, automatizando la recepción de material académico y coordinando el proceso de digitalización.

---

## 🚀 Características Principales

*   **📤 Envío de Material:** Permite a los alumnos enviar apuntes, resúmenes y exámenes corregidos directamente al equipo de administración de forma organizada.
*   **✍️ Coordinación de Digitalización:** Facilita la asignación de tareas a voluntarios para transcribir apuntes en sucio a código limpio en LaTeX.
*   **💬 Canal de Soporte:** Centraliza las dudas, sugerencias y reportes de errores de la web o de los apuntes para una respuesta rápida.
*   **⚙️ Flujo Automatizado:** Agiliza la moderación interna antes de que el contenido se suba al repositorio web principal.

---

## 🛠️ Tecnologías Utilizadas

*   **Lenguaje:** Python 3.10+
*   **Librería Principal:** `python-telegram-bot`

---

## 💻 Instalación y Configuración Local

Si quieres contribuir al desarrollo del bot o probarlo en tu propio entorno, sigue estos pasos:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/LosDelDGIIM/Bot.git](https://github.com/LosDelDGIIM/Bot.git)
cd Bot
```
### 2. Configurar el entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows usa: venv\Scripts\activate
pip install -r requirements.txt
```
### 3. Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto y añade las credenciales necesarias (puedes guiarte con `.env.example`).
### 4. Ejecutar el Bot
```bash
python3 bot.py
```
