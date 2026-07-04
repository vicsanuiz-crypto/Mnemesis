package com.mnemesis.agent.model

import org.json.JSONArray
import org.json.JSONObject

/**
 * Flattened, serializable view of an AccessibilityNodeInfo subtree.
 * `id` is a per-dump index the agent can reference in action requests
 * (e.g. {"type":"tap","nodeId":17}) instead of raw coordinates.
 */
data class UiNode(
    val id: Int,
    val className: String?,
    val text: String?,
    val contentDescription: String?,
    val viewIdResourceName: String?,
    val packageName: String?,
    val bounds: Bounds,
    val clickable: Boolean,
    val focusable: Boolean,
    val focused: Boolean,
    val checkable: Boolean,
    val checked: Boolean,
    val scrollable: Boolean,
    val enabled: Boolean,
    val editable: Boolean,
    val children: List<UiNode>
) {
    data class Bounds(val left: Int, val top: Int, val right: Int, val bottom: Int) {
        fun centerX() = (left + right) / 2
        fun centerY() = (top + bottom) / 2

        fun toJson(): JSONObject = JSONObject()
            .put("left", left)
            .put("top", top)
            .put("right", right)
            .put("bottom", bottom)
    }

    fun toJson(): JSONObject {
        val json = JSONObject()
            .put("id", id)
            .put("class", className)
            .put("text", text)
            .put("contentDescription", contentDescription)
            .put("viewId", viewIdResourceName)
            .put("package", packageName)
            .put("bounds", bounds.toJson())
            .put("clickable", clickable)
            .put("focusable", focusable)
            .put("focused", focused)
            .put("checkable", checkable)
            .put("checked", checked)
            .put("scrollable", scrollable)
            .put("enabled", enabled)
            .put("editable", editable)

        if (children.isNotEmpty()) {
            val childArray = JSONArray()
            children.forEach { childArray.put(it.toJson()) }
            json.put("children", childArray)
        }
        return json
    }

    /** Depth-first search for a node previously handed to the agent by id. */
    fun findById(target: Int): UiNode? {
        if (id == target) return this
        for (child in children) {
            child.findById(target)?.let { return it }
        }
        return null
    }
}
