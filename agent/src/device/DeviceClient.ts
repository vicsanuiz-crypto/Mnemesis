import type { ActionResult, UiSnapshot } from "../types.js";

/**
 * Talks to the ControlServer running inside the Mnemesis accessibility
 * service on the phone, normally reached through `adb forward tcp:PORT tcp:PORT`.
 */
export class DeviceClient {
  constructor(private readonly baseUrl: string) {}

  async getUi(): Promise<UiSnapshot> {
    const res = await fetch(`${this.baseUrl}/ui`);
    if (!res.ok) {
      throw new Error(`GET /ui failed: ${res.status} ${await res.text()}`);
    }
    return (await res.json()) as UiSnapshot;
  }

  async tap(x: number, y: number): Promise<ActionResult> {
    return this.postAction({ type: "tap", x, y });
  }

  async longPress(x: number, y: number): Promise<ActionResult> {
    return this.postAction({ type: "long_press", x, y });
  }

  async swipe(
    x1: number,
    y1: number,
    x2: number,
    y2: number,
    durationMs = 300
  ): Promise<ActionResult> {
    return this.postAction({ type: "swipe", x1, y1, x2, y2, durationMs });
  }

  async openApp(query: string): Promise<ActionResult> {
    return this.postAction({ type: "open_app", query });
  }

  async clickNode(nodeId: number): Promise<ActionResult> {
    return this.postAction({ type: "click_node", nodeId });
  }

  async typeText(nodeId: number, text: string): Promise<ActionResult> {
    return this.postAction({ type: "type_text", nodeId, text });
  }

  async back(): Promise<ActionResult> {
    return this.postAction({ type: "back" });
  }

  async home(): Promise<ActionResult> {
    return this.postAction({ type: "home" });
  }

  async recents(): Promise<ActionResult> {
    return this.postAction({ type: "recents" });
  }

  private async postAction(body: Record<string, unknown>): Promise<ActionResult> {
    const res = await fetch(`${this.baseUrl}/action`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    const json = (await res.json()) as ActionResult;
    if (!res.ok) {
      return { ok: false, error: json.error ?? `HTTP ${res.status}` };
    }
    return json;
  }
}
