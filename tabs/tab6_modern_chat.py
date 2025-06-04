import socket
import threading
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QLabel, QLineEdit, QPushButton, QTextEdit,
                             QGroupBox, QMessageBox, QGraphicsOpacityEffect,
                             QFrame)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal, QObject, Slot, QPropertyAnimation, QEasingCurve, QTimer, QEvent

class WorkerSignals(QObject):
    """Defines signals available for communication with the GUI thread."""
    message = Signal(str)
    error = Signal(str)
    status = Signal(str)

class ServerThread(threading.Thread):
    def __init__(self, port, signals):
        threading.Thread.__init__(self, daemon=True)
        self.port = port
        self.signals = signals
        self.running = False
        self.server_socket = None
        self.clients = []
        
    def run(self):
        self.signals.message.emit("Opening Port...\n")
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1)
            
            self.running = True
            self.signals.status.emit(f"Server running on port {self.port}")
            self.signals.message.emit(f"Server started on port {self.port}")
            
            while self.running:
                try:
                    client, addr = self.server_socket.accept()
                    self.signals.message.emit(f"New connection from {addr}")
                    
                    client_handler = ClientHandlerThread(client, self, self.signals)
                    self.clients.append(client_handler)
                    client_handler.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.signals.error.emit(f"Accept error: {e}")
                        
        except Exception as e:
            self.signals.error.emit(f"Unable to attach to port: {e}")
        finally:
            if self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass
    
    def stop(self):
        self.running = False
        # Close all client connections
        for client in self.clients[:]:
            self.remove_client(client)
            
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
                
        self.signals.status.emit("Server stopped")
        self.signals.message.emit("Server stopped")
    
    def broadcast(self, message, sender=None):
        """Send message to all connected clients except the sender"""
        for client in self.clients:
            if client != sender:
                client.send(message)
    
    def remove_client(self, client_thread):
        if client_thread in self.clients:
            self.clients.remove(client_thread)
            self.signals.message.emit(f"Client disconnected. Active connections: {len(self.clients)}")

class ClientHandlerThread(threading.Thread):
    def __init__(self, client_socket, server, signals):
        threading.Thread.__init__(self, daemon=True)
        self.client_socket = client_socket
        self.server = server
        self.signals = signals
        self.nickname = "Anonymous"
    
    def run(self):
        try:
            while self.server.running:
                try:
                    data = self.client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                    
                    if data.startswith("NICK:"):
                        self.nickname = data[5:]
                        self.signals.message.emit(f"Client registered: {self.nickname}")
                        continue
                    
                    message = f"{self.nickname}: {data}"
                    self.signals.message.emit(f"Received: {message}")
                    self.server.broadcast(message, self)
                except socket.timeout:
                    continue
                    
        except Exception as e:
            self.signals.error.emit(f"Error handling client: {e}")
        finally:
            self.client_socket.close()
            self.server.remove_client(self)
            if self.server.running:
                self.server.broadcast(f"{self.nickname} has left the chat.")
    
    def send(self, message):
        try:
            self.client_socket.sendall(message.encode('utf-8'))
        except:
            self.client_socket.close()
            self.server.remove_client(self)

