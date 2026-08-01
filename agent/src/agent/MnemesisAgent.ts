import {
  type Content,
  type FunctionDeclaration,
  FunctionCallingMode,
  type GenerativeModel,
  type GoogleGenerativeAI,
  SchemaType,
} from "@google/generative-ai";
import type { DeviceClient } from "../device/DeviceClient.js";
import { SYSTEM_PROMPT, describeSnapshot } from "./prompts.js";

const FUNCTION_DECLARATIONS: FunctionDeclaration[] = [
  {
    name: "tap",
    description: "Toca la pantalla en unas coordenadas de píxel absolutas.",
    parameters: {
      type: SchemaType.OBJECT,
      properties: {
        x: { type: SchemaType.NUMBER },
        y: { type: SchemaType.NUMBER },
      },
      required: ["x", "y"],
    },
  },
  {
    name: "swipe",
    description:
      "Desliza el dedo entre dos puntos de la pantalla (scroll, deslizar para cerrar, etc.).",
    parameters: {
      type: SchemaType.OBJECT,
      properties: {
        x1: { type: SchemaType.NUMBER },
        y1: { type: SchemaType.NUMBER },
        x2: { type: SchemaType.NUMBER },
        y2: { type: SchemaType.NUMBER },
        durationMs: {
          type: SchemaType.NUMBER,
          description: "Duración del gesto en ms (por defecto 300).",
        },
      },
      required: ["x1", "y1", "x2", "y2"],
    },
  },
  {
    name: "open_app",
    description:
      "Abre una app por su nombre visible (p. ej. 'calculadora', 'whatsapp', 'ajustes'). " +
      "Es la forma preferida de abrir cualquier app: no hace falta buscar su icono en el escritorio.",
    parameters: {
      type: SchemaType.OBJECT,
      properties: {
        query: {
          type: SchemaType.STRING,
          description: "Nombre de la app tal como aparece en el teléfono, o su package name.",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "click_node",
    description:
      "Pulsa el nodo de accesibilidad con el id indicado (preferido frente a tap cuando el nodo está en la lista).",
    parameters: {
      type: SchemaType.OBJECT,
      properties: { nodeId: { type: SchemaType.NUMBER } },
      required: ["nodeId"],
    },
  },
  {
    name: "type_text",
    description: "Escribe texto en el nodo editable con el id indicado.",
    parameters: {
      type: SchemaType.OBJECT,
      properties: {
        nodeId: { type: SchemaType.NUMBER },
        text: { type: SchemaType.STRING },
      },
      required: ["nodeId", "text"],
    },
  },
  {
    name: "back",
    description: "Pulsa el botón/gesto de retroceso del sistema.",
  },
  {
    name: "home",
    description: "Va a la pantalla de inicio.",
  },
  {
    name: "recents",
    description: "Abre la vista de apps recientes.",
  },
  {
    name: "wait",
    description:
      "Espera un momento (p. ej. mientras carga una app) antes de volver a mirar la pantalla.",
    parameters: {
      type: SchemaType.OBJECT,
      properties: { ms: { type: SchemaType.NUMBER } },
      required: ["ms"],
    },
  },
  {
    name: "finish",
    description: "Termina la tarea: indica si se completó con éxito y un resumen breve.",
    parameters: {
      type: SchemaType.OBJECT,
      properties: {
        success: { type: SchemaType.BOOLEAN },
        summary: { type: SchemaType.STRING },
      },
      required: ["success", "summary"],
    },
  },
];

export interface AgentRunResult {
  success: boolean;
  summary: string;
  steps: number;
}

export class MnemesisAgent {
  private readonly model: GenerativeModel;

  constructor(
    genAI: GoogleGenerativeAI,
    private readonly device: DeviceClient,
    modelName: string,
    private readonly maxSteps: number
  ) {
    this.model = genAI.getGenerativeModel({
      model: modelName,
      systemInstruction: SYSTEM_PROMPT,
      tools: [{ functionDeclarations: FUNCTION_DECLARATIONS }],
      // Fuerza al modelo a llamar siempre a una de las herramientas declaradas.
      toolConfig: { functionCallingConfig: { mode: FunctionCallingMode.ANY } },
    });
  }

  async run(task: string): Promise<AgentRunResult> {
    const contents: Content[] = [];

    let snapshot = await this.device.getUi();
    contents.push({
      role: "user",
      parts: [{ text: `Tarea: ${task}\n\n${describeSnapshot(snapshot)}` }],
    });

    for (let step = 1; step <= this.maxSteps; step++) {
      const result = await this.generateWithRetry(contents);
      const response = result.response;

      const call = response.functionCalls()?.[0];

      // Conserva el turno del modelo en el historial para el siguiente ciclo.
      const modelParts = response.candidates?.[0]?.content?.parts ?? [];
      contents.push({ role: "model", parts: modelParts });

      if (!call) {
        throw new Error(
          "El modelo no llamó a ninguna herramienta pese a functionCallingConfig=ANY."
        );
      }

      const args = (call.args ?? {}) as Record<string, unknown>;
      console.log(`[paso ${step}] ${call.name}(${JSON.stringify(args)})`);

      if (call.name === "finish") {
        return {
          success: Boolean(args.success),
          summary: String(args.summary ?? ""),
          steps: step,
        };
      }

      const actionResult = await this.executeTool(call.name, args);
      // Abrir una app tarda en cargar: dale tiempo antes de volver a leer la pantalla.
      await sleep(call.name === "open_app" ? 1500 : 400);
      snapshot = await this.device.getUi();

      contents.push({
        role: "user",
        parts: [
          {
            functionResponse: {
              name: call.name,
              response: { result: actionResult },
            },
          },
          { text: describeSnapshot(snapshot) },
        ],
      });
    }

    return {
      success: false,
      summary: `Se alcanzó el máximo de pasos (${this.maxSteps}) sin que el agente terminara la tarea.`,
      steps: this.maxSteps,
    };
  }

  /**
   * Llama a Gemini reintentando ante el límite de peticiones del plan gratuito
   * (429). Respeta el retryDelay que sugiere la propia API cuando está presente.
   */
  private async generateWithRetry(contents: Content[], maxRetries = 5) {
    let attempt = 0;
    for (;;) {
      try {
        return await this.model.generateContent({ contents });
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        const status = (err as { status?: number })?.status;
        const isRateLimit =
          status === 429 || /\b429\b|too many requests|quota/i.test(message);

        if (!isRateLimit || attempt >= maxRetries) throw err;

        attempt++;
        const waitMs = parseRetryDelayMs(message) ?? Math.min(60000, 15000 * attempt);
        console.log(
          `  (límite de peticiones de Gemini alcanzado; espero ${Math.round(
            waitMs / 1000
          )}s y reintento —  intento ${attempt}/${maxRetries})`
        );
        await sleep(waitMs);
      }
    }
  }

  private async executeTool(name: string, args: Record<string, unknown>) {
    switch (name) {
      case "tap":
        return this.device.tap(args.x as number, args.y as number);
      case "swipe":
        return this.device.swipe(
          args.x1 as number,
          args.y1 as number,
          args.x2 as number,
          args.y2 as number,
          (args.durationMs as number) ?? 300
        );
      case "open_app":
        return this.device.openApp(args.query as string);
      case "click_node":
        return this.device.clickNode(args.nodeId as number);
      case "type_text":
        return this.device.typeText(args.nodeId as number, args.text as string);
      case "back":
        return this.device.back();
      case "home":
        return this.device.home();
      case "recents":
        return this.device.recents();
      case "wait":
        await sleep(args.ms as number);
        return { ok: true };
      default:
        return { ok: false, error: `herramienta desconocida: ${name}` };
    }
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** Extrae el retardo sugerido por la API de un mensaje 429 (p. ej. "retryDelay":"49s"). */
function parseRetryDelayMs(message: string): number | null {
  const json = message.match(/"retryDelay"\s*:\s*"(\d+(?:\.\d+)?)s"/i);
  const prose = message.match(/retry in\s+(\d+(?:\.\d+)?)\s*s/i);
  const seconds = json?.[1] ?? prose?.[1];
  if (!seconds) return null;
  // +1s de margen para asegurarnos de que la ventana ya se ha reabierto.
  return Math.round(parseFloat(seconds) * 1000) + 1000;
}
