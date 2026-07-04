package com.mnemesis.agent.util

import android.graphics.Rect
import android.view.accessibility.AccessibilityNodeInfo
import com.mnemesis.agent.model.UiNode

/**
 * Walks the live AccessibilityNodeInfo tree and turns it into a plain,
 * serializable UiNode tree the agent (running off-device) can reason about.
 */
object UiTreeSerializer {

    const val MAX_NODES = 800
    const val MAX_DEPTH = 60

    fun serialize(root: AccessibilityNodeInfo?): UiNode? {
        if (root == null) return null
        val counter = intArrayOf(0)
        return build(root, counter, 0)
    }

    private fun build(node: AccessibilityNodeInfo, counter: IntArray, depth: Int): UiNode? {
        if (counter[0] >= MAX_NODES || depth >= MAX_DEPTH) return null

        val bounds = Rect()
        node.getBoundsInScreen(bounds)

        val id = counter[0]++
        val children = mutableListOf<UiNode>()

        for (i in 0 until node.childCount) {
            val child = node.getChild(i) ?: continue
            build(child, counter, depth + 1)?.let { children.add(it) }
        }

        return UiNode(
            id = id,
            className = node.className?.toString(),
            text = node.text?.toString(),
            contentDescription = node.contentDescription?.toString(),
            viewIdResourceName = node.viewIdResourceName,
            packageName = node.packageName?.toString(),
            bounds = UiNode.Bounds(bounds.left, bounds.top, bounds.right, bounds.bottom),
            clickable = node.isClickable,
            focusable = node.isFocusable,
            focused = node.isFocused,
            checkable = node.isCheckable,
            checked = node.isChecked,
            scrollable = node.isScrollable,
            enabled = node.isEnabled,
            editable = node.isEditable,
            children = children
        )
    }
}
