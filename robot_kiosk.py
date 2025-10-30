#!/usr/bin/env python3
#Install the required dependencies to run this script using requirements.txt file
"""
robot_kiosk.py

Single-file PyQt5 kiosk GUI for a humanoid robot prototype (simulated sensors).
- Fullscreen kiosk (frameless). ESC to exit.
- Pages: Home | Motor Control | Sensors | Settings
- Interactive robot diagram -> opens circular QDial for motor control (0-100)
- Simulated battery, CPU, IMU, gas sensor updates via QTimer
- Replace simulated parts with real sensor reads (serial, I2C, network) in the indicated places.
"""

import sys
import random
from PyQt5.QtCore import Qt, QTimer, QRect, QSize
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QFrame, QGridLayout, QSlider, QDialog, QDial, QGroupBox
)


# ---------------------------
# Custom circular progress widget
# ---------------------------
class CircularProgress(QWidget):
    def __init__(self, label="MOTOR", color=QColor(80, 200, 255), parent=None):
        super().__init__(parent)
        self.value = 0
        self.label = label
        self.color = color
        self.setMinimumSize(130, 130)

    def setValue(self, v):
        self.value = max(0, min(100, int(v)))
        self.update()

    def paintEvent(self, event):
        r = self.rect()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        margin = 10
        rect = r.adjusted(margin, margin, -margin, -margin)

        # Background circle
        pen_bg = QPen(QColor(35, 40, 50), 12)
        painter.setPen(pen_bg)
        painter.drawEllipse(rect)

        # Arc for progress
        pen_arc = QPen(self.color, 12)
        painter.setPen(pen_arc)
        start_angle = 90 * 16
        span_angle = -int(360 * 16 * (self.value / 100.0))
        painter.drawArc(rect, start_angle, span_angle)

        # Text label + value
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 11, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, f"{self.label}\n{self.value}%")

# ---------------------------
# Dial popup dialog for circular control
# ---------------------------
class DialDialog(QDialog):
    def __init__(self, title, initial=50, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)
        self.setStyleSheet("background-color: rgba(20,20,26,230); color: #e6eef8;")
        self.resize(260, 300)

        layout = QVBoxLayout()
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(label)

        self.dial = QDial()
        self.dial.setRange(0, 100)
        self.dial.setValue(initial)
        self.dial.setNotchesVisible(True)
        self.dial.setFixedSize(180, 180)
        self.dial.setWrapping(False)
        layout.addWidget(self.dial, alignment=Qt.AlignCenter)

        self.value_label = QLabel(f"{initial}%")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.value_label)

        btn_close = QPushButton("Done")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.dial.valueChanged.connect(self._on_change)

    def _on_change(self, val):
        self.value_label.setText(f"{val}%")

    def get_value(self):
        return self.dial.value()


