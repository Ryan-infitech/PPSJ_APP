import socket
import requests
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTextEdit, QFrame, 
                             QMessageBox, QApplication)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

class ServerLocationTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = QLabel("Pencari Lokasi Server")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        
        # Description
        description = QLabel(
            "Masukkan hostname atau nama domain untuk menemukan alamat IP dan lokasi geografisnya."
        )
        description.setWordWrap(True)
        description.setFont(QFont("Arial", 12))
        description.setStyleSheet("color: #555;")
        description.setAlignment(Qt.AlignCenter)
        
        # Input section
        input_card = QFrame()
        input_card.setFrameShape(QFrame.StyledPanel)
        input_card.setFrameShadow(QFrame.Raised)
        input_card.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        input_layout = QVBoxLayout()
        
        # Host input
        host_layout = QHBoxLayout()
        host_label = QLabel("Masukkan Hostname:")
        host_label.setFont(QFont("Arial", 12))
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("contoh: google.com")
        self.host_input.setFont(QFont("Arial", 12))
        
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_input)
        
        # Find button
        self.find_btn = QPushButton("Cari Lokasi")
        self.find_btn.setFont(QFont("Arial", 12))
        self.find_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        self.find_btn.clicked.connect(self.find_location)
        
        # Result area
        result_label = QLabel("Hasil:")
        result_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Arial", 12))
        self.result_text.setMinimumHeight(200)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        # Add everything to input layout
        input_layout.addLayout(host_layout)
        input_layout.addWidget(self.find_btn)
        input_layout.addWidget(result_label)
        input_layout.addWidget(self.result_text)
        
        input_card.setLayout(input_layout)
        
        # Add everything to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(description)
        main_layout.addWidget(input_card)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def get_ip_address(self, host):
        try:
            ip_address = socket.gethostbyname(host)
            return ip_address
        except socket.gaierror:
            return None
    
    def get_location(self, ip_address):
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5)
            QApplication.restoreOverrideCursor()
            
            data = response.json()
            
            if data["status"] == "success":
                city = data.get("city", "Tidak diketahui")
                region = data.get("regionName", "Tidak diketahui")
                country = data.get("country", "Tidak diketahui")
                isp = data.get("isp", "Tidak diketahui")
                lat = data.get("lat", "Tidak diketahui")
                lon = data.get("lon", "Tidak diketahui")
                
                return {
                    "city": city,
                    "region": region,
                    "country": country,
                    "isp": isp,
                    "lat": lat,
                    "lon": lon
                }
            else:
                return None
        except Exception as e:
            QApplication.restoreOverrideCursor()
            return None
    
    def find_location(self):
        host = self.host_input.text().strip()
        
        if not host:
            QMessageBox.warning(self, "Error Input", "Silakan masukkan hostname.")
            return
        
        # Get IP address
        ip_address = self.get_ip_address(host)
        if not ip_address:
            self.result_text.setHtml(f"<p><b>Error:</b> Tidak dapat menemukan alamat IP untuk host: {host}</p>")
            return
        
        # Get location data
        location_data = self.get_location(ip_address)
        
        if location_data:
            result = f"""
            <h3>Hasil untuk: {host}</h3>
            <p><b>Alamat IP:</b> {ip_address}</p>
            <p><b>Kota:</b> {location_data['city']}</p>
            <p><b>Wilayah:</b> {location_data['region']}</p>
            <p><b>Negara:</b> {location_data['country']}</p>
            <p><b>ISP:</b> {location_data['isp']}</p>
            <p><b>Koordinat:</b> {location_data['lat']}, {location_data['lon']}</p>
            """
            self.result_text.setHtml(result)
        else:
            self.result_text.setHtml(f"<p><b>Error:</b> Tidak dapat menentukan lokasi untuk IP: {ip_address}</p>")
