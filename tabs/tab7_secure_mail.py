import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QLineEdit, QTextEdit, QFrame, 
                              QGroupBox, QMessageBox, QTabWidget, 
                              QCheckBox, QGridLayout, QApplication,
                              QSizePolicy, QSpacerItem)
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtCore import Qt, QThread, Signal

# Default email credentials
DEFAULT_EMAIL = {
    "EMAIL_FROM": "tokotech.ltd@gmail.com",
    "SMTP_HOST": "smtp.gmail.com",
    "SMTP_PORT": "587",
    "SMTP_USER": "tokotech.ltd@gmail.com",
    "SMTP_PASS": "Ganti-Ges-Rahasia-Wkwkw"
}

class EmailSenderThread(QThread):
    """Thread for sending emails without blocking the UI"""
    success = Signal(str)
    error = Signal(str)
    
    def __init__(self, smtp_config, email_data):
        super().__init__()
        self.smtp_config = smtp_config
        self.email_data = email_data
    
    def run(self):
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = self.email_data["subject"]
            message["From"] = self.email_data["from"]
            message["To"] = self.email_data["to"]
            
            # Add email body
            message.attach(MIMEText(self.email_data["body"], "plain"))
            
            # Create secure connection
            context = ssl.create_default_context()
            
            # Connect to server and send email
            with smtplib.SMTP(self.smtp_config["host"], int(self.smtp_config["port"])) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(self.smtp_config["user"], self.smtp_config["password"])
                server.send_message(message)
            
            self.success.emit("Email berhasil dikirim!")
        except Exception as e:
            self.error.emit(f"Error mengirim email: {str(e)}")

class SecureMailTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize attributes
        self.use_default_credentials = True
        self.sender_thread = None
        self.creds_widget = None
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header with icon
        header_layout = QHBoxLayout()
        
        # Email icon
        email_icon = QLabel()
        icon_pixmap = QPixmap("icons/email.png")
        if not icon_pixmap.isNull():
            email_icon.setPixmap(icon_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Fallback if icon not found
            email_icon.setText("📧")
            email_icon.setFont(QFont("Arial", 24))
        
        header_layout.addWidget(email_icon)
        
        # Header text
        header_text = QVBoxLayout()
        title = QLabel("Secure Mail Sender")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        desc = QLabel("Kirim email dengan aman menggunakan SMTP terenkripsi (TLS)")
        desc.setFont(QFont("Arial", 11))
        desc.setStyleSheet("color: #666666;")
        
        header_text.addWidget(title)
        header_text.addWidget(desc)
        header_layout.addLayout(header_text)
        header_layout.addStretch(1)
        
        main_layout.addLayout(header_layout)
        
        # Main content card
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Credentials toggle (simple version initially shown)
        creds_toggle_layout = QHBoxLayout()
        
        self.use_default_check = QCheckBox("Gunakan kredensial default (tokotech.ltd@gmail.com)")
        self.use_default_check.setChecked(True)
        self.use_default_check.toggled.connect(self.toggle_credentials)
        self.use_default_check.setFont(QFont("Arial", 11))
        self.use_default_check.setStyleSheet("""
            QCheckBox {
                color: #2c3e50;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        
        creds_toggle_layout.addWidget(self.use_default_check)
        creds_toggle_layout.addStretch()
        
        content_layout.addLayout(creds_toggle_layout)
        
        # Custom credentials section (initially hidden)
        self.creds_widget = QGroupBox("Kredensial SMTP Kustom")
        self.creds_widget.setStyleSheet("""
            QGroupBox {
                background-color: #f8f9fa;
                border-radius: 6px;
                margin-top: 15px;
                font-weight: bold;
                border: 1px solid #d1d1d1;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2c3e50;
            }
        """)
        
        creds_layout = QGridLayout(self.creds_widget)
        creds_layout.setVerticalSpacing(12)
        creds_layout.setHorizontalSpacing(15)
        creds_layout.setContentsMargins(15, 20, 15, 15)
        
        # SMTP Host
        host_label = QLabel("SMTP Host:")
        host_label.setFont(QFont("Arial", 10))
        self.smtp_host = QLineEdit(DEFAULT_EMAIL["SMTP_HOST"])
        creds_layout.addWidget(host_label, 0, 0)
        creds_layout.addWidget(self.smtp_host, 0, 1)
        
        # SMTP Port
        port_label = QLabel("SMTP Port:")
        port_label.setFont(QFont("Arial", 10))
        self.smtp_port = QLineEdit(DEFAULT_EMAIL["SMTP_PORT"])
        creds_layout.addWidget(port_label, 0, 2)
        creds_layout.addWidget(self.smtp_port, 0, 3)
        
        # SMTP User
        user_label = QLabel("SMTP User:")
        user_label.setFont(QFont("Arial", 10))
        self.smtp_user = QLineEdit(DEFAULT_EMAIL["SMTP_USER"])
        creds_layout.addWidget(user_label, 1, 0)
        creds_layout.addWidget(self.smtp_user, 1, 1)
        
        # SMTP Password
        pass_label = QLabel("SMTP Password:")
        pass_label.setFont(QFont("Arial", 10))
        self.smtp_pass = QLineEdit(DEFAULT_EMAIL["SMTP_PASS"])
        self.smtp_pass.setEchoMode(QLineEdit.Password)
        creds_layout.addWidget(pass_label, 1, 2)
        creds_layout.addWidget(self.smtp_pass, 1, 3)
        
        # Initially hide the credentials widget
        self.creds_widget.setVisible(False)
        content_layout.addWidget(self.creds_widget)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0;")
        content_layout.addWidget(separator)
        
        # Compose Email Section
        compose_layout = QVBoxLayout()
        compose_layout.setSpacing(12)
        
        # Email header section
        email_header = QGridLayout()
        email_header.setVerticalSpacing(12)
        email_header.setHorizontalSpacing(15)
        
        # From field
        from_label = QLabel("Dari:")
        from_label.setFont(QFont("Arial", 10))
        self.from_field = QLineEdit(DEFAULT_EMAIL["EMAIL_FROM"])
        email_header.addWidget(from_label, 0, 0)
        email_header.addWidget(self.from_field, 0, 1)
        
        # Sender name field
        name_label = QLabel("Nama Pengirim:")
        name_label.setFont(QFont("Arial", 10))
        self.sender_name = QLineEdit("Secure Mail")
        email_header.addWidget(name_label, 0, 2)
        email_header.addWidget(self.sender_name, 0, 3)
        
        # To field
        to_label = QLabel("Kepada:")
        to_label.setFont(QFont("Arial", 10))
        self.to_field = QLineEdit()
        self.to_field.setPlaceholderText("contoh: recipient@example.com")
        email_header.addWidget(to_label, 1, 0)
        email_header.addWidget(self.to_field, 1, 1, 1, 3)  # Span across 3 columns
        
        # Subject field
        subject_label = QLabel("Subjek:")
        subject_label.setFont(QFont("Arial", 10))
        self.subject_field = QLineEdit()
        self.subject_field.setPlaceholderText("Subjek email Anda")
        email_header.addWidget(subject_label, 2, 0)
        email_header.addWidget(self.subject_field, 2, 1, 1, 3)  # Span across 3 columns
        
        compose_layout.addLayout(email_header)
        
        # Message body
        body_label = QLabel("Isi Pesan:")
        body_label.setFont(QFont("Arial", 10, QFont.Bold))
        compose_layout.addWidget(body_label)
        
        self.body_field = QTextEdit()
        self.body_field.setMinimumHeight(180)
        self.body_field.setPlaceholderText("Ketik pesan email Anda di sini...")
        compose_layout.addWidget(self.body_field)
        
        # Style all inputs
        input_style = """
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
            QLineEdit:disabled {
                background-color: #f5f5f5;
                color: #999;
            }
        """
        
        for widget in [self.smtp_host, self.smtp_port, self.smtp_user, self.smtp_pass,
                      self.from_field, self.sender_name, self.to_field, self.subject_field]:
            widget.setStyleSheet(input_style)
        
        self.body_field.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 11px;
            }
            QTextEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        
        content_layout.addLayout(compose_layout)
        
        # Send button with container
        btn_container = QHBoxLayout()
        btn_container.addStretch(1)
        
        self.send_btn = QPushButton("Kirim Email")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        self.send_btn.setMinimumWidth(160)
        self.send_btn.clicked.connect(self.send_email)
        
        btn_container.addWidget(self.send_btn)
        btn_container.addStretch(1)
        
        content_layout.addLayout(btn_container)
        main_layout.addWidget(content_frame)
        
        # Status bar
        self.status_bar = QLabel("Siap untuk mengirim email")
        self.status_bar.setFont(QFont("Arial", 10))
        self.status_bar.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px 12px;
                color: #333;
            }
        """)
        
        main_layout.addWidget(self.status_bar)
        
        # Apply global styled to the tab
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #333333;
            }
        """)
        
        self.setLayout(main_layout)
    
    def toggle_credentials(self, use_default):
        """Toggle between default and custom SMTP credentials"""
        self.use_default_credentials = use_default
        
        # Show/hide credential widget - show only when NOT using default
        self.creds_widget.setVisible(not use_default)
        
        # Enable/disable credential fields - enable only when NOT using default
        self.smtp_host.setEnabled(not use_default)
        self.smtp_port.setEnabled(not use_default)
        self.smtp_user.setEnabled(not use_default)
        self.smtp_pass.setEnabled(not use_default)
        
        # Reset to default values if using default
        if use_default:
            self.from_field.setText(DEFAULT_EMAIL["EMAIL_FROM"])
            # This will keep the fields populated but disabled when using default
        else:
            # If switching to custom, make sure the fields are editable
            self.from_field.setEnabled(True)
    
    def validate_inputs(self):
        """Validate all inputs before sending email"""
        # Check SMTP settings
        if not self.smtp_host.text() or not self.smtp_port.text() or not self.smtp_user.text() or not self.smtp_pass.text():
            QMessageBox.warning(self, "Validasi Gagal", "Kredensial SMTP tidak lengkap")
            return False
        
        # Validate port number
        try:
            port = int(self.smtp_port.text())
            if port < 1 or port > 65535:
                QMessageBox.warning(self, "Validasi Gagal", "Port SMTP harus berada di antara 1-65535")
                return False
        except ValueError:
            QMessageBox.warning(self, "Validasi Gagal", "Port SMTP harus berupa angka")
            return False
        
        # Check email data
        if not self.from_field.text():
            QMessageBox.warning(self, "Validasi Gagal", "Alamat email pengirim tidak boleh kosong")
            return False
        
        if not self.to_field.text():
            QMessageBox.warning(self, "Validasi Gagal", "Alamat email penerima tidak boleh kosong")
            return False
        
        # Basic email format validation with @ symbol
        if '@' not in self.from_field.text() or '@' not in self.to_field.text():
            QMessageBox.warning(self, "Validasi Gagal", "Format email tidak valid")
            return False
        
        if not self.subject_field.text():
            QMessageBox.warning(self, "Validasi Gagal", "Subjek email tidak boleh kosong")
            return False
        
        if not self.body_field.toPlainText():
            QMessageBox.warning(self, "Validasi Gagal", "Isi pesan tidak boleh kosong")
            return False
        
        return True
    
    def send_email(self):
        """Send the email with provided information"""
        if not self.validate_inputs():
            return
        
        # Disable the send button to prevent multiple clicks
        self.send_btn.setEnabled(False)
        self.status_bar.setText("Mengirim email...")
        self.status_bar.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                border: 1px solid #ffeeba;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                color: #856404;
            }
        """)
        
        QApplication.processEvents()  # Update UI
        
        # Get SMTP configuration
        smtp_config = {
            "host": self.smtp_host.text(),
            "port": self.smtp_port.text(),
            "user": self.smtp_user.text(),
            "password": self.smtp_pass.text()
        }
        
        # Get email data
        # Format the From header to use "Dari" field as the display part, but SMTP user as the actual email address
        display_email = self.from_field.text().strip()
        smtp_email = smtp_config["user"]
        
        # Use format: "display_email <actual_smtp_email>"
        from_header = f"{display_email} <{smtp_email}>"
        
        # Get sender name and prepare the email body
        sender_name = self.sender_name.text().strip()
        original_body = self.body_field.toPlainText()
        
        # Add sender name to the beginning of the message body
        if sender_name:
            modified_body = f"Dari: {sender_name}\n\n{original_body}"
        else:
            modified_body = original_body
        
        email_data = {
            "from": from_header,
            "to": self.to_field.text(),
            "subject": self.subject_field.text(),
            "body": modified_body
        }
        
        # Create and start a thread for sending the email
        self.sender_thread = EmailSenderThread(smtp_config, email_data)
        self.sender_thread.success.connect(self.on_email_success)
        self.sender_thread.error.connect(self.on_email_error)
        self.sender_thread.finished.connect(lambda: self.send_btn.setEnabled(True))
        self.sender_thread.start()
    
    def on_email_success(self, message):
        """Handle successful email sending"""
        self.status_bar.setText(message)
        self.status_bar.setStyleSheet("""
            QLabel {
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                color: #155724;
            }
        """)
        
        QMessageBox.information(self, "Sukses", message)
        
        # Clear fields after successful send
        self.to_field.clear()
        self.subject_field.clear()
        self.body_field.clear()
    
    def on_email_error(self, error_message):
        """Handle email sending errors"""
        self.status_bar.setText(error_message)
        self.status_bar.setStyleSheet("""
            QLabel {
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                color: #721c24;
            }
        """)
        
        QMessageBox.critical(self, "Error", error_message)
