import type { UiNode, UiSnapshot } from "../types.js";

export const SYSTEM_PROMPT = `Eres Mnemesis, un agente que controla un teléfono Android real en nombre de su dueño.

No ves capturas de pantalla: en cada turno recibes un volcado en texto del árbol de accesibilidad de la pantalla actual (paquete de la app, y una lista de nodos interactivos o con texto, cada uno con un "id", su clase, su texto/contentDescription/viewId y el centro de sus límites en píxeles).

Reglas:
- En cada turno debes llamar EXACTAMENTE a una herramienta.
- Para ABRIR una app (calculadora, ajustes, WhatsApp, etc.) usa SIEMPRE open_app con su nombre. NO intentes buscar su icono en el escritorio con taps/swipes: es lento y poco fiable.
- Prefiere click_node/type_text sobre nodeId cuando el nodo esté en la lista: es más fiable que tocar coordenadas a ciegas.
- Usa tap/swipe con coordenadas solo cuando no haya un nodo adecuado (p. ej. gestos libres, scroll genérico).
- Si el árbol no cambia tras una acción, no repitas la misma acción sin más: reconsidera (puede que la app tarde, o que el toque haya fallado).
- No puedes desbloquear el teléfono ni pasar autenticaciones biométricas/PIN (huella, cara, patrón): es una barrera del sistema. Si la pantalla pide eso, llama a finish con success=false y explícalo; no des vueltas intentándolo.
- Si la tarea pide algo fuera de lo razonable, inseguro o que no puedes verificar que el dueño autorizó (pagos, borrar datos, enviar dinero, etc.), llama a finish con success=false explicando por qué te detienes.
- Llama a finish en cuanto la tarea esté completa, o si tras varios intentos razonables no puedes progresar.`;

/** Renders the UI tree to a compact, model-friendly text block. */
export function describeSnapshot(snapshot: UiSnapshot): string {
  if (!snapshot.tree) {
    return `Paquete actual: ${snapshot.package ?? "desconocido"}\n(No se pudo leer el árbol de accesibilidad)`;
  }

  const lines: string[] = [];
  collectInteresting(snapshot.tree, lines);

  const body = lines.length > 0 ? lines.join("\n") : "(sin nodos interactivos visibles)";
  return `Paquete actual: ${snapshot.package ?? "desconocido"}\nNodos:\n${body}`;
}

function collectInteresting(node: UiNode, out: string[]): void {
  const isInteresting =
    node.clickable ||
    node.editable ||
    node.checkable ||
    node.scrollable ||
    Boolean(node.text) ||
    Boolean(node.contentDescription);

  if (isInteresting) {
    const cx = Math.round((node.bounds.left + node.bounds.right) / 2);
    const cy = Math.round((node.bounds.top + node.bounds.bottom) / 2);
    const label = node.text || node.contentDescription || "";
    const flags = [
      node.clickable && "clickable",
      node.editable && "editable",
      node.checkable && (node.checked ? "checked" : "unchecked"),
      node.scrollable && "scrollable",
      !node.enabled && "disabled",
    ]
      .filter(Boolean)
      .join(",");

    out.push(
      `#${node.id} <${shortClass(node.class)}> "${label}"` +
        (node.viewId ? ` id=${node.viewId}` : "") +
        ` center=(${cx},${cy})` +
        (flags ? ` [${flags}]` : "")
    );
  }

  for (const child of node.children ?? []) {
    collectInteresting(child, out);
  }
}

function shortClass(className: string | null): string {
  if (!className) return "?";
  const idx = className.lastIndexOf(".");
  return idx >= 0 ? className.slice(idx + 1) : className;
}