class ClientThread(threading.Thread):
    def __init__(self, host, port, nickname, signals):
        threading.Thread.__init__(self, daemon=True)
        self.host = host
        self.port = port
        self.nickname = nickname
        self.signals = signals
        self.client_socket = None
        self.running = False
    
    def run(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            
            self.running = True
            self.signals.status.emit(f"Connected to {self.host}:{self.port}")
            self.signals.message.emit("Connected to server!")
            
            # Send nickname to server
            self.client_socket.sendall(f"NICK:{self.nickname}".encode('utf-8'))
            
            # Receive messages
            while self.running:
                try:
                    data = self.client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                    self.signals.message.emit(data)
                except socket.timeout:
                    continue
                        
        except Exception as e:
            self.signals.error.emit(f"Could not connect to server: {e}")
        finally:
            if self.client_socket:
                try:
                    self.client_socket.close()
                except:
                    pass
            self.running = False
            self.signals.status.emit("Disconnected")
    
    def send_message(self, message):
        if not self.running or not self.client_socket:
            return False
        
        try:
            self.client_socket.sendall(message.encode('utf-8'))
            return True
        except:
            self.stop()
            return False
    
    def stop(self):
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        self.signals.status.emit("Disconnected")

class ModernChatTab(QWidget):
    def __init__(self):
        super().__init__()
        
        self.server_thread = None
        self.client_thread = None
        self.current_animation = None
        self.chat_effect = None
        
        self.init_ui()
        
        # Create a single reusable effect and animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(800)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Start animation when widget is shown
        QTimer.singleShot(100, self.animation.start)
        
        # Install event filter to handle widget show/hide events
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        if obj == self and event.type() == QEvent.Show:
            # Reset and start the animation when the widget is shown
            if self.opacity_effect and not self.animation.state():
                self.animation.start()
        return super().eventFilter(obj, event)
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("Chat Modern Client/Server")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        
        # Create tab widget with modern style
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: #ffffff;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                border-bottom-color: #ddd;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 100px;
                padding: 8px 15px;
                font-weight: bold;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom-color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }
        """)
        
        # Create Server Tab
        self.server_tab = QWidget()
        self.init_server_tab()
        self.tab_widget.addTab(self.server_tab, "Server")
        
        # Create Client Tab
        self.client_tab = QWidget()
        self.init_client_tab()
        self.tab_widget.addTab(self.client_tab, "Client")
        
        layout.addWidget(header)
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def init_server_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Server configuration
        config_box = QGroupBox("Konfigurasi Server")
        config_box.setStyleSheet("""
            QGroupBox {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2c3e50;
            }
        """)
        
        config_layout = QHBoxLayout()
        config_layout.setContentsMargins(15, 20, 15, 15)
        
        config_layout.addWidget(QLabel("Port:"))
        self.server_port = QLineEdit("1234")
        self.server_port.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        config_layout.addWidget(self.server_port)
        
        self.server_button = QPushButton("Mulai Server")
        self.server_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        self.server_button.clicked.connect(self.toggle_server)
        config_layout.addWidget(self.server_button)
        
        # Add a button for creating additional client tabs
        self.add_client_tab_button = QPushButton("Tambah Client Tab")
        self.add_client_tab_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)
        self.add_client_tab_button.clicked.connect(self.add_client_tab)
        config_layout.addWidget(self.add_client_tab_button)
        
        config_box.setLayout(config_layout)
        layout.addWidget(config_box)
        
        # Server log
        log_box = QGroupBox("Log Server")
        log_box.setStyleSheet("""
            QGroupBox {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2c3e50;
            }
        """)
        
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(15, 20, 15, 15)
        
        self.server_log = QTextEdit()
        self.server_log.setReadOnly(True)
        self.server_log.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #ffffff;
                padding: 10px;
                font-family: 'Consolas', monospace;
            }
        """)
        log_layout.addWidget(self.server_log)
        
        log_box.setLayout(log_layout)
        layout.addWidget(log_box)
        
        # Status bar
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #f1f1f1;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        status_label = QLabel("Status:")
        status_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        
        self.server_status = QLabel("Server tidak berjalan")
        self.server_status.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-weight: bold;
            }
        """)
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.server_status)
        status_layout.addStretch()
        
        status_frame.setLayout(status_layout)
        layout.addWidget(status_frame)
        
        self.server_tab.setLayout(layout)
    
    def init_client_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Client configuration
        config_box = QGroupBox("Konfigurasi Client")
        config_box.setStyleSheet("""
            QGroupBox {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2c3e50;
            }
        """)
        
        config_layout = QVBoxLayout()
        config_layout.setContentsMargins(15, 20, 15, 15)
        
        server_layout = QHBoxLayout()
        server_layout.setSpacing(10)
        
        server_layout.addWidget(QLabel("Server:"))
        self.client_server = QLineEdit("localhost")
        self.client_server.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        server_layout.addWidget(self.client_server)
        
        server_layout.addWidget(QLabel("Port:"))
        self.client_port = QLineEdit("1234")
        self.client_port.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        server_layout.addWidget(self.client_port)
        
        server_layout.addWidget(QLabel("Nama Pengguna:"))
        self.client_nickname = QLineEdit()
        self.client_nickname.setPlaceholderText("Masukkan nama pengguna Anda")
        self.client_nickname.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        server_layout.addWidget(self.client_nickname)
        
        config_layout.addLayout(server_layout)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.client_connect_button = QPushButton("Hubungkan")
        self.client_connect_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        self.client_connect_button.clicked.connect(self.toggle_client)
        buttons_layout.addWidget(self.client_connect_button)
        buttons_layout.addStretch()
        
        config_layout.addLayout(buttons_layout)
        config_box.setLayout(config_layout)
        layout.addWidget(config_box)
        
        # Chat area
        chat_box = QGroupBox("Chat")
        chat_box.setStyleSheet("""
            QGroupBox {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2c3e50;
            }
        """)
        
        chat_layout = QVBoxLayout()
        chat_layout.setContentsMargins(15, 20, 15, 15)
        
        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        self.chat_log.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #ffffff;
                padding: 10px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        chat_layout.addWidget(self.chat_log)
        
        message_layout = QHBoxLayout()
        message_layout.setSpacing(10)
        
        message_layout.addWidget(QLabel("Pesan:"))
        self.client_message = QLineEdit()
        self.client_message.setPlaceholderText("Ketik pesan Anda di sini...")
        self.client_message.returnPressed.connect(self.send_client_message)
        self.client_message.setEnabled(False)
        self.client_message.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
            QLineEdit:disabled {
                background-color: #f5f5f5;
                color: #999;
            }
        """)
        message_layout.addWidget(self.client_message)
        
        self.send_button = QPushButton("Kirim")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #999;
            }
        """)
        self.send_button.clicked.connect(self.send_client_message)
        self.send_button.setEnabled(False)
        message_layout.addWidget(self.send_button)
        
        chat_layout.addLayout(message_layout)
        chat_box.setLayout(chat_layout)
        layout.addWidget(chat_box)
        
        # Status bar
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #f1f1f1;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        status_label = QLabel("Status:")
        status_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        
        self.client_status = QLabel("Terputus")
        self.client_status.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-weight: bold;
            }
        """)
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.client_status)
        status_layout.addStretch()
        
        status_frame.setLayout(status_layout)
        layout.addWidget(status_frame)
        
        self.client_tab.setLayout(layout)
    
    def toggle_server(self):
        if self.server_thread and self.server_thread.running:
            self.stop_server()
        else:
            self.start_server()
    
    def start_server(self):
        try:
            port = int(self.server_port.text())
            
            # Set up signals for communication
            signals = WorkerSignals()
            signals.message.connect(self.add_server_log)
            signals.error.connect(self.show_server_error)
            signals.status.connect(self.update_server_status)
            
            self.server_thread = ServerThread(port, signals)
            self.server_thread.start()
            
            self.server_button.setText("Hentikan Server")
            
        except ValueError:
            QMessageBox.warning(self, "Port Tidak Valid", "Silakan masukkan nomor port yang valid.")
        except Exception as e:
            QMessageBox.critical(self, "Error Server", f"Error memulai server: {e}")
    
    def stop_server(self):
        if self.server_thread:
            self.server_thread.stop()
            self.server_button.setText("Mulai Server")
    
    def add_server_log(self, message):
        self.server_log.append(message)
    
    def show_server_error(self, error):
        self.server_log.append(f"ERROR: {error}")
        QMessageBox.warning(self, "Error Server", error)
    
    def update_server_status(self, status):
        self.server_status.setText(status)
        if "running" in status.lower():
            self.server_status.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.server_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def toggle_client(self):
        if self.client_thread and self.client_thread.running:
            self.disconnect_client()
        else:
            self.connect_client()
    
    def connect_client(self):
        try:
            host = self.client_server.text()
            port = int(self.client_port.text())
            nickname = self.client_nickname.text() or "Anonymous"
            
            # Set up signals for communication
            signals = WorkerSignals()
            signals.message.connect(self.add_chat_message)
            signals.error.connect(self.show_client_error)
            signals.status.connect(self.update_client_status)
            
            self.client_thread = ClientThread(host, port, nickname, signals)
            self.client_thread.start()
            
            self.client_connect_button.setText("Putuskan")
            self.client_message.setEnabled(True)
            self.send_button.setEnabled(True)
            
            # Display own nickname
            self.add_chat_message(f"Terhubung sebagai: {nickname}")
            
        except ValueError:
            QMessageBox.warning(self, "Port Error", "Please enter a valid port number.")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Error connecting: {e}")
    
    def disconnect_client(self):
        if self.client_thread:
            self.client_thread.stop()
            self.client_connect_button.setText("Hubungkan")
            self.client_message.setEnabled(False)
            self.send_button.setEnabled(False)
    
    def add_chat_message(self, message):
        self.chat_log.append(message)
        
        # Create a flash animation with a timer instead of using opacity effect
        original_style = self.chat_log.styleSheet()
        highlight_style = """
            QTextEdit {
                background-color: #e6f7ff;
                border: 1px solid #91d5ff;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Segoe UI', sans-serif;
            }
        """
        
        self.chat_log.setStyleSheet(highlight_style)
        # Restore original style after a short delay
        QTimer.singleShot(300, lambda: self.chat_log.setStyleSheet(original_style))
    
    def show_client_error(self, error):
        self.chat_log.append(f"ERROR: {error}")
        QMessageBox.warning(self, "Error Client", error)
    
    def update_client_status(self, status):
        self.client_status.setText(status)
        if "connected" in status.lower() or "terhubung" in status.lower():
            self.client_status.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.client_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def send_client_message(self):
        if not self.client_thread or not self.client_thread.running:
            QMessageBox.warning(self, "Not Connected", "Please connect to server first.")
            return
        
        message = self.client_message.text().strip()
        if not message:
            return
        
        nickname = self.client_nickname.text() or "Anonymous"
        success = self.client_thread.send_message(message)
        
        if success:
            # Display the user's own message in their chat log
            self.add_chat_message(f"You: {message}")
            
            # Clear input and add flash effect
            self.client_message.clear()
            
            # Add a visual flash effect for feedback
            orig_style = self.client_message.styleSheet()
            flash_style = "QLineEdit { background-color: #e6f7ff; border: 1px solid #91d5ff; padding: 8px; }"
            self.client_message.setStyleSheet(flash_style)
            QTimer.singleShot(300, lambda: self.client_message.setStyleSheet(orig_style))
        else:
            QMessageBox.critical(self, "Send Error", "Failed to send message.")

    def add_client_tab(self):
        """Add a new client tab identical to the original client tab"""
        # Generate a unique tab name
        tab_count = self.tab_widget.count()
        tab_name = f"Client {tab_count - 1}"  # Subtract 1 to account for server tab
        
        # Create a new client tab
        new_client_tab = QWidget()
        
        # Set up the client tab layout
        client_layout = QVBoxLayout()
        client_layout.setSpacing(15)
        
        # Client configuration section - identical to the original client tab
        config_box = QGroupBox("Konfigurasi Client")
        config_box.setStyleSheet("""
            QGroupBox {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2c3e50;
            }
        """)
        
        config_layout = QVBoxLayout()
        config_layout.setContentsMargins(15, 20, 15, 15)
        
        server_layout = QHBoxLayout()
        server_layout.setSpacing(10)
        
        server_layout.addWidget(QLabel("Server:"))
        client_server = QLineEdit("localhost")
        client_server.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        server_layout.addWidget(client_server)
        
        server_layout.addWidget(QLabel("Port:"))
        client_port = QLineEdit("1234")
        client_port.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        server_layout.addWidget(client_port)
        
        server_layout.addWidget(QLabel("Nama Pengguna:"))
        client_nickname = QLineEdit()
        client_nickname.setPlaceholderText("Masukkan nama pengguna Anda")
        client_nickname.setText(tab_name)  # Set default nickname to tab name
        client_nickname.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        server_layout.addWidget(client_nickname)
        
        config_layout.addLayout(server_layout)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        client_connect_button = QPushButton("Hubungkan")
        client_connect_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        buttons_layout.addWidget(client_connect_button)
        
        # Add a close tab button
        close_tab_button = QPushButton("Tutup Tab")
        close_tab_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        buttons_layout.addWidget(close_tab_button)
        buttons_layout.addStretch()
        
        config_layout.addLayout(buttons_layout)
        config_box.setLayout(config_layout)
        client_layout.addWidget(config_box)
        
        # Chat area - identical to the original client tab
        chat_box = QGroupBox("Chat")
        chat_box.setStyleSheet("""
            QGroupBox {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2c3e50;
            }
        """)
        
        chat_layout = QVBoxLayout()
        chat_layout.setContentsMargins(15, 20, 15, 15)
        
        chat_log = QTextEdit()
        chat_log.setReadOnly(True)
        chat_log.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #ffffff;
                padding: 10px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        chat_layout.addWidget(chat_log)
        
        message_layout = QHBoxLayout()
        message_layout.setSpacing(10)
        
        message_layout.addWidget(QLabel("Pesan:"))
        client_message = QLineEdit()
        client_message.setPlaceholderText("Ketik pesan Anda di sini...")
        client_message.setEnabled(False)
        client_message.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: #f5f5f5;
                color: #999;
            }
            QLineEdit:enabled {
                background-color: white;
                color: black;
            }
        """)
        message_layout.addWidget(client_message)
        
        send_button = QPushButton("Kirim")
        send_button.setEnabled(False)
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #ccc;
                color: #999;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:enabled {
                background-color: #3498db;
                color: white;
            }
            QPushButton:enabled:hover {
                background-color: #2980b9;
            }
        """)
        message_layout.addWidget(send_button)
        
        chat_layout.addLayout(message_layout)
        chat_box.setLayout(chat_layout)
        client_layout.addWidget(chat_box)
        
        # Status bar - identical to the original client tab
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #f1f1f1;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        status_label = QLabel("Status:")
        status_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        
        client_status = QLabel("Terputus")
        client_status.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-weight: bold;
            }
        """)
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(client_status)
        status_layout.addStretch()
        
        status_frame.setLayout(status_layout)
        client_layout.addWidget(status_frame)
        
        # Set the tab's layout
        new_client_tab.setLayout(client_layout)
        
        # Add the tab to the tab widget
        self.tab_widget.addTab(new_client_tab, tab_name)
        
        # Keep track of client threads for each tab
        if not hasattr(self, 'client_threads'):
            self.client_threads = {0: self.client_thread}  # Add the original client tab
        
        # Add this new tab to the client_threads dictionary
        tab_index = self.tab_widget.count() - 1
        self.client_threads[tab_index] = None
        
        # Switch to the new tab
        self.tab_widget.setCurrentIndex(tab_index)
        
        # Set up client connection functionality
        def toggle_client_connection():
            if hasattr(self, 'client_threads') and tab_index in self.client_threads and self.client_threads[tab_index] and self.client_threads[tab_index].running:
                # Disconnect logic
                if self.client_threads[tab_index]:
                    self.client_threads[tab_index].stop()
                    self.client_threads[tab_index] = None
                
                client_connect_button.setText("Hubungkan")
                client_connect_button.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: bold;
                        min-width: 120px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                client_message.setEnabled(False)
                send_button.setEnabled(False)
                client_status.setText("Terputus")
                client_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
                chat_log.append("Terputus dari server.")
            else:
                # Connect logic
                try:
                    host = client_server.text().strip()
                    port = int(client_port.text().strip())
                    nickname = client_nickname.text().strip() or tab_name
                    
                    # Set up signals for this client
                    signals = WorkerSignals()
                    
                    def update_chat(msg):
                        chat_log.append(msg)
                        # Flash effect
                        original_style = chat_log.styleSheet()
                        highlight_style = """
                            QTextEdit {
                                background-color: #e6f7ff;
                                border: 1px solid #91d5ff;
                                border-radius: 4px;
                                padding: 10px;
                                font-family: 'Segoe UI', sans-serif;
                            }
                        """
                        chat_log.setStyleSheet(highlight_style)
                        QTimer.singleShot(300, lambda: chat_log.setStyleSheet(original_style))
                    
                    def update_status(status):
                        client_status.setText(status)
                        if "Connected" in status or "Terhubung" in status:
                            client_status.setStyleSheet("color: #27ae60; font-weight: bold;")
                        else:
                            client_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
                    
                    def show_error(error):
                        chat_log.append(f"ERROR: {error}")
                        QMessageBox.warning(self, f"Error {tab_name}", error)
                    
                    signals.message.connect(update_chat)
                    signals.error.connect(show_error)
                    signals.status.connect(update_status)
                    
                    # Create and start thread
                    client_thread = ClientThread(host, port, nickname, signals)
                    self.client_threads[tab_index] = client_thread
                    client_thread.start()
                    
                    # Update UI
                    client_connect_button.setText("Putuskan")
                    client_connect_button.setStyleSheet("""
                        QPushButton {
                            background-color: #e74c3c;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            padding: 8px 16px;
                            font-weight: bold;
                            min-width: 120px;
                        }
                        QPushButton:hover {
                            background-color: #c0392b;
                        }
                    """)
                    client_message.setEnabled(True)
                    send_button.setEnabled(True)
                    client_message.setFocus()
                    
                    chat_log.append(f"Terhubung sebagai: {nickname}")
                    
                except ValueError:
                    QMessageBox.warning(self, "Port Tidak Valid", "Silakan masukkan nomor port yang valid.")
                except Exception as e:
                    QMessageBox.critical(self, "Error Koneksi", f"Error menghubungkan ke server: {e}")
        
        def send_client_message():
            if not hasattr(self, 'client_threads') or tab_index not in self.client_threads or not self.client_threads[tab_index] or not self.client_threads[tab_index].running:
                return
                
            message = client_message.text().strip()
            if not message:
                return
                
            nickname = client_nickname.text().strip() or tab_name
            success = self.client_threads[tab_index].send_message(message)
            
            if success:
                # Display the user's own message in their chat log
                chat_log.append(f"You: {message}")
                
                # Clear input and add flash effect
                client_message.clear()
                
                # Flash effect
                orig_style = client_message.styleSheet()
                flash_style = "QLineEdit { background-color: #e6f7ff; border: 1px solid #91d5ff; padding: 8px; }"
                client_message.setStyleSheet(flash_style)
                QTimer.singleShot(300, lambda: client_message.setStyleSheet(orig_style))
            else:
                QMessageBox.warning(self, "Error Pengiriman", "Tidak dapat mengirim pesan ke server.")
                toggle_client_connection()  # Disconnect on error
    
        def close_tab():
            # Disconnect if connected
            if hasattr(self, 'client_threads') and tab_index in self.client_threads and self.client_threads[tab_index] and self.client_threads[tab_index].running:
                self.client_threads[tab_index].stop()
            
            # Remove tab and clean up references
            self.tab_widget.removeTab(tab_index)
            if hasattr(self, 'client_threads') and tab_index in self.client_threads:
                del self.client_threads[tab_index]
        
        # Connect the signals
        client_connect_button.clicked.connect(toggle_client_connection)
        send_button.clicked.connect(send_client_message)
        client_message.returnPressed.connect(send_client_message)
        close_tab_button.clicked.connect(close_tab)
        
        return new_client_tab
