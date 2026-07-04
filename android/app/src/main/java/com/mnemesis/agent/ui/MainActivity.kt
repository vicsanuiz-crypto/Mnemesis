package com.mnemesis.agent.ui

import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.mnemesis.agent.R
import com.mnemesis.agent.accessibility.MnemesisAccessibilityService

class MainActivity : AppCompatActivity() {

    private lateinit var textServiceStatus: TextView
    private lateinit var textServerStatus: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        textServiceStatus = findViewById(R.id.textServiceStatus)
        textServerStatus = findViewById(R.id.textServerStatus)

        findViewById<Button>(R.id.btnOpenSettings).setOnClickListener {
            startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
        }
    }

    override fun onResume() {
        super.onResume()
        refreshStatus()
    }

    private fun refreshStatus() {
        val running = MnemesisAccessibilityService.instance != null
        textServiceStatus.text = getString(
            if (running) R.string.status_service_enabled else R.string.status_service_disabled
        )
        textServerStatus.text = if (running) {
            getString(R.string.status_server_running, MnemesisAccessibilityService.CONTROL_PORT)
        } else {
            ""
        }
    }
}
