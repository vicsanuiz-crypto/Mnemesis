import "dotenv/config";
import Anthropic from "@anthropic-ai/sdk";
import { DeviceClient } from "./device/DeviceClient.js";
import { MnemesisAgent } from "./agent/MnemesisAgent.js";

async function main() {
  const task = process.argv.slice(2).join(" ").trim();
  if (!task) {
    console.error('Uso: npm start -- "abre WhatsApp y manda un mensaje a Juan diciendo hola"');
    process.exit(1);
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    console.error("Falta ANTHROPIC_API_KEY. Copia agent/.env.example a agent/.env y rellénalo.");
    process.exit(1);
  }

  const deviceUrl = process.env.MNEMESIS_DEVICE_URL ?? "http://127.0.0.1:8734";
  const model = process.env.MNEMESIS_MODEL ?? "claude-sonnet-5";
  const maxSteps = Number(process.env.MNEMESIS_MAX_STEPS ?? 25);

  const anthropic = new Anthropic({ apiKey });
  const device = new DeviceClient(deviceUrl);
  const agent = new MnemesisAgent(anthropic, device, model, maxSteps);

  console.log(`Mnemesis: conectando con el dispositivo en ${deviceUrl}...`);
  const health = await fetch(`${deviceUrl}/health`).catch(() => null);
  if (!health || !health.ok) {
    console.error(
      "No se pudo contactar con el teléfono. Verifica: el servicio de accesibilidad Mnemesis está activo, " +
        "y ejecutaste `adb forward tcp:8734 tcp:8734` con el móvil conectado."
    );
    process.exit(1);
  }

  console.log(`Mnemesis: iniciando tarea -> "${task}"`);
  const result = await agent.run(task);

  console.log("\n--- Resultado ---");
  console.log(`Éxito: ${result.success}`);
  console.log(`Pasos: ${result.steps}`);
  console.log(`Resumen: ${result.summary}`);
  process.exit(result.success ? 0 : 1);
}

main().catch((err) => {
  console.error("Error fatal:", err);
  process.exit(1);
});
