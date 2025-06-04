import sys
import os
import importlib.util
import subprocess
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QStyleFactory,
                              QSplashScreen, QLabel, QGraphicsOpacityEffect, QProgressBar)
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor, QPalette, QLinearGradient, QBrush, QPainter, QScreen
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize, QPoint, QRect, QParallelAnimationGroup


# Import tab modules
from tabs.tab1_info import InfoTab
from tabs.tab2_host_info import HostInfoTab
from tabs.tab3_name_to_ip import NameToIPTab
from tabs.tab4_server_location import ServerLocationTab
from tabs.tab5_tcp_echo import TCPEchoTab
from tabs.tab6_modern_chat import ModernChatTab
from tabs.tab7_secure_mail import SecureMailTab

class AnimatedTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabPosition(QTabWidget.North)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.currentChanged.connect(self.animate_tab_transition)
        self.previous_index = 0
        self.animation_running = False
        self.current_animation = None
        
        # Dictionary to keep track of opacity effects for each widget
        self.opacity_effects = {}
    
    def animate_tab_transition(self, index):
        if self.animation_running:
            return
            
        self.animation_running = True
        current_widget = self.widget(index)
        
        # Clean up any previous effects on other widgets
        for widget, effect in list(self.opacity_effects.items()):
            if widget != current_widget:
                widget.setGraphicsEffect(None)
                del self.opacity_effects[widget]
        
        # Create new opacity effect each time
        effect = QGraphicsOpacityEffect(current_widget)
        self.opacity_effects[current_widget] = effect
        
        # Apply the effect
        current_widget.setGraphicsEffect(effect)
        effect.setOpacity(0)
        
        # Cancel any running animation
        if self.current_animation and self.current_animation.state() == QPropertyAnimation.Running:
            self.current_animation.stop()
        
        # Create the animation
        self.current_animation = QPropertyAnimation(effect, b"opacity")
        self.current_animation.setDuration(500)
        self.current_animation.setStartValue(0)
        self.current_animation.setEndValue(1)
        self.current_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.current_animation.finished.connect(self.on_animation_finished)
        self.current_animation.start()
        
        self.previous_index = index
    
    def on_animation_finished(self):
        self.animation_running = False

class CustomSplashScreen(QSplashScreen):
    def __init__(self):
        # Create a pixmap for the splash screen with a gradient background
        pixmap = QPixmap(600, 400)
        pixmap.fill(Qt.transparent)
        
        # Create a gradient background
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0, QColor(60, 86, 180))
        gradient.setColorAt(1, QColor(30, 30, 90))
        
        # Paint the gradient on the pixmap
        painter = QPainter(pixmap)
        painter.fillRect(pixmap.rect(), QBrush(gradient))
        
        # Add title text
        font = QFont("Segoe UI", 28, QFont.Bold)
        painter.setFont(font)
        painter.setPen(Qt.white)
        painter.drawText(QRect(0, 100, 600, 50), Qt.AlignCenter, "PPSJ Application")
        
        # Add subtitle
        font.setPointSize(14)
        painter.setFont(font)
        painter.drawText(QRect(0, 160, 600, 30), Qt.AlignCenter, "Praktikum Pemrograman Sistem dan Jaringan")
        
        # Finishing
        painter.end()
        
        super().__init__(pixmap)
        
        # Add a progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(100, 300, 400, 20)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("PPSJ Application - Praktikum Pemrograman Sistem dan Jaringan")
        self.setWindowIcon(QIcon("icons/Konoha.ico"))
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        layout = QVBoxLayout(central_widget)
        
        # Create animated tab widget
        self.tabs = AnimatedTabWidget()
        
        # Create tab instances
        self.tab1 = InfoTab()
        self.tab2 = HostInfoTab()
        self.tab3 = NameToIPTab()
        self.tab4 = ServerLocationTab()
        self.tab5 = TCPEchoTab()
        self.tab6 = ModernChatTab()
        self.tab7 = SecureMailTab()
        
        # Add tabs to widget
        self.tabs.addTab(self.tab1, "Informasi")
        self.tabs.addTab(self.tab2, "Hostname")
        self.tabs.addTab(self.tab3, "Host Info")
        self.tabs.addTab(self.tab4, "Server Location")
        self.tabs.addTab(self.tab5, "TCP Echo")
        self.tabs.addTab(self.tab6, "Modern Chat")
        self.tabs.addTab(self.tab7, "Secure Mail")
        
        layout.addWidget(self.tabs)
        
        # Center the window
        self.center()
        
        # Setup animations
        self.setup_window_animations()
    
    def setup_window_animations(self):
        """Set up window animation effects"""
        self.setWindowOpacity(0)
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(800)
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)
        self.opacity_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def showEvent(self, event):
        """Override showEvent to trigger animation"""
        super().showEvent(event)
        if hasattr(self, 'opacity_animation'):
            self.opacity_animation.start()
    
    def center(self):
        """Center the window on the screen"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application-wide font with larger size
    font = QFont("Segoe UI", 16)  # Increased from 14 to 16
    app.setFont(font)
    
    # Set application icon with robust path resolution
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "app_icon.png")
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    
    # Set fusion style with customizations
    app.setStyle("Fusion")
    
    # Set custom palette for modern look with improved colors
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(248, 249, 250))          # Lighter background
    palette.setColor(QPalette.WindowText, QColor(33, 37, 41))         # Darker text for better contrast
    palette.setColor(QPalette.Base, QColor(255, 255, 255))           
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(33, 37, 41))
    palette.setColor(QPalette.Text, QColor(33, 37, 41))
    palette.setColor(QPalette.Button, QColor(248, 249, 250))
    palette.setColor(QPalette.ButtonText, QColor(33, 37, 41))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.Highlight, QColor(52, 152, 219))        # Brighter blue highlight
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Create and show the splash screen
    splash = CustomSplashScreen()
    splash.show()
    
    # Simulate loading
    for i in range(1, 101):
        splash.progress_bar.setValue(i)
        app.processEvents()
        QTimer.singleShot(10, lambda: None)
    
    # Create the main window
    window = MainWindow()
    
    # Close splash and show main window with a small delay
    QTimer.singleShot(500, splash.close)
    QTimer.singleShot(500, window.showMaximized)  # Show maximized instead of normal
    
    sys.exit(app.exec())
