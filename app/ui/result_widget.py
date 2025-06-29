from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage, QPainter, QColor
from PyQt5.QtCore import Qt, QSize, QRect, QPoint
import numpy as np

class ResultWidget(QWidget):
    COLORS = [
        QColor(0, 0, 0),        # Phase 0 - Black
        QColor(255, 255, 255),  # Phase 1 - White
        QColor(255, 0, 0),      # Phase 2 - Red
        QColor(0, 255, 0),      # Phase 3 - Green
        QColor(0, 0, 255),      # Phase 4 - Blue
        QColor(255, 255, 0),    # Phase 5 - Yellow
    ]

    def __init__(self, width=100, height=100):
        super().__init__()
        self.image_size = QSize(width, height)
        self.image = QImage(self.image_size, QImage.Format_RGB32)
        self.image.fill(Qt.white)
        self.target_rect = QRect()
        self.setMinimumSize(200, 200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        widget_rect = self.rect()
        scaled_size = self.image_size.scaled(widget_rect.size(), Qt.KeepAspectRatio)
        self.target_rect = QRect(QPoint(0, 0), scaled_size)
        self.target_rect.moveCenter(widget_rect.center())
        painter.drawImage(self.target_rect, self.image, self.image.rect())

    def set_data(self, grid: np.ndarray):
        height, width = grid.shape
        if self.image.size() != QSize(width, height):
            self.image = QImage(width, height, QImage.Format_RGB32)
            self.image_size = QSize(width, height)

        for y in range(height):
            for x in range(width):
                phase = grid[y, x]
                self.image.setPixelColor(x, y, self.COLORS[phase % len(self.COLORS)])
        self.update()

    def set_size(self, width, height):
        self.image_size = QSize(width, height)
        self.image = QImage(width, height, QImage.Format_RGB32)
        self.image.fill(self.COLORS[0]) # Initialize with Phase 0 color (black)
        self.update()
