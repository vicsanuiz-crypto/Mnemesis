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
      const result = await this.model.generateContent({ contents });
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
      await sleep(400);
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
