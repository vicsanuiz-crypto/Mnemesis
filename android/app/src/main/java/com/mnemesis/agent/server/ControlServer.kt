package com.mnemesis.agent.server

import android.util.Log
import com.mnemesis.agent.accessibility.MnemesisAccessibilityService
import fi.iki.elonen.NanoHTTPD
import org.json.JSONObject

/**
 * Local-only HTTP control plane for the accessibility service. Bound to
 * 127.0.0.1 so it is never reachable over the network directly -- the agent
 * on the host machine reaches it through `adb forward tcp:8734 tcp:8734`.
 */
class ControlServer(
    private val service: MnemesisAccessibilityService,
    port: Int
) : NanoHTTPD("127.0.0.1", port) {

    companion object {
        private const val TAG = "ControlServer"
    }

    override fun serve(session: IHTTPSession): Response {
        return try {
            when {
                session.method == Method.GET && session.uri == "/health" ->
                    jsonResponse(JSONObject().put("status", "ok"))

                session.method == Method.GET && session.uri == "/ui" ->
                    handleGetUi()

                session.method == Method.POST && session.uri == "/action" ->
                    handleAction(session)

                else -> jsonResponse(
                    JSONObject().put("ok", false).put("error", "not found"),
                    Response.Status.NOT_FOUND
                )
            }
        } catch (e: Exception) {
            Log.e(TAG, "Request failed", e)
            jsonResponse(
                JSONObject().put("ok", false).put("error", e.message ?: "internal error"),
                Response.Status.INTERNAL_ERROR
            )
        }
    }

    private fun handleGetUi(): Response {
        val tree = service.dumpUiTree()
        val body = JSONObject()
            .put("package", service.currentPackageName())
            .put("tree", tree?.toJson())
        return jsonResponse(body)
    }

    private fun handleAction(session: IHTTPSession): Response {
        val body = readBody(session)
        val json = JSONObject(body)
        val type = json.optString("type")

        val ok: Boolean = when (type) {
            "tap" -> service.tap(
                json.getDouble("x").toFloat(),
                json.getDouble("y").toFloat()
            )

            "long_press" -> service.longPress(
                json.getDouble("x").toFloat(),
                json.getDouble("y").toFloat()
            )

            "swipe" -> service.swipe(
                json.getDouble("x1").toFloat(),
                json.getDouble("y1").toFloat(),
                json.getDouble("x2").toFloat(),
                json.getDouble("y2").toFloat(),
                json.optLong("durationMs", 300L)
            )

            "open_app" -> service.openApp(json.getString("query"))

            "click_node" -> service.clickNode(json.getInt("nodeId"))

            "type_text" -> service.typeText(json.getInt("nodeId"), json.getString("text"))

            "back" -> service.back()
            "home" -> service.home()
            "recents" -> service.recents()

            else -> throw IllegalArgumentException("unknown action type: $type")
        }

        return jsonResponse(JSONObject().put("ok", ok))
    }

    private fun readBody(session: IHTTPSession): String {
        val contentLength = session.headers["content-length"]?.toIntOrNull() ?: 0
        if (contentLength <= 0) return "{}"
        val buffer = ByteArray(contentLength)
        var offset = 0
        while (offset < contentLength) {
            val read = session.inputStream.read(buffer, offset, contentLength - offset)
            if (read < 0) break
            offset += read
        }
        return String(buffer, 0, offset)
    }

    private fun jsonResponse(
        json: JSONObject,
        status: Response.Status = Response.Status.OK
    ): Response = newFixedLengthResponse(status, "application/json", json.toString())
}
