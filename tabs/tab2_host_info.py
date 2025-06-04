import socket
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QFrame)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

class HostInfoTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = QLabel("Informasi Hostname")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        
        # Description
        description = QLabel(
            "Fitur ini memungkinkan Anda untuk melihat hostname komputer Anda. "
            "Hostname adalah label yang diberikan pada perangkat yang terhubung ke jaringan yang mengidentifikasinya secara unik."
        )
        description.setWordWrap(True)
        description.setFont(QFont("Arial", 12))
        description.setStyleSheet("color: #555;")
        
        # Hostname card
        hostname_card = QFrame()
        hostname_card.setFrameShape(QFrame.StyledPanel)
        hostname_card.setFrameShadow(QFrame.Raised)
        hostname_card.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        hostname_layout = QVBoxLayout()
        
        # Hostname title
        hostname_label = QLabel("Lihat Hostname Lokal")
        hostname_label.setFont(QFont("Arial", 14, QFont.Bold))
        hostname_label.setAlignment(Qt.AlignCenter)
        
        # Show hostname button
        self.get_hostname_btn = QPushButton("Tampilkan Hostname Saya")
        self.get_hostname_btn.setFont(QFont("Arial", 12))
        self.get_hostname_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 12px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.get_hostname_btn.clicked.connect(self.show_hostname)
        
        # Center the button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.get_hostname_btn)
        button_layout.addStretch()
        
        # Hostname result display
        self.hostname_result = QTextEdit()
        self.hostname_result.setReadOnly(True)
        self.hostname_result.setFont(QFont("Arial", 14))
        self.hostname_result.setAlignment(Qt.AlignCenter)
        self.hostname_result.setMinimumHeight(120)
        self.hostname_result.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                margin-top: 20px;
            }
        """)
        self.hostname_result.setPlaceholderText("Hostname Anda akan ditampilkan di sini")
        
        # Add all elements to hostname layout
        hostname_layout.addWidget(hostname_label)
        hostname_layout.addLayout(button_layout)
        hostname_layout.addWidget(self.hostname_result)
        
        hostname_card.setLayout(hostname_layout)
        
        # Information section
        info_card = QFrame()
        info_card.setFrameShape(QFrame.StyledPanel)
        info_card.setFrameShadow(QFrame.Raised)
        info_card.setStyleSheet("""
            QFrame {
                background-color: #e3f2fd;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        info_layout = QVBoxLayout()
        
        info_title = QLabel("Apa itu Hostname?")
        info_title.setFont(QFont("Arial", 14, QFont.Bold))
        
        info_text = QLabel(
            "Hostname adalah label yang diberikan pada perangkat yang terhubung ke jaringan komputer. "
            "Hostname berfungsi sebagai pengidentifikasi yang mudah dibaca oleh manusia untuk perangkat tersebut, "
            "sehingga memudahkan untuk menemukan perangkat tertentu pada jaringan. "
            "Hostname biasanya lebih mudah diingat daripada alamat IP.\n\n"
            "Hostname komputer Anda digunakan oleh protokol jaringan untuk mengidentifikasi perangkat Anda di jaringan lokal."
        )
        info_text.setWordWrap(True)
        info_text.setFont(QFont("Arial", 12))
        
        info_layout.addWidget(info_title)
        info_layout.addWidget(info_text)
        
        info_card.setLayout(info_layout)
        
        # Add all widgets to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(description)
        main_layout.addWidget(hostname_card)
        main_layout.addWidget(info_card)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def show_hostname(self):
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            
            # Display hostname and IP with some styling
            self.hostname_result.setHtml(
                f"<div style='text-align: center;'>"
                f"<p style='font-size: 16px; margin-bottom: 10px;'><b>Hostname Anda:</b></p>"
                f"<p style='font-size: 20px; color: #2196F3; font-weight: bold;'>{hostname}</p>"
                f"<p style='font-size: 14px; margin-top: 10px;'><b>Alamat IP Lokal:</b> {ip_address}</p>"
                f"</div>"
            )
            
            # Apply success styling
            self.hostname_result.setStyleSheet("""
                QTextEdit {
                    background-color: #e8f5e9;
                    border: 1px solid #a5d6a7;
                    border-radius: 5px;
                    padding: 10px;
                    margin-top: 20px;
                }
            """)
            
        except Exception as e:
            self.hostname_result.setHtml(
                f"<div style='text-align: center;'>"
                f"<p style='font-size: 16px; color: #d32f2f;'><b>Error mengambil hostname:</b></p>"
                f"<p style='font-size: 14px;'>{str(e)}</p>"
                f"</div>"
            )
            
            # Apply error styling
            self.hostname_result.setStyleSheet("""
                QTextEdit {
                    background-color: #ffebee;
                    border: 1px solid #ef9a9a;
                    border-radius: 5px;
                    padding: 10px;
                    margin-top: 20px;
                }
            """)
