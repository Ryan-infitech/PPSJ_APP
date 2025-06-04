from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QFrame, QSizePolicy)
from PySide6.QtGui import QFont, QPixmap, QColor, QPainter, QImage, QPen
from PySide6.QtCore import Qt, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

class InfoTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize network manager first
        self.network_manager = QNetworkAccessManager(self)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Header with title and decorative element
        header_container = QFrame()
        header_container.setObjectName("headerFrame")
        header_container.setStyleSheet("""
            #headerFrame {
                background-color: #3498db;
                border-radius: 12px;
            }
        """)
        header_layout = QVBoxLayout(header_container)
        
        header = QLabel("Praktikum Pemrograman Sistem dan Jaringan")
        header.setFont(QFont("Segoe UI", 26, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: white; margin: 15px;")
        
        subheader = QLabel("Aplikasi Demo Konsep Jaringan")
        subheader.setFont(QFont("Segoe UI", 14))
        subheader.setAlignment(Qt.AlignCenter)
        subheader.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        header_layout.addWidget(header)
        header_layout.addWidget(subheader)
        header_layout.setContentsMargins(20, 30, 20, 30)
        
        # Profile section with enhanced card design
        profile_layout = QHBoxLayout()
        profile_layout.setSpacing(20)
        
        # Profile info with better styling
        info_card = QFrame()
        info_card.setObjectName("profileCard")
        info_card.setStyleSheet("""
            #profileCard {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(25, 25, 25, 25)
        
        # Add "Profile" label at the top
        profile_label = QLabel("Profile Mahasiswa")
        profile_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        profile_label.setStyleSheet("color: #3498db; margin-bottom: 15px;")
        
        # Add profile picture placeholder (circle)
        self.profile_pic = QLabel()
        self.profile_pic.setFixedSize(180, 180)
        self.profile_pic.setObjectName("profilePicture")
        self.profile_pic.setStyleSheet("""
            #profilePicture {
                background-color: transparent;
                border-radius: 90px;
                border: 3px solid #3498db;
            }
        """)
        self.profile_pic.setScaledContents(True)
        self.profile_pic.setAlignment(Qt.AlignCenter)
        
        # Load profile picture from URL
        self.load_profile_picture("https://tokotech.live/_next/image?url=%2Fimages%2FRIANSEPTIAWAN.JPG&w=828&q=75")
        
        name_label = QLabel("Rian Septiawan")
        name_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        
        nim_label = QLabel("NIM: 23076052")
        nim_label.setFont(QFont("Segoe UI", 16))
        nim_label.setAlignment(Qt.AlignCenter)
        
        # Add profile info to layout with better spacing
        info_layout.addWidget(profile_label, 0, Qt.AlignLeft)
        info_layout.addSpacing(10)
        info_layout.addWidget(self.profile_pic, 0, Qt.AlignCenter)
        info_layout.addSpacing(15)
        info_layout.addWidget(name_label, 0, Qt.AlignCenter)
        info_layout.addWidget(nim_label, 0, Qt.AlignCenter)
        info_layout.addStretch()
        
        profile_layout.addWidget(info_card)
        
        # Description section with improved styling
        description_card = QFrame()
        description_card.setObjectName("descriptionCard")
        description_card.setStyleSheet("""
            #descriptionCard {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        desc_layout = QVBoxLayout(description_card)
        desc_layout.setContentsMargins(25, 25, 25, 25)
        
        desc_title = QLabel("Tentang Proyek")
        desc_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        desc_title.setStyleSheet("color: #3498db; margin-bottom: 10px;")
        
        desc_text = QLabel(
            "<p>Proyek ini adalah tugas akhir untuk mata kuliah <b>Praktikum Pemrograman "
            "Sistem dan Jaringan</b>. Aplikasi ini mendemonstrasikan berbagai konsep "
            "jaringan seperti:</p>"
            "<ul>"
            "<li>Konversi nama host ke IP dan sebaliknya</li>"
            "<li>Lookup lokasi server</li>"
            "<li>Implementasi server TCP Echo</li>"
            "<li>Chat modern dengan multithreading</li>"
            "<li>Secure email dengan enkripsi TLS</li>"
            "</ul>"
            "<p>Aplikasi ini dibuat menggunakan <b>PySide6</b> untuk antarmuka pengguna dan "
            "memanfaatkan modul-modul Python untuk fungsionalitas jaringan seperti "
            "socket, threading, dan requests.</p>"
        )
        desc_text.setWordWrap(True)
        desc_text.setFont(QFont("Segoe UI", 12))
        desc_text.setTextFormat(Qt.RichText)
        
        desc_layout.addWidget(desc_title)
        desc_layout.addWidget(desc_text)
        
        profile_layout.addWidget(description_card)
        
        # Add everything to the main layout
        main_layout.addWidget(header_container)
        main_layout.addLayout(profile_layout)
        
        # Footer with app version
        footer = QLabel("Version 1.0.0 • 2025")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #777; margin-top: 10px;")
        
        main_layout.addStretch()
        main_layout.addWidget(footer)
        
        self.setLayout(main_layout)
    
    def load_profile_picture(self, url):
        """Load profile picture from URL using QNetworkAccessManager"""
        request = QNetworkRequest(QUrl(url))
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self.process_image_response(reply))

    def process_image_response(self, reply):
        """Process the image data from the network reply"""
        if reply.error() == QNetworkReply.NoError:
            image_data = reply.readAll()
            image = QImage()
            image.loadFromData(image_data)
            
            if not image.isNull():
                # Create a circular mask for the image
                size = 180
                
                # Create a circular mask
                mask = QImage(size, size, QImage.Format_ARGB32)
                mask.fill(Qt.transparent)
                
                painter = QPainter(mask)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setBrush(Qt.white)
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(0, 0, size, size)
                painter.end()
                
                # Scale the image to fit the mask
                scaled_img = image.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                
                # Center the image to crop it properly
                source_x = max(0, (scaled_img.width() - size) / 2)
                source_y = max(0, (scaled_img.height() - size) / 2)
                
                # Create the result image and apply the mask
                result = QPixmap(size, size)
                result.fill(Qt.transparent)
                
                result_painter = QPainter(result)
                result_painter.setRenderHint(QPainter.Antialiasing)
                result_painter.drawImage(0, 0, mask)
                result_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                result_painter.drawImage(0, 0, scaled_img, source_x, source_y, size, size)
                result_painter.end()
                
                # Set the pixmap to the label
                self.profile_pic.setPixmap(result)
            else:
                # If image fails to load, create a placeholder
                self.create_placeholder_image()
        else:
            # If network error, create a placeholder
            self.create_placeholder_image()
        
        reply.deleteLater()

    def create_placeholder_image(self):
        """Create a placeholder image when the URL fails to load"""
        size = 180
        placeholder = QPixmap(size, size)
        placeholder.fill(Qt.transparent)
        
        painter = QPainter(placeholder)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw circle background
        painter.setBrush(QColor(52, 152, 219))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, size, size)
        
        # Draw user icon
        painter.setPen(QPen(Qt.white, 3))
        painter.setBrush(Qt.white)
        
        # Head
        painter.drawEllipse(size//2 - 25, size//3 - 20, 50, 50)
        
        # Body
        painter.drawEllipse(size//2 - 40, size//2 + 10, 80, 80)
        
        painter.end()
        self.profile_pic.setPixmap(placeholder)
