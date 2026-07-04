package com.mnemesis.agent.util

import android.accessibilityservice.GestureDescription
import android.graphics.Path

/** Builds GestureDescription objects for the taps/swipes the agent requests. */
object GestureExecutor {

    private const val DEFAULT_TAP_DURATION_MS = 60L

    fun tap(x: Float, y: Float, durationMs: Long = DEFAULT_TAP_DURATION_MS): GestureDescription {
        val path = Path().apply { moveTo(x, y) }
        val stroke = GestureDescription.StrokeDescription(path, 0, durationMs)
        return GestureDescription.Builder().addStroke(stroke).build()
    }

    fun longPress(x: Float, y: Float, durationMs: Long = 600L): GestureDescription {
        val path = Path().apply { moveTo(x, y) }
        val stroke = GestureDescription.StrokeDescription(path, 0, durationMs)
        return GestureDescription.Builder().addStroke(stroke).build()
    }

    fun swipe(
        x1: Float,
        y1: Float,
        x2: Float,
        y2: Float,
        durationMs: Long = 300L
    ): GestureDescription {
        val path = Path().apply {
            moveTo(x1, y1)
            lineTo(x2, y2)
        }
        val stroke = GestureDescription.StrokeDescription(path, 0, durationMs)
        return GestureDescription.Builder().addStroke(stroke).build()
    }
}
