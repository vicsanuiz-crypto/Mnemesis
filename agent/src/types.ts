export interface Bounds {
  left: number;
  top: number;
  right: number;
  bottom: number;
}

export interface UiNode {
  id: number;
  class: string | null;
  text: string | null;
  contentDescription: string | null;
  viewId: string | null;
  package: string | null;
  bounds: Bounds;
  clickable: boolean;
  focusable: boolean;
  focused: boolean;
  checkable: boolean;
  checked: boolean;
  scrollable: boolean;
  enabled: boolean;
  editable: boolean;
  children?: UiNode[];
}

export interface UiSnapshot {
  package: string | null;
  tree: UiNode | null;
}

export interface ActionResult {
  ok: boolean;
  error?: string;
}