# ---------------------------
# Main Kiosk Application
# ---------------------------
class RobotKiosk(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Humanoid Robot Kiosk")
        self.setWindowFlags(Qt.FramelessWindowHint)  # frameless
        self.showFullScreen()  # fullscreen kiosk

        # Top-level styling
        self.setStyleSheet("""
            QWidget { background-color: #0b0f14; color: #dbe7ff; font-family: 'Segoe UI'; }
            QLabel#title { font-size: 22px; font-weight: 700; color: #9ad0ff; }
            QPushButton.nav { background-color: transparent; color: #98c1ff; border: none; padding: 8px 14px; font-size:14px; }
            QPushButton.nav:hover { color: #ffffff; }
            QFrame#topbar { background-color: #07101a; border-bottom: 1px solid #0e2a3b; }
            QGroupBox { border: 1px solid #102233; border-radius: 8px; padding: 8px; margin-top: 8px; }
        """)

        # State for motors (simulated)
        self.motors = {
            "ARM": 50,
            "WRIST": 50,
            "TENTACLE": 50
        }

        # Layout: top bar + content
        v_main = QVBoxLayout()
        v_main.setContentsMargins(6, 6, 6, 6)
        v_main.setSpacing(8)

        # Top bar
        top_bar = QFrame()
        top_bar.setObjectName("topbar")
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 8, 10, 8)

        title = QLabel("HUMANOID ROBOT CONTROL")
        title.setObjectName("title")
        top_layout.addWidget(title)

        top_layout.addStretch()

        # Connection and battery readouts (simulated)
        self.conn_label = QLabel("WiFi: --")
        self.batt_label = QLabel("🔋 100% (12.6V)")
        self.uptime_label = QLabel("Uptime: 00:00:00")
        for w in (self.conn_label, self.batt_label, self.uptime_label):
            w.setStyleSheet("font-size: 13px; padding-left:8px; padding-right:8px;")
            top_layout.addWidget(w)

        # Navigation buttons
        nav_buttons = QHBoxLayout()
        nav_buttons.setSpacing(6)
        pages = [("Home", 0), ("Motor", 1), ("Sensors", 2), ("Settings", 3)]
        self.page_buttons = {}
        for name, idx in pages:
            b = QPushButton(name)
            b.setObjectName("nav")
            b.setProperty("page_index", idx)
            b.setProperty("class", "nav")
            b.clicked.connect(self._on_nav)
            nav_buttons.addWidget(b)
            self.page_buttons[idx] = b
        top_layout.addLayout(nav_buttons)

        top_bar.setLayout(top_layout)
        v_main.addWidget(top_bar)

        # Stacked widget for pages
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_home_page())
        self.stack.addWidget(self._build_motor_page())
        self.stack.addWidget(self._build_sensors_page())
        self.stack.addWidget(self._build_settings_page())
        v_main.addWidget(self.stack)

        # Footer hint
        footer = QLabel("Press ESC to exit kiosk mode")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size:12px; color:#7f8ea6; padding:6px;")
        v_main.addWidget(footer)

        self.setLayout(v_main)

        # Timers for simulated updates
        self._setup_timers()

    # ---------------------------
    # Page builders
    # ---------------------------
    def _build_home_page(self):
        page = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(20)

        # Left: overview cards
        left = QVBoxLayout()
        left.setSpacing(12)

        # System status group
        sys_grp = QGroupBox("System Status")
        sys_layout = QVBoxLayout()
        self.cpu_label = QLabel("CPU: 12% | Mem: 24% | Temp: 42°C")
        self.cam_label = QLabel("Camera: Ready")
        self.ai_label = QLabel("AI: Idle")
        sys_layout.addWidget(self.cpu_label)
        sys_layout.addWidget(self.cam_label)
        sys_layout.addWidget(self.ai_label)
        sys_grp.setLayout(sys_layout)
        left.addWidget(sys_grp)

        # Battery group
        batt_grp = QGroupBox("Battery")
        batt_layout = QVBoxLayout()
        self.batt_large_label = QLabel("🔋 100%")
        self.batt_large_label.setFont(QFont("Arial", 18, QFont.Bold))
        batt_layout.addWidget(self.batt_large_label)
        batt_layout.addWidget(QLabel("Voltage: 12.6 V"))
        batt_layout.addWidget(QLabel("Estimated runtime: 1h 24m"))
        batt_grp.setLayout(batt_layout)
        left.addWidget(batt_grp)

        left.addStretch()
        layout.addLayout(left, 2)

        # Right: big camera placeholder and fold
        right = QVBoxLayout()
        cam_box = QGroupBox("Front Camera")
        cam_layout = QVBoxLayout()
        cam_placeholder = QLabel("Camera feed placeholder")
        cam_placeholder.setAlignment(Qt.AlignCenter)
        cam_placeholder.setStyleSheet("background-color:#06101a; border-radius:8px; padding:20px;")
        cam_placeholder.setFixedHeight(240)
        cam_layout.addWidget(cam_placeholder)
        cam_box.setLayout(cam_layout)
        right.addWidget(cam_box)

        right.addStretch()
        layout.addLayout(right, 3)

        page.setLayout(layout)
        return page

    def _build_motor_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(12)

        # Top row: circular widgets
        circ_row = QHBoxLayout()
        self.circ_arm = CircularProgress("ARM", QColor(95, 197, 255))
        self.circ_wrist = CircularProgress("WRIST", QColor(135, 255, 185))
        self.circ_tent = CircularProgress("TENTACLE", QColor(255, 190, 125))
        self.circ_arm.setValue(self.motors["ARM"])
        self.circ_wrist.setValue(self.motors["WRIST"])
        self.circ_tent.setValue(self.motors["TENTACLE"])
        circ_row.addWidget(self.circ_arm)
        circ_row.addWidget(self.circ_wrist)
        circ_row.addWidget(self.circ_tent)
        layout.addLayout(circ_row)

        # Middle: sliders & presets
        mid = QHBoxLayout()
        sliders = QVBoxLayout()
        sliders.addWidget(QLabel("Manual sliders"))
        s_row = QHBoxLayout()
        self.s_arm = self._create_vertical_slider(self.motors["ARM"])
        self.s_wrist = self._create_vertical_slider(self.motors["WRIST"])
        self.s_tent = self._create_vertical_slider(self.motors["TENTACLE"])
        s_row.addWidget(self.s_arm)
        s_row.addWidget(self.s_wrist)
        s_row.addWidget(self.s_tent)
        sliders.addLayout(s_row)
        mid.addLayout(sliders, 2)

        # Right: interactive robot diagram (clickable parts)
        diagram_box = QGroupBox("Robot Diagram (tap parts)")
        diag_layout = QGridLayout()
        diagram_widget = QWidget()
        diagram_widget.setMinimumSize(360, 280)
        diagram_widget.setStyleSheet("background-color: #07121a; border-radius:8px;")
        # We'll place invisible-looking circular buttons at positions
        self.btn_arm = QPushButton("Arm")
        self.btn_wrist = QPushButton("Wrist")
        self.btn_tent = QPushButton("Tentacle")

        for b in (self.btn_arm, self.btn_wrist, self.btn_tent):
            b.setStyleSheet("""
                QPushButton {
                  background-color: #0e2733;
                  color: #cfeeff;
                  border-radius: 28px;
                  min-width: 80px; min-height: 48px;
                }
                QPushButton:pressed { background-color: #163845; }
            """)
        # Positioning in a grid-ish manner
        diag_layout.addWidget(self.btn_arm, 0, 1, alignment=Qt.AlignCenter)
        diag_layout.addWidget(self.btn_wrist, 1, 0, alignment=Qt.AlignCenter)
        diag_layout.addWidget(self.btn_tent, 1, 2, alignment=Qt.AlignCenter)

        diagram_box.setLayout(diag_layout)
        mid.addWidget(diagram_box, 1)

        layout.addLayout(mid)

        # Preset / speed controls
        bottom_row = QHBoxLayout()
        preset_box = QGroupBox("Presets")
        p_layout = QHBoxLayout()
        for name in ("Stand", "Wave", "Relax"):
            b = QPushButton(name)
            b.clicked.connect(lambda _, n=name: self._apply_preset(n))
            p_layout.addWidget(b)
        preset_box.setLayout(p_layout)
        bottom_row.addWidget(preset_box)

        speed_box = QGroupBox("Global Speed")
        sp_layout = QVBoxLayout()
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(10, 200)
        self.speed_slider.setValue(100)
        sp_layout.addWidget(self.speed_slider)
        speed_box.setLayout(sp_layout)
        bottom_row.addWidget(speed_box)

        layout.addLayout(bottom_row)

        # Connect interactions
        self.s_arm.valueChanged.connect(lambda v: self._set_motor("ARM", v))
        self.s_wrist.valueChanged.connect(lambda v: self._set_motor("WRIST", v))
        self.s_tent.valueChanged.connect(lambda v: self._set_motor("TENTACLE", v))

        self.btn_arm.clicked.connect(lambda: self._open_dial("ARM"))
        self.btn_wrist.clicked.connect(lambda: self._open_dial("WRIST"))
        self.btn_tent.clicked.connect(lambda: self._open_dial("TENTACLE"))

        page.setLayout(layout)
        return page

    def _build_sensors_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        stats_box = QGroupBox("Sensor Readouts")
        gl = QHBoxLayout()

        # IMU
        imu_box = QGroupBox("IMU (Pitch / Roll / Yaw)")
        imu_layout = QVBoxLayout()
        self.imu_label = QLabel("Pitch: 0.0° | Roll: 0.0° | Yaw: 0.0°")
        imu_layout.addWidget(self.imu_label)
        imu_box.setLayout(imu_layout)
        gl.addWidget(imu_box)

        # Proximity / ToF placeholders
        prox_box = QGroupBox("Proximity")
        prox_layout = QVBoxLayout()
        self.prox_label = QLabel("Front: 120 cm | Left: 200 cm | Right: 200 cm")
        prox_layout.addWidget(self.prox_label)
        prox_box.setLayout(prox_layout)
        gl.addWidget(prox_box)

        # Gas / Environment
        env_box = QGroupBox("Environment")
        env_layout = QVBoxLayout()
        self.gas_label = QLabel("Air Quality: OK (MQ: 120)")
        self.temp_label = QLabel("Temp: 26°C | Humidity: 44%")
        env_layout.addWidget(self.gas_label)
        env_layout.addWidget(self.temp_label)
        env_box.setLayout(env_layout)
        gl.addWidget(env_box)

        stats_box.setLayout(gl)
        layout.addWidget(stats_box)

        # Graph placeholders or logs (simple)
        layout.addWidget(QLabel("Sensor log (simulated)"))
        self.sensor_log = QLabel("No recent events.")
        self.sensor_log.setStyleSheet("background-color:#04121a; padding:8px;")
        layout.addWidget(self.sensor_log)

        page.setLayout(layout)
        return page

    def _build_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        network_box = QGroupBox("Network")
        net_layout = QHBoxLayout()
        self.wifi_entry = QLabel("WiFi: Not connected (simulated)")
        net_layout.addWidget(self.wifi_entry)
        network_box.setLayout(net_layout)
        layout.addWidget(network_box)

        power_box = QGroupBox("Power & Battery")
        p_layout = QVBoxLayout()
        p_layout.addWidget(QLabel("Battery monitoring: INA219 / MAX17043 (placeholder)"))
        p_layout.addWidget(QLabel("BMS: Connect matching cell-count BMS for LiPo packs"))
        power_box.setLayout(p_layout)
        layout.addWidget(power_box)

        debug_box = QGroupBox("Debug & Maintenance")
        d_layout = QVBoxLayout()
        btn_reboot = QPushButton("Simulate Reboot")
        btn_reboot.clicked.connect(lambda: self.sensor_log.setText("Reboot simulated."))
        d_layout.addWidget(btn_reboot)
        debug_box.setLayout(d_layout)
        layout.addWidget(debug_box)

        btn_shutdown = QPushButton("Shutdown Robot")
        btn_shutdown.setStyleSheet("""
            QPushButton {
                background-color: #a83232;
                color: white;
                border-radius: 6px;
                padding: 6px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c94444;
            }
        """)
        btn_shutdown.clicked.connect(self._shutdown_robot)
        d_layout.addWidget(btn_shutdown)

        layout.addStretch()
        page.setLayout(layout)
        return page

    # ---------------------------
    # Helpers
    # ---------------------------
    def _create_vertical_slider(self, initial=50):
        sl = QSlider(Qt.Vertical)
        sl.setRange(0, 100)
        sl.setValue(initial)
        sl.setFixedHeight(180)
        sl.setStyleSheet("""
            QSlider::handle:vertical { background: #1f6feb; height: 16px; border-radius: 6px; }
        """)
        return sl

    def _on_nav(self):
        sender = self.sender()
        if sender:
            idx = sender.property("page_index")
            self.stack.setCurrentIndex(idx)

    def _apply_preset(self, name):
        if name == "Stand":
            vals = {"ARM": 30, "WRIST": 40, "TENTACLE": 10}
        elif name == "Wave":
            vals = {"ARM": 80, "WRIST": 60, "TENTACLE": 10}
        else:  # Relax
            vals = {"ARM": 40, "WRIST": 30, "TENTACLE": 20}
        for k, v in vals.items():
            self._set_motor(k, v)

    def _set_motor(self, key, val):
        val = int(val)
        if key in self.motors:
            self.motors[key] = val
        # Update related UI widgets
        self.circ_arm.setValue(self.motors["ARM"])
        self.circ_wrist.setValue(self.motors["WRIST"])
        self.circ_tent.setValue(self.motors["TENTACLE"])
        # Keep sliders in sync (if update came from program)
        self.s_arm.blockSignals(True); self.s_arm.setValue(self.motors["ARM"]); self.s_arm.blockSignals(False)
        self.s_wrist.blockSignals(True); self.s_wrist.setValue(self.motors["WRIST"]); self.s_wrist.blockSignals(False)
        self.s_tent.blockSignals(True); self.s_tent.setValue(self.motors["TENTACLE"]); self.s_tent.blockSignals(False)
        # Here: send motor commands to hardware (serial / mqtt / etc.)
        # For example:
        # self._send_motor_command(key, val)

    def _open_dial(self, motor_name):
        initial = self.motors.get(motor_name, 50)
        dlg = DialDialog(f"{motor_name} Control", initial=initial, parent=self)
        # Center dialog on screen
        dlg.move(self.geometry().center() - dlg.rect().center())
        if dlg.exec_() == QDialog.Accepted:
            new_val = dlg.get_value()
            self._set_motor(motor_name, new_val)

    # ---------------------------
    # Simulated sensors & timers
    # ---------------------------
    def _setup_timers(self):
        # Battery & connection simulation
        self.batt_val = 100
        self.batt_timer = QTimer(self)
        self.batt_timer.timeout.connect(self._simulate_battery)
        self.batt_timer.start(3000)

        # Sensor updates (IMU, gas, proximity)
        self.sensor_timer = QTimer(self)
        self.sensor_timer.timeout.connect(self._simulate_sensors)
        self.sensor_timer.start(900)

        # Uptime timer
        self.uptime_seconds = 0
        self.uptime_timer = QTimer(self)
        self.uptime_timer.timeout.connect(self._update_uptime)
        self.uptime_timer.start(1000)

        # Connection simulation
        self.conn_state = False
        self.conn_timer = QTimer(self)
        self.conn_timer.timeout.connect(self._toggle_conn)
        self.conn_timer.start(5000)

    def _simulate_battery(self):
        # Decrease slowly for demo, then sometimes recharge
        self.batt_val -= random.choice([0, 0, 1])
        if self.batt_val < 20 and random.random() < 0.28:
            # simulate plugging in to charge
            self.batt_val = min(100, self.batt_val + random.randint(8, 25))
        self.batt_val = max(0, min(100, self.batt_val))
        voltage = 11.0 + (self.batt_val / 100.0) * 1.6  # simulated mapping
        self.batt_label.setText(f"🔋 {self.batt_val}% ({voltage:.2f}V)")
        self.batt_large_label.setText(f"🔋 {self.batt_val}%")
        # TODO: Replace with actual INA219/MAX17043 read and update GUI

    def _simulate_sensors(self):
        # IMU: pitch roll yaw random walk
        p = round(random.uniform(-10.0, 10.0), 1)
        r = round(random.uniform(-6.0, 6.0), 1)
        y = round(random.uniform(-180.0, 180.0), 1)
        self.imu_label.setText(f"Pitch: {p}° | Roll: {r}° | Yaw: {y}°")

        # Proximity: random
        f = random.randint(20, 200)
        l = random.randint(20, 300)
        rr = random.randint(20, 300)
        self.prox_label.setText(f"Front: {f} cm | Left: {l} cm | Right: {rr} cm")

        # Gas and environment
        mq = random.randint(60, 200)
        temp = round(random.uniform(20.0, 36.0), 1)
        hum = random.randint(30, 70)
        self.gas_label.setText(f"Air Quality: { 'OK' if mq<150 else 'ALERT' } (MQ: {mq})")
        self.temp_label.setText(f"Temp: {temp}°C | Humidity: {hum}%")

        # Sensor log append
        if random.random() < 0.07:
            self.sensor_log.setText(f"Event: sensor spike detected (mq={mq})")
        else:
            self.sensor_log.setText("No recent events.")

    def _update_uptime(self):
        self.uptime_seconds += 1
        s = self.uptime_seconds
        h = s // 3600; m = (s % 3600) // 60; sec = s % 60
        self.uptime_label.setText(f"Uptime: {h:02d}:{m:02d}:{sec:02d}")

    def _toggle_conn(self):
        self.conn_state = not self.conn_state
        if self.conn_state:
            ss = random.randint(-70, -40)
            self.conn_label.setText(f"WiFi: connected (RSSI {ss} dBm)")
            self.wifi_entry.setText(f"WiFi: Connected (RSSI {ss} dBm)")
        else:
            self.conn_label.setText("WiFi: disconnected")
            self.wifi_entry.setText("WiFi: Not connected (simulated)")
    
    def _shutdown_robot(self):
        # For demonstration: close the kiosk window
        print("Shutdown initiated... closing kiosk.")
        self.close()
    

    # ---------------------------
    # Keyboard / keypress
    # ---------------------------
    def keyPressEvent(self, event):
        # ESC to close kiosk (for development only)
        if event.key() == Qt.Key_Escape:
            self.close()


# ---------------------------
# Main
# ---------------------------
def main():
    app = QApplication(sys.argv)
    # Optional: hide cursor for kiosk-only touch usage
    # app.setOverrideCursor(Qt.BlankCursor)

    window = RobotKiosk()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
