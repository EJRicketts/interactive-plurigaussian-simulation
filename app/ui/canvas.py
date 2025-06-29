from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QImage, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QPoint, QRect
import numpy as np
import sys

class CanvasWidget(QWidget):
    strokeFinished = pyqtSignal(np.ndarray)

    COLORS = [
        QColor(0, 0, 0),        # Phase 0 - Black
        QColor(255, 255, 255),  # Phase 1 - White
        QColor(255, 0, 0),      # Phase 2 - Red
        QColor(0, 255, 0),      # Phase 3 - Green
        QColor(0, 0, 255),      # Phase 4 - Blue
        QColor(255, 255, 0),    # Phase 5 - Yellow
        QColor(0, 255, 255),    # Phase 6 - Cyan
    ]

    def __init__(self, width=100, height=100):
        super().__init__()
        self.image_size = QSize(width, height)
        self.image = QImage(self.image_size, QImage.Format_RGB32)
        self.grid = np.zeros((height, width), dtype=int)
        self.image.fill(self.COLORS[0]) # Initialize with Phase 0 color (black)
        
        self.drawing = False
        self.brush_size = 5
        self.brush_shape = "Circle"
        self.draw_mode = "add"
        self.current_phase = 1
        
        self.target_rect = QRect()
        
        self.setMinimumSize(200, 200)

    def set_brush_size(self, size):
        self.brush_size = size

    def set_brush_shape(self, shape):
        self.brush_shape = shape.lower()

    def set_draw_mode(self, mode):
        self.draw_mode = mode

    def set_phase(self, phase):
        self.current_phase = phase

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        
        widget_rect = self.rect()
        scaled_size = self.image_size.scaled(widget_rect.size(), Qt.KeepAspectRatio)
        
        self.target_rect = QRect(QPoint(0, 0), scaled_size)
        self.target_rect.moveCenter(widget_rect.center())

        painter.drawImage(self.target_rect, self.image, self.image.rect())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.target_rect.contains(event.pos()):
            self.drawing = True
            self.draw_at_pos(event.pos())

    def mouseMoveEvent(self, event):
        if self.drawing and self.target_rect.contains(event.pos()):
            self.draw_at_pos(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            self.strokeFinished.emit(self.grid)

    def map_widget_to_image_coords(self, pos):
        x_rel = pos.x() - self.target_rect.x()
        y_rel = pos.y() - self.target_rect.y()
        
        ix = int(x_rel * self.image.width() / self.target_rect.width())
        iy = int(y_rel * self.image.height() / self.target_rect.height())

        return max(0, min(ix, self.image.width() - 1)), max(0, min(iy, self.image.height() - 1))

    def draw_at_pos(self, pos):
        ix, iy = self.map_widget_to_image_coords(pos)
        
        painter = QPainter(self.image)
        color = self.COLORS[self.current_phase] if self.draw_mode == "add" else self.COLORS[0]
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)

        half_brush = self.brush_size // 2
        start_x = ix - half_brush
        start_y = iy - half_brush
        
        if self.brush_shape == "circle":
            painter.drawEllipse(QPoint(ix, iy), half_brush, half_brush)
        elif self.brush_shape == "triangle":
            points = [
                QPoint(ix, iy - half_brush),
                QPoint(ix - half_brush, iy + half_brush),
                QPoint(ix + half_brush, iy + half_brush),
            ]
            painter.drawPolygon(*points)
        else:
            # Default to circle if an unknown shape is somehow selected
            painter.drawEllipse(QPoint(ix, iy), half_brush, half_brush)

        painter.end()

        # Update grid
        phase_to_set = self.current_phase if self.draw_mode == "add" else 0
        
        # Create a mask for the brush shape
        y_coords, x_coords = np.ogrid[-half_brush:half_brush+1, -half_brush:half_brush+1]
        if self.brush_shape == "circle":
            mask = x_coords**2 + y_coords**2 <= half_brush**2
        elif self.brush_shape == "triangle":
            mask = (y_coords >= x_coords - half_brush) & (y_coords <= half_brush)
        else:
            # Default to circle mask
            mask = x_coords**2 + y_coords**2 <= half_brush**2

        # Apply the mask to the grid
        for r in range(self.brush_size):
            for c in range(self.brush_size):
                if mask[r, c]:
                    ny, nx = start_y + r, start_x + c
                    if 0 <= ny < self.image.height() and 0 <= nx < self.image.width():
                        self.grid[ny, nx] = phase_to_set

        self.update()

    def set_data(self, grid: np.ndarray):
        self.grid = grid
        height, width = grid.shape
        if self.image.size() != QSize(width, height):
            self.image = QImage(width, height, QImage.Format_RGB32)
            self.image_size = QSize(width, height)

        for y in range(height):
            for x in range(width):
                phase = self.grid[y, x]
                self.image.setPixelColor(x, y, self.COLORS[phase % len(self.COLORS)])
        self.update()

    def set_size(self, width, height):
        self.image_size = QSize(width, height)
        self.image = QImage(width, height, QImage.Format_RGB32)
        self.grid = np.zeros((height, width), dtype=int)
        self.image.fill(self.COLORS[0]) # Initialize with Phase 0 color (black)
        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    canvas = CanvasWidget()
    
    def on_stroke_finished(grid):
        print("Stroke finished. Grid shape:", grid.shape)
        print("Number of modified cells:", np.count_nonzero(grid))
        # Create a dummy result grid to test set_data
        result_grid = np.random.randint(0, 6, size=grid.shape)
        # In a real app, this would be a separate widget
        # For this test, we'll just display it on the same canvas after a delay
        # canvas.set_data(result_grid)

    canvas.strokeFinished.connect(on_stroke_finished)
    canvas.show()
    sys.exit(app.exec_())
