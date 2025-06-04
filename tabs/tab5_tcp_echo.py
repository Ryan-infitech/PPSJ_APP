import socket
import threading
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTextEdit, QFrame, 
                             QTabWidget, QSpinBox, QMessageBox)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal, QObject, Slot

class TCPSignals(QObject):
    update_server_log = Signal(str)  # Dedicated signal for server logs
    update_client_log = Signal(str)  # Dedicated signal for client logs
    server_status_changed = Signal(bool)
    client_status_changed = Signal(bool)

class TCPEchoTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set up signals
        self.signals = TCPSignals()
        
        # Server variables
        self.server_socket = None
        self.server_running = False
        self.clients = []
        self.client_count = 0
        self.server_message_count = 0  # Counter for server messages
        
        # Client variables
        self.client_socket = None
        self.client_connected = False
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = QLabel("TCP Echo Client/Server")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        
        # Create subtabs
        self.subtabs = QTabWidget()
        
        # Create server tab
        self.server_tab = QWidget()
        self.setup_server_tab()
        
        # Create client tab
        self.client_tab = QWidget()
        self.setup_client_tab()
        
        # Add the subtabs
        self.subtabs.addTab(self.server_tab, "TCP Echo Server")
        self.subtabs.addTab(self.client_tab, "TCP Echo Client")
        
        # Connect signals - Use dedicated signals for each log
        self.signals.update_server_log.connect(self.update_server_log)
        self.signals.update_client_log.connect(self.update_client_log)
        self.signals.server_status_changed.connect(self.update_server_status)
        self.signals.client_status_changed.connect(self.update_client_status)
        
        # Add everything to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(self.subtabs)
        
        self.setLayout(main_layout)
    
    def setup_server_tab(self):
        server_layout = QVBoxLayout()
        self.server_tab.setLayout(server_layout)
        
        # Controls
        controls_frame = QFrame()
        controls_frame.setFrameShape(QFrame.StyledPanel)
        controls_frame.setFrameShadow(QFrame.Raised)
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        controls_layout = QHBoxLayout()
        
        # Port input
        port_label = QLabel("Port:")
        port_label.setFont(QFont("Arial", 12))
        
        self.server_port = QSpinBox()
        self.server_port.setMinimum(1024)
        self.server_port.setMaximum(65535)
        self.server_port.setValue(1234)
        self.server_port.setFont(QFont("Arial", 12))
        
        # Start/Stop button
        self.server_btn = QPushButton("Mulai Server")
        self.server_btn.setFont(QFont("Arial", 12))
        self.server_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.server_btn.clicked.connect(self.toggle_server)
        
        # Clear log button
        self.clear_server_log_btn = QPushButton("Bersihkan Log")
        self.clear_server_log_btn.setFont(QFont("Arial", 12))
        self.clear_server_log_btn.clicked.connect(lambda: self.server_log.clear())
        
        # Add controls to layout
        controls_layout.addWidget(port_label)
        controls_layout.addWidget(self.server_port)
        controls_layout.addStretch()
        controls_layout.addWidget(self.server_btn)
        controls_layout.addWidget(self.clear_server_log_btn)
        
        controls_frame.setLayout(controls_layout)
        
        # Log area
        log_label = QLabel("Log Server:")
        log_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.server_log = QTextEdit()
        self.server_log.setReadOnly(True)
        self.server_log.setFont(QFont("Consolas", 11))
        self.server_log.setMinimumHeight(300)
        self.server_log.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        # Server Message input area (new)
        msg_frame = QFrame()
        msg_frame.setFrameShape(QFrame.StyledPanel)
        msg_frame.setFrameShadow(QFrame.Raised)
        msg_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        msg_layout = QHBoxLayout()
        
        msg_label = QLabel("Pesan Server:")
        msg_label.setFont(QFont("Arial", 12))
        
        self.server_message_input = QLineEdit()
        self.server_message_input.setPlaceholderText("Ketik pesan untuk dikirim ke semua klien...")
        self.server_message_input.setFont(QFont("Arial", 12))
        self.server_message_input.setEnabled(False)
        self.server_message_input.returnPressed.connect(self.broadcast_message)
        
        self.server_send_btn = QPushButton("Kirim ke Semua")
        self.server_send_btn.setFont(QFont("Arial", 12))
        self.server_send_btn.setEnabled(False)
        self.server_send_btn.clicked.connect(self.broadcast_message)
        
        # Add to message layout
        msg_layout.addWidget(msg_label)
        msg_layout.addWidget(self.server_message_input)
        msg_layout.addWidget(self.server_send_btn)
        
        msg_frame.setLayout(msg_layout)
        
        # Status bar
        self.server_status = QLabel("Server: Berhenti")
        self.server_status.setFont(QFont("Arial", 11))
        self.server_status.setStyleSheet("""
            QLabel {
                background-color: #ffcdd2;
                color: #b71c1c;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        # Add everything to server layout
        server_layout.addWidget(controls_frame)
        server_layout.addWidget(log_label)
        server_layout.addWidget(self.server_log)
        server_layout.addWidget(msg_frame)  # Add the new message input area
        server_layout.addWidget(self.server_status)
    
    def setup_client_tab(self):
        client_layout = QVBoxLayout()
        self.client_tab.setLayout(client_layout)
        
        # Connection controls
        conn_frame = QFrame()
        conn_frame.setFrameShape(QFrame.StyledPanel)
        conn_frame.setFrameShadow(QFrame.Raised)
        conn_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        conn_layout = QHBoxLayout()
        
        # Server address
        server_label = QLabel("Server:")
        server_label.setFont(QFont("Arial", 12))
        
        self.server_address = QLineEdit()
        self.server_address.setText("localhost")
        self.server_address.setFont(QFont("Arial", 12))
        
        # Port
        port_label = QLabel("Port:")
        port_label.setFont(QFont("Arial", 12))
        
        self.client_port = QSpinBox()
        self.client_port.setMinimum(1024)
        self.client_port.setMaximum(65535)
        self.client_port.setValue(1234)
        self.client_port.setFont(QFont("Arial", 12))
        
        # Connect button
        self.connect_btn = QPushButton("Hubungkan")
        self.connect_btn.setFont(QFont("Arial", 12))
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 10px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.connect_btn.clicked.connect(self.toggle_connection)
        
        # Add to connection layout
        conn_layout.addWidget(server_label)
        conn_layout.addWidget(self.server_address)
        conn_layout.addWidget(port_label)
        conn_layout.addWidget(self.client_port)
        conn_layout.addWidget(self.connect_btn)
        
        conn_frame.setLayout(conn_layout)
        
        # Log area
        log_label = QLabel("Log Client:")
        log_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.client_log = QTextEdit()
        self.client_log.setReadOnly(True)
        self.client_log.setFont(QFont("Consolas", 11))
        self.client_log.setMinimumHeight(200)
        self.client_log.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        # Message input
        msg_frame = QFrame()
        msg_frame.setFrameShape(QFrame.StyledPanel)
        msg_frame.setFrameShadow(QFrame.Raised)
        msg_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        msg_layout = QHBoxLayout()
        
        msg_label = QLabel("Pesan:")
        msg_label.setFont(QFont("Arial", 12))
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ketik pesan untuk dikirim...")
        self.message_input.setFont(QFont("Arial", 12))
        self.message_input.setEnabled(False)
        self.message_input.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Kirim")
        self.send_btn.setFont(QFont("Arial", 12))
        self.send_btn.setEnabled(False)
        self.send_btn.clicked.connect(self.send_message)
        
        # Add to message layout
        msg_layout.addWidget(msg_label)
        msg_layout.addWidget(self.message_input)
        msg_layout.addWidget(self.send_btn)
        
        msg_frame.setLayout(msg_layout)
        
        # Status bar
        self.client_status = QLabel("Client: Terputus")
        self.client_status.setFont(QFont("Arial", 11))
        self.client_status.setStyleSheet("""
            QLabel {
                background-color: #ffcdd2;
                color: #b71c1c;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        # Add everything to client layout
        client_layout.addWidget(conn_frame)
        client_layout.addWidget(log_label)
        client_layout.addWidget(self.client_log)
        client_layout.addWidget(msg_frame)
        client_layout.addWidget(self.client_status)
    
    @Slot(str)
    def update_server_log(self, message):
        """Update only the server log"""
        self.server_log.append(message)
    
    @Slot(str)
    def update_client_log(self, message):
        """Update only the client log"""
        self.client_log.append(message)
    
    @Slot(bool)
    def update_server_status(self, is_running):
        if is_running:
            self.server_status.setText(f"Server: Berjalan pada port {self.server_port.value()}")
            self.server_status.setStyleSheet("""
                QLabel {
                    background-color: #c8e6c9;
                    color: #2e7d32;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
            self.server_btn.setText("Hentikan Server")
            self.server_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            self.server_port.setEnabled(False)
            # Enable server message controls
            self.server_message_input.setEnabled(True)
            self.server_send_btn.setEnabled(True)
        else:
            self.server_status.setText("Server: Berhenti")
            self.server_status.setStyleSheet("""
                QLabel {
                    background-color: #ffcdd2;
                    color: #b71c1c;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
            self.server_btn.setText("Mulai Server")
            self.server_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.server_port.setEnabled(True)
            # Disable server message controls
            self.server_message_input.setEnabled(False)
            self.server_send_btn.setEnabled(False)
    
    @Slot(bool)
    def update_client_status(self, is_connected):
        if is_connected:
            self.client_status.setText(f"Client: Terhubung ke {self.server_address.text()}:{self.client_port.value()}")
            self.client_status.setStyleSheet("""
                QLabel {
                    background-color: #c8e6c9;
                    color: #2e7d32;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
            self.connect_btn.setText("Putuskan")
            self.connect_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            self.server_address.setEnabled(False)
            self.client_port.setEnabled(False)
            self.message_input.setEnabled(True)
            self.send_btn.setEnabled(True)
            self.message_input.setFocus()
        else:
            self.client_status.setText("Client: Terputus")
            self.client_status.setStyleSheet("""
                QLabel {
                    background-color: #ffcdd2;
                    color: #b71c1c;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
            self.connect_btn.setText("Hubungkan")
            self.connect_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #0b7dda;
                }
            """)
            self.server_address.setEnabled(True)
            self.client_port.setEnabled(True)
            self.message_input.setEnabled(False)
            self.send_btn.setEnabled(False)
    
    def toggle_server(self):
        if not self.server_running:
            self.start_server()
        else:
            self.stop_server()
    
    def start_server(self):
        try:
            port = self.server_port.value()
            
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(5)
            
            self.server_running = True
            self.server_message_count = 0  # Reset message counter
            self.signals.server_status_changed.emit(True)
            self.signals.update_server_log.emit(f"Server dimulai pada port {port}")
            
            # Start thread to accept connections
            threading.Thread(target=self.accept_connections, daemon=True).start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error Server", f"Tidak dapat memulai server: {str(e)}")
            self.signals.update_server_log.emit(f"Error: {str(e)}")
    
    def stop_server(self):
        if self.server_running:
            self.server_running = False
            
            # Close all client connections
            for client in self.clients:
                try:
                    client.close()
                except:
                    pass
            self.clients.clear()
            
            # Close server socket
            if self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass
            
            self.signals.server_status_changed.emit(False)
            self.signals.update_server_log.emit("Server berhenti")
    
    def accept_connections(self):
        self.server_socket.settimeout(1)
        
        while self.server_running:
            try:
                client, addr = self.server_socket.accept()
                self.clients.append(client)
                
                client_id = self.client_count
                self.client_count += 1
                
                threading.Thread(target=self.handle_client, 
                               args=(client, addr, client_id), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.server_running:
                    self.signals.update_server_log.emit(f"Error koneksi: {str(e)}")
    
    def handle_client(self, client, addr, client_id):
        # Use the server_log signal directly - no need for message source tracking
        self.signals.update_server_log.emit(f"Koneksi baru dari Client{client_id} ({addr[0]}:{addr[1]})")
        messages = 0
        
        try:
            while self.server_running:
                client.settimeout(1)
                try:
                    data = client.recv(1024).decode('utf-8')
                    if not data or data == "close":
                        break
                    
                    messages += 1
                    # Log received message to server log only
                    self.signals.update_server_log.emit(f"Pesan dari Client{client_id} ({addr[0]}): \"{data}\"")
                    
                    # Send echo response with the proper format - this will be filtered out by client
                    response = f"Echo {messages}: {data}"
                    client.send(response.encode('utf-8'))
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.server_running:
                        self.signals.update_server_log.emit(f"Error koneksi client{client_id}: {str(e)}")
                    break
            
            # Send summary before disconnecting
            try:
                client.send(f"{messages} pesan diterima.".encode('utf-8'))
            except:
                pass
                
            self.signals.update_server_log.emit(f"Client{client_id} terputus. Total pesan: {messages}")
        finally:
            if client in self.clients:
                self.clients.remove(client)
            client.close()
    
    # New method to broadcast messages from server to all clients
    def broadcast_message(self):
        if not self.server_running or len(self.clients) == 0:
            self.signals.update_server_log.emit("Tidak ada client yang terhubung untuk menerima pesan")
            return
        
        message = self.server_message_input.text().strip()
        if not message:
            return
            
        # Log to server with the message content
        self.signals.update_server_log.emit(f"Server mengirim pesan: {message}")
        
        # Send to all clients - send plain message without Echo prefix
        disconnected_clients = []
        for client in self.clients:
            try:
                client.send(message.encode('utf-8'))
            except:
                disconnected_clients.append(client)
                
        # Remove disconnected clients
        for client in disconnected_clients:
            if client in self.clients:
                self.clients.remove(client)
                
        self.server_message_input.clear()
    
    def toggle_connection(self):
        if not self.client_connected:
            self.connect_to_server()
        else:
            self.disconnect_from_server()
    
    def connect_to_server(self):
        try:
            host = self.server_address.text()
            port = self.client_port.value()
            
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            
            self.client_connected = True
            self.signals.client_status_changed.emit(True)
            self.signals.update_client_log.emit(f"Terhubung ke server pada {host}:{port}")
            
            # Start thread to receive server messages
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error Koneksi", f"Tidak dapat terhubung ke server: {str(e)}")
            self.signals.update_client_log.emit(f"Error koneksi: {str(e)}")
    
    def disconnect_from_server(self):
        if self.client_connected and self.client_socket:
            try:
                # Try to send close message
                self.client_socket.send("close".encode('utf-8'))
                
                # Wait briefly for final message
                try:
                    self.client_socket.settimeout(2)
                    final = self.client_socket.recv(1024).decode('utf-8')
                    self.signals.update_client_log.emit(f"Server: {final}")
                except:
                    pass
            except:
                pass
            
            # Close socket
            self.client_socket.close()
            self.client_socket = None
            self.client_connected = False
            
            self.signals.client_status_changed.emit(False)
            self.signals.update_client_log.emit("Terputus dari server")
    
    def receive_messages(self):
        while self.client_connected:
            try:
                self.client_socket.settimeout(1)
                response = self.client_socket.recv(1024).decode('utf-8')
                if not response:
                    break
                
                # Check if this is an echo of our own message (which we've already logged)
                if response.startswith("Echo ") and ":" in response:
                    # This is our own message echoed back, don't log it again
                    continue
                
                # Format server messages properly (without Echo prefix)
                self.signals.update_client_log.emit(f"Server: {response}")
            except socket.timeout:
                continue
            except Exception as e:
                if self.client_connected:
                    self.signals.update_client_log.emit(f"Error: {str(e)}")
                    self.signals.client_status_changed.emit(False)
                    self.client_connected = False
                break
    
    def send_message(self):
        if not self.client_connected:
            return
        
        message = self.message_input.text().strip()
        if not message:
            return
        
        try:
            self.client_socket.send(message.encode('utf-8'))
            # Log the client's own message with "echo0:" format
            self.signals.update_client_log.emit(f"echo0: {message}")
            self.message_input.clear()
        except Exception as e:
            self.signals.update_client_log.emit(f"Error: {str(e)}")
            self.disconnect_from_server()
