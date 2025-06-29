from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QImage, QPainter, QColor, QPen, QPolygon
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QPoint, QRect
import numpy as np
import math


class CanvasWidget(QWidget):
    strokeFinished = pyqtSignal(np.ndarray)

    COLORS = [
        QColor(0, 0, 0),  # Phase 0 - Black
        QColor(255, 255, 255),  # Phase 1 - White
        QColor(255, 0, 0),  # Phase 2 - Red
        QColor(0, 255, 0),  # Phase 3 - Green
        QColor(0, 0, 255),  # Phase 4 - Blue
        QColor(255, 255, 0),  # Phase 5 - Yellow
        QColor(0, 255, 255),  # Phase 6 - Cyan
    ]

    def __init__(self, width=250, height=250):
        super().__init__()
        self.image_size = QSize(width, height)
        self.image = QImage(self.image_size, QImage.Format_RGB32)
        self.grid = np.zeros((height, width), dtype=int)
        self.image.fill(self.COLORS[0])  # Initialize with Phase 0 color (black)

        self.drawing = False
        self.brush_size = 5
        self.brush_shape = "Circle"
        self.current_tool = "brush"
        self.current_phase = 1

        # Undo/Redo system
        self.history = [self.grid.copy()]  # Start with initial state
        self.history_index = 0
        self.max_history = 20  # Limit history to prevent memory issues

        self.target_rect = QRect()

        self.setMinimumSize(200, 200)
        self.setFocusPolicy(Qt.StrongFocus)  # Enable keyboard focus
        self.setMouseTracking(True)  # Enable mouse tracking for preview

        # Brush preview
        self.mouse_pos = QPoint(-1, -1)  # Track mouse position
        self.show_preview = False

    def set_brush_size(self, size):
        self.brush_size = size

    def set_brush_shape(self, shape):
        self.brush_shape = shape.lower()

    def set_tool(self, tool_name):
        self.current_tool = tool_name

    def set_phase(self, phase):
        self.current_phase = phase

    def save_state(self):
        """Save current grid state to history after an action is completed"""
        # Remove any states after current index (when user made changes after undo)
        self.history = self.history[: self.history_index + 1]

        # Add the new state (current grid after the action)
        self.history.append(self.grid.copy())
        self.history_index = len(self.history) - 1

        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_index -= 1

    def undo(self):
        """Undo last operation"""
        if self.history_index > 0:
            self.history_index -= 1
            self.grid = self.history[self.history_index].copy()
            self.set_data(self.grid)
            return True
        return False

    def redo(self):
        """Redo last undone operation"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.grid = self.history[self.history_index].copy()
            self.set_data(self.grid)
            return True
        return False

    def can_undo(self):
        """Check if undo is possible"""
        return self.history_index > 0

    def can_redo(self):
        """Check if redo is possible"""
        return self.history_index < len(self.history) - 1

    def _create_triangle_polygon(self, center_x, center_y, half_brush):
        """Create equilateral triangle polygon centered at given coordinates"""
        height = int(half_brush * math.sqrt(3))
        points = [
            QPoint(center_x, center_y - height // 2),  # Top vertex
            QPoint(center_x - half_brush, center_y + height // 2),  # Bottom left
            QPoint(center_x + half_brush, center_y + height // 2),  # Bottom right
        ]
        return QPolygon(points)

    def _create_triangle_mask(self, x_coords, y_coords, half_brush):
        """Create equilateral triangle mask for brush operations"""
        height = int(half_brush * math.sqrt(3))
        # Triangle with apex at top, base at bottom
        return (y_coords >= abs(x_coords) * math.sqrt(3) - height // 2) & (
            y_coords <= height // 2
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        widget_rect = self.rect()
        scaled_size = self.image_size.scaled(widget_rect.size(), Qt.KeepAspectRatio)

        self.target_rect = QRect(QPoint(0, 0), scaled_size)
        self.target_rect.moveCenter(widget_rect.center())

        painter.drawImage(self.target_rect, self.image, self.image.rect())

        # Draw brush preview
        if self.show_preview and self.current_tool == "brush" and not self.drawing:
            self.draw_brush_preview(painter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.target_rect.contains(event.pos()):
            ix, iy = self.map_widget_to_image_coords(event.pos())
            if self.current_tool == "fill":
                self._flood_fill(iy, ix, self.grid[iy, ix], self.current_phase)
                # Save state after fill operation is complete
                self.save_state()
                self.strokeFinished.emit(self.grid)
            elif self.current_tool == "brush":
                self.drawing = True
                self.draw_at_pos(event.pos())

    def mouseMoveEvent(self, event):
        # Update mouse position for brush preview
        if self.target_rect.contains(event.pos()):
            self.mouse_pos = event.pos()
            self.show_preview = True
            if self.drawing:
                self.draw_at_pos(event.pos())
        else:
            self.show_preview = False
        self.update()  # Trigger repaint for preview

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            # Save state after brush stroke is complete
            self.save_state()
            self.strokeFinished.emit(self.grid)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for undo/redo"""
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Z:
                if self.undo():
                    self.strokeFinished.emit(self.grid)
                event.accept()
                return
            elif event.key() == Qt.Key_Y:
                if self.redo():
                    self.strokeFinished.emit(self.grid)
                event.accept()
                return
        super().keyPressEvent(event)

    def enterEvent(self, event):
        """Mouse entered the widget"""
        self.show_preview = True
        self.update()

    def leaveEvent(self, event):
        """Mouse left the widget"""
        self.show_preview = False
        self.update()

    def draw_brush_preview(self, painter):
        """Draw brush preview at mouse position"""
        if self.mouse_pos.x() < 0 or self.mouse_pos.y() < 0:
            return

        # Map mouse position to image coordinates for size calculation
        ix, iy = self.map_widget_to_image_coords(self.mouse_pos)

        # Calculate brush size in widget coordinates
        scale_x = self.target_rect.width() / self.image.width()
        scale_y = self.target_rect.height() / self.image.height()
        scale = min(scale_x, scale_y)  # Use the smaller scale to maintain aspect ratio

        widget_brush_size = self.brush_size * scale
        half_brush = widget_brush_size / 2

        # Set up preview drawing
        painter.setPen(
            QPen(QColor(255, 255, 255, 180), 2, Qt.DashLine)
        )  # Semi-transparent white dashed line
        painter.setBrush(Qt.NoBrush)

        # Draw preview shape
        if self.brush_shape.lower() == "circle":
            painter.drawEllipse(self.mouse_pos, int(half_brush), int(half_brush))
        elif self.brush_shape.lower() == "triangle":
            from PyQt5.QtGui import QPolygon
            import math

            height = int(half_brush * math.sqrt(3))
            points = [
                QPoint(self.mouse_pos.x(), self.mouse_pos.y() - height // 2),
                QPoint(
                    self.mouse_pos.x() - int(half_brush),
                    self.mouse_pos.y() + height // 2,
                ),
                QPoint(
                    self.mouse_pos.x() + int(half_brush),
                    self.mouse_pos.y() + height // 2,
                ),
            ]
            polygon = QPolygon(points)
            painter.drawPolygon(polygon)
        elif self.brush_shape.lower() == "square":
            painter.drawRect(
                self.mouse_pos.x() - int(half_brush),
                self.mouse_pos.y() - int(half_brush),
                int(widget_brush_size),
                int(widget_brush_size),
            )

    def map_widget_to_image_coords(self, pos):
        x_rel = pos.x() - self.target_rect.x()
        y_rel = pos.y() - self.target_rect.y()

        ix = int(x_rel * self.image.width() / self.target_rect.width())
        iy = int(y_rel * self.image.height() / self.target_rect.height())

        return max(0, min(ix, self.image.width() - 1)), max(
            0, min(iy, self.image.height() - 1)
        )

    def draw_at_pos(self, pos):
        ix, iy = self.map_widget_to_image_coords(pos)

        painter = QPainter(self.image)
        color = self.COLORS[self.current_phase]
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)

        half_brush = self.brush_size // 2
        start_x = ix - half_brush
        start_y = iy - half_brush

        if self.brush_shape == "circle":
            painter.drawEllipse(QPoint(ix, iy), half_brush, half_brush)
        elif self.brush_shape == "triangle":
            polygon = self._create_triangle_polygon(ix, iy, half_brush)
            painter.drawPolygon(polygon)
        elif self.brush_shape == "square":
            painter.drawRect(start_x, start_y, self.brush_size, self.brush_size)
        else:
            # Default to circle if an unknown shape is somehow selected
            painter.drawEllipse(QPoint(ix, iy), half_brush, half_brush)

        painter.end()

        # Update grid
        phase_to_set = self.current_phase

        # Create a mask for the brush shape
        y_coords, x_coords = np.ogrid[
            -half_brush : half_brush + 1, -half_brush : half_brush + 1
        ]
        if self.brush_shape == "circle":
            mask = x_coords**2 + y_coords**2 <= half_brush**2
        elif self.brush_shape == "triangle":
            mask = self._create_triangle_mask(x_coords, y_coords, half_brush)
        elif self.brush_shape == "square":
            # Square brush mask
            mask = (abs(x_coords) <= half_brush) & (abs(y_coords) <= half_brush)
        else:
            # Default to circle mask
            mask = x_coords**2 + y_coords**2 <= half_brush**2

        # Apply the mask to the grid
        for r in range(mask.shape[0]):
            for c in range(mask.shape[1]):
                if mask[r, c]:
                    ny, nx = start_y + r, start_x + c
                    if 0 <= ny < self.grid.shape[0] and 0 <= nx < self.grid.shape[1]:
                        self.grid[ny, nx] = phase_to_set

        self.set_data(self.grid)

    def _flood_fill(self, start_row, start_col, target_phase, replacement_phase):
        if target_phase == replacement_phase:
            return

        rows, cols = self.grid.shape
        q = [(start_row, start_col)]

        while q:
            r, c = q.pop(0)

            if not (
                0 <= r < rows and 0 <= c < cols and self.grid[r, c] == target_phase
            ):
                continue

            self.grid[r, c] = replacement_phase
            self.image.setPixelColor(
                c, r, self.COLORS[replacement_phase % len(self.COLORS)]
            )

            q.append((r + 1, c))
            q.append((r - 1, c))
            q.append((r, c + 1))
            q.append((r, c - 1))

        self.update()

    def set_data(self, grid: np.ndarray):
        self.grid = grid.astype(int)  # Ensure grid contains integers
        height, width = self.grid.shape
        if self.image.size() != QSize(width, height):
            self.image = QImage(width, height, QImage.Format_RGB32)
            self.image_size = QSize(width, height)

        for y in range(height):
            for x in range(width):
                phase = int(self.grid[y, x])  # Explicitly convert to int
                self.image.setPixelColor(x, y, self.COLORS[phase % len(self.COLORS)])
        self.update()


