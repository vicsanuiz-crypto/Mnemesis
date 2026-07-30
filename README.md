# Mnemesis

Agente de IA que controla un teléfono Android real para completar tareas en lenguaje natural ("abre WhatsApp y manda un mensaje a Juan diciendo que llego tarde").

A diferencia de los agentes basados en capturas de pantalla, Mnemesis **no envía imágenes a ningún sitio**: usa el árbol de accesibilidad de Android (texto, ids de vista, límites de cada elemento) como única fuente de percepción. Eso lo hace más barato en tokens, más rápido y más fiable para pulsar el botón correcto, a costa de necesitar una app instalada en el propio dispositivo.

## Arquitectura

```
┌─────────────────────────┐         adb forward          ┌───────────────────────────┐
│   Móvil Android          │  tcp:8734 ────────────────►  │  Máquina de control        │
│                          │                               │                            │
│  MnemesisAccessibility-  │   GET /ui  → árbol JSON       │  agent/ (Node + TS)        │
│  Service (Kotlin)        │◄──────────────────────────────│  MnemesisAgent:            │
│   - lee el árbol de      │   POST /action → tap/swipe/   │   percibe → decide (Gemini) │
│     accesibilidad        │   type_text/back/home/...     │   → actúa → repite          │
│   - ejecuta gestos       │                               │                            │
│   - servidor local       │                               │                            │
│     (NanoHTTPD, solo     │                               │                            │
│     127.0.0.1)           │                               │                            │
└─────────────────────────┘                               └───────────────────────────┘
```

- **`android/`** — app Android (Kotlin) con un `AccessibilityService` que expone un servidor HTTP local (puerto `8734`, solo `127.0.0.1`) con dos rutas:
  - `GET /ui` — volcado del árbol de accesibilidad actual (paquete activo + nodos con texto/id/límites/rol).
  - `POST /action` — ejecuta una acción: `tap`, `long_press`, `swipe`, `click_node`, `type_text`, `back`, `home`, `recents`.
- **`agent/`** — CLI en Node/TypeScript que recibe una tarea en lenguaje natural, y en bucle: pide el árbol de UI, se lo pasa a **Google Gemini** junto con la tarea y el historial, ejecuta la acción que decida el modelo (usando function calling), y repite hasta que el propio modelo llama a `finish`.

El servidor solo escucha en loopback (`127.0.0.1`) para que nadie en la misma red pueda controlarlo: el único camino de entrada es `adb forward`, que requiere depuración USB activada y el cable/ADB-over-WiFi ya autorizado en el propio dispositivo.

## Requisitos

- Un móvil Android (API 26+) con **depuración USB** activada y ADB instalado en la máquina de control.
- Android Studio (recomendado) o Gradle 8.x para compilar la app.
- Node.js 18+ y una `GEMINI_API_KEY` (gratis desde [Google AI Studio](https://aistudio.google.com) → "Get API key") para el agente.

## Puesta en marcha

### 1. Instalar la app en el móvil

Abre la carpeta `android/` en Android Studio y ejecuta la app en tu dispositivo (o `./gradlew installDebug` si tienes Gradle configurado). Después:

1. Abre **Mnemesis** en el móvil.
2. Pulsa **"Activar accesibilidad"** → actívalo en Ajustes → Accesibilidad → Mnemesis.
3. Vuelve a la app: debería indicar que el servicio y el servidor están activos.

### 2. Exponer el puerto de control

Con el móvil conectado por USB (o ADB sobre WiFi ya emparejado):

```bash
adb forward tcp:8734 tcp:8734
```

### 3. Ejecutar el agente

```bash
cd agent
cp .env.example .env   # pega tu GEMINI_API_KEY en el archivo .env
npm install
npm start -- "abre los ajustes y dime qué versión de Android tengo"
```

En Windows, `cp .env.example .env` es `copy .env.example .env`.

El agente imprimirá cada paso que decide dar (herramienta + argumentos) y termina cuando el modelo llama a `finish`, indicando si la tarea se completó.

Si al lanzarlo aparece un error de tipo "model not found", edita `agent/.env` y cambia `MNEMESIS_MODEL` por el nombre de modelo que te muestre AI Studio (por ejemplo `gemini-3.5-flash`).

## Seguridad y límites

- Este proyecto ejecuta acciones reales en un dispositivo real: solo debe usarse en un móvil propio (o con permiso explícito del dueño) y con tareas de las que te fíes.
- No hay confirmación humana entre pasos: revisa la tarea antes de lanzarla, especialmente para acciones irreversibles (borrar, pagar, enviar mensajes).
- El agente se detiene solo tras `MNEMESIS_MAX_STEPS` pasos (25 por defecto) como salvaguarda ante bucles.
- El servidor de control no tiene autenticación porque solo escucha en loopback; no lo expongas nunca a `0.0.0.0` sin añadir autenticación antes.
