import Anthropic from "@anthropic-ai/sdk";
import type { DeviceClient } from "../device/DeviceClient.js";
import { SYSTEM_PROMPT, describeSnapshot } from "./prompts.js";

const TOOLS: Anthropic.Tool[] = [
  {
    name: "tap",
    description: "Toca la pantalla en unas coordenadas de píxel absolutas.",
    input_schema: {
      type: "object",
      properties: {
        x: { type: "number" },
        y: { type: "number" },
      },
      required: ["x", "y"],
    },
  },
  {
    name: "swipe",
    description: "Desliza el dedo entre dos puntos de la pantalla (scroll, deslizar para cerrar, etc.).",
    input_schema: {
      type: "object",
      properties: {
        x1: { type: "number" },
        y1: { type: "number" },
        x2: { type: "number" },
        y2: { type: "number" },
        durationMs: { type: "number", description: "Duración del gesto en ms (por defecto 300)." },
      },
      required: ["x1", "y1", "x2", "y2"],
    },
  },
  {
    name: "click_node",
    description: "Pulsa el nodo de accesibilidad con el id indicado (preferido frente a tap cuando el nodo está en la lista).",
    input_schema: {
      type: "object",
      properties: { nodeId: { type: "number" } },
      required: ["nodeId"],
    },
  },
  {
    name: "type_text",
    description: "Escribe texto en el nodo editable con el id indicado.",
    input_schema: {
      type: "object",
      properties: {
        nodeId: { type: "number" },
        text: { type: "string" },
      },
      required: ["nodeId", "text"],
    },
  },
  {
    name: "back",
    description: "Pulsa el botón/gesto de retroceso del sistema.",
    input_schema: { type: "object", properties: {} },
  },
  {
    name: "home",
    description: "Va a la pantalla de inicio.",
    input_schema: { type: "object", properties: {} },
  },
  {
    name: "recents",
    description: "Abre la vista de apps recientes.",
    input_schema: { type: "object", properties: {} },
  },
  {
    name: "wait",
    description: "Espera un momento (p. ej. mientras carga una app) antes de volver a mirar la pantalla.",
    input_schema: {
      type: "object",
      properties: { ms: { type: "number" } },
      required: ["ms"],
    },
  },
  {
    name: "finish",
    description: "Termina la tarea: indica si se completó con éxito y un resumen breve.",
    input_schema: {
      type: "object",
      properties: {
        success: { type: "boolean" },
        summary: { type: "string" },
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
  constructor(
    private readonly anthropic: Anthropic,
    private readonly device: DeviceClient,
    private readonly model: string,
    private readonly maxSteps: number
  ) {}

  async run(task: string): Promise<AgentRunResult> {
    const messages: Anthropic.MessageParam[] = [];

    let snapshot = await this.device.getUi();
    messages.push({
      role: "user",
      content: `Tarea: ${task}\n\n${describeSnapshot(snapshot)}`,
    });

    for (let step = 1; step <= this.maxSteps; step++) {
      const response = await this.anthropic.messages.create({
        model: this.model,
        max_tokens: 1024,
        system: SYSTEM_PROMPT,
        tools: TOOLS,
        tool_choice: { type: "any" },
        messages,
      });

      messages.push({ role: "assistant", content: response.content });

      const toolUse = response.content.find(
        (block): block is Anthropic.ToolUseBlock => block.type === "tool_use"
      );

      if (!toolUse) {
        throw new Error("El modelo no llamó a ninguna herramienta pese a tool_choice=any.");
      }

      console.log(`[paso ${step}] ${toolUse.name}(${JSON.stringify(toolUse.input)})`);

      if (toolUse.name === "finish") {
        const input = toolUse.input as { success: boolean; summary: string };
        return { success: input.success, summary: input.summary, steps: step };
      }

      const actionResult = await this.executeTool(toolUse.name, toolUse.input as Record<string, unknown>);
      await sleep(400);
      snapshot = await this.device.getUi();

      messages.push({
        role: "user",
        content: [
          {
            type: "tool_result",
            tool_use_id: toolUse.id,
            content: `Resultado: ${JSON.stringify(actionResult)}\n\n${describeSnapshot(snapshot)}`,
          },
        ],
      });
    }

    return {
      success: false,
      summary: `Se alcanzó el máximo de pasos (${this.maxSteps}) sin que el agente terminara la tarea.`,
      steps: this.maxSteps,
    };
  }

  private async executeTool(name: string, input: Record<string, unknown>) {
    switch (name) {
      case "tap":
        return this.device.tap(input.x as number, input.y as number);
      case "swipe":
        return this.device.swipe(
          input.x1 as number,
          input.y1 as number,
          input.x2 as number,
          input.y2 as number,
          (input.durationMs as number) ?? 300
        );
      case "click_node":
        return this.device.clickNode(input.nodeId as number);
      case "type_text":
        return this.device.typeText(input.nodeId as number, input.text as string);
      case "back":
        return this.device.back();
      case "home":
        return this.device.home();
      case "recents":
        return this.device.recents();
      case "wait":
        await sleep(input.ms as number);
        return { ok: true };
      default:
        return { ok: false, error: `herramienta desconocida: ${name}` };
    }
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
