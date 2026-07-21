# Conectores — APIs y servicios

⚠️ **Aquí NUNCA van valores de claves.** Solo qué se usa y dónde vive su clave.

## Modelos de IA (medido, no supuesto — jul 2026)

Comparados con el **prompt real** del escáner de AI-Trader (no benchmarks abstractos),
con `compare-free-models.mjs`. Criterio: JSON válido + seguimiento de reglas (3 casos
trampa) + latencia + aguantar el prompt grande.

| Modelo | Veredicto |
|---|---|
| **`gemini-2.5-flash`** | ✅ **El recomendado.** 5/5 en reglas, 6.6s con el escaneo completo |
| `gemini-2.5-flash-lite` | ✅ 5/5, 3.6s (el doble de rápido). Es el **fallback** |
| Groq `llama-3.3-70b` | ⚠️ 5/5 y el más rápido (1.9s) **pero su capa gratuita rechaza el escaneo completo** (~8K tokens: `Request too large`). Solo prompts pequeños |
| `gemini-3.5-flash` | 💳 De pago ($1.50/$9 por M). Funciona, saldo activo. Capacidad intermitente |

**MUERTOS** (verificados, eliminados de los selectores): `gemini-2.5-pro`,
`llama-4-maverick`, `deepseek-r1-distill-llama-70b`, `mixtral-8x7b-32768`,
`openrouter llama-3.3-70b-instruct:free`.

**Hallazgo clave:** en razonamiento los tres buenos **empataron**. Para estas tareas
**no hace falta un modelo más listo** — el edge está en las reglas, no en el LLM.
Pagar 10× no mejora resultados mientras se valida en papel.

**Gemini 3.x:** retiró los parámetros de muestreo → hay que **omitir `temperature`**.
En cambio `thinkingBudget: 0` sí se respeta y es clave: 44 tokens vs 318 → **~12×
más barato** (los tokens de "pensamiento" se facturan a precio de salida).

Claves en el `.env` de AI-Trader: `GEMINI_API`, `GROQ_API_KEY`, `OPENROUTER_API_KEY`,
`ANTHROPIC_API_KEY`.

## Brókers y datos de mercado

- **Alpaca** (paper) — acciones US + cripto spot. Datos diarios/intradía. Claves en
  `.env` de AI-Trader. **Coste de mantener: 0 en largos al contado**; margen ~6.25%
  anual y cortos HTB sí pagan.
- **Binance Futuros** — infraestructura montada pero **SIN claves configuradas**:
  nunca ha operado. Se conserva como vía futura hacia cortos/apalancamiento que
  Alpaca no permite en cripto.
- **Yahoo Finance** — barras históricas para indicadores.
- **Polymarket** (gamma-api) — mercados de predicción. El paper-betting se **retiró**
  (ROI −60%): el modelo derivaba su probabilidad de los precios del propio mercado
  que intentaba batir → circular. El motor matemático (`poly-model.js`) queda como
  herramienta de análisis manual.

## Otros servicios

- **Railway** — hosting 24/7 de AI-Trader. Deploy automático al pushear a `main`.
- **Telegram** — bot de control y avisos de AI-Trader (`/status`, `/edge`, `/robustez`,
  `/digest`, `/resumen`…). Un token solo admite UN poller: por eso local va con
  `TG_BOT_DISABLED=1`.
- **Netlify** — hosting de la PWA LOMLOE (deploy arrastrando la carpeta).
- **Firebase/Firestore** — sync y login Google de LOMLOE, con whitelist.
- **GitHub** — `vicsanuiz-crypto/ai-trader`, `vicsanuiz-crypto/Mnemesis`.
  ⚠️ `gh` CLI **no está instalado**; usar `git` directamente.

## Anthropic — agentes de finanzas (may 2026)

Existen 10 agentes oficiales para finanzas (pitchbooks, KYC, revisión de earnings,
cierre de mes…), **pero son para trabajo de oficina: ninguno genera señales de
trading ni opera**. No sirven para AI-Trader. Anotado para no volver a mirarlo.

Relacionado: [[projects]] · [[skills]]
