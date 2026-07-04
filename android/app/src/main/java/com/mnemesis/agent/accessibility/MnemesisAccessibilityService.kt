package com.mnemesis.agent.accessibility

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.os.Bundle
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import com.mnemesis.agent.model.UiNode
import com.mnemesis.agent.server.ControlServer
import com.mnemesis.agent.util.GestureExecutor
import com.mnemesis.agent.util.UiTreeSerializer
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

/**
 * Reads the on-screen accessibility tree and executes taps/swipes/text-entry
 * requested by the off-device agent. No screenshots or pixel data ever leave
 * the device: only the structured UI tree (text, ids, bounds, roles).
 */
class MnemesisAccessibilityService : AccessibilityService() {

    private var controlServer: ControlServer? = null

    companion object {
        private const val TAG = "MnemesisService"
        const val CONTROL_PORT = 8734

        @Volatile
        var instance: MnemesisAccessibilityService? = null
            private set
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
        Log.i(TAG, "Accessibility service connected")

        controlServer = ControlServer(this, CONTROL_PORT).also {
            try {
                it.start(5000, false)
                Log.i(TAG, "Control server listening on 127.0.0.1:$CONTROL_PORT")
            } catch (e: Exception) {
                Log.e(TAG, "Failed to start control server", e)
            }
        }
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // The agent pulls the tree on demand via /ui; no need to react to every event.
    }

    override fun onInterrupt() {
        Log.w(TAG, "Accessibility service interrupted")
    }

    override fun onDestroy() {
        controlServer?.stop()
        controlServer = null
        instance = null
        super.onDestroy()
    }

    fun currentPackageName(): String? = rootInActiveWindow?.packageName?.toString()

    fun dumpUiTree(): UiNode? {
        val root = rootInActiveWindow ?: return null
        return UiTreeSerializer.serialize(root)
    }

    fun tap(x: Float, y: Float): Boolean = runGesture(GestureExecutor.tap(x, y))

    fun longPress(x: Float, y: Float): Boolean = runGesture(GestureExecutor.longPress(x, y))

    fun swipe(x1: Float, y1: Float, x2: Float, y2: Float, durationMs: Long): Boolean =
        runGesture(GestureExecutor.swipe(x1, y1, x2, y2, durationMs))

    /** Sets the text of the node with the given id (must be editable). */
    fun typeText(nodeId: Int, text: String): Boolean {
        val target = findNodeById(nodeId) ?: return false
        val arguments = Bundle().apply {
            putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
        }
        return target.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)
    }

    /** Clicks the node with the given id via the accessibility action (no coordinates needed). */
    fun clickNode(nodeId: Int): Boolean {
        val target = findNodeById(nodeId) ?: return false
        return target.performAction(AccessibilityNodeInfo.ACTION_CLICK)
    }

    fun back(): Boolean = performGlobalAction(GLOBAL_ACTION_BACK)

    fun home(): Boolean = performGlobalAction(GLOBAL_ACTION_HOME)

    fun recents(): Boolean = performGlobalAction(GLOBAL_ACTION_RECENTS)

    private fun findNodeById(nodeId: Int): AccessibilityNodeInfo? {
        val root = rootInActiveWindow ?: return null
        return findNodeByIdRecursive(root, intArrayOf(0), 0, nodeId)
    }

    // Traversal order/limits must mirror UiTreeSerializer.build so ids line up.
    private fun findNodeByIdRecursive(
        node: AccessibilityNodeInfo,
        counter: IntArray,
        depth: Int,
        target: Int
    ): AccessibilityNodeInfo? {
        if (counter[0] >= UiTreeSerializer.MAX_NODES || depth >= UiTreeSerializer.MAX_DEPTH) {
            return null
        }
        val id = counter[0]++
        if (id == target) return node
        for (i in 0 until node.childCount) {
            val child = node.getChild(i) ?: continue
            findNodeByIdRecursive(child, counter, depth + 1, target)?.let { return it }
        }
        return null
    }

    private fun runGesture(gesture: GestureDescription): Boolean {
        val latch = CountDownLatch(1)
        var result = false
        val callback = object : GestureResultCallback() {
            override fun onCompleted(gestureDescription: GestureDescription?) {
                result = true
                latch.countDown()
            }

            override fun onCancelled(gestureDescription: GestureDescription?) {
                result = false
                latch.countDown()
            }
        }
        val dispatched = dispatchGesture(gesture, callback, null)
        if (!dispatched) return false
        latch.await(5, TimeUnit.SECONDS)
        return result
    }
}
