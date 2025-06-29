import json
import numpy as np
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QScrollArea,
    QFileDialog,
    QMessageBox,
    QLabel,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage

# Constants
CONTROLS_WIDTH = 350
CANVAS_WIDTH = 600
TITLE_HEIGHT = 20
DEFAULT_SPLITTER_SIZES = [350, 600, 600]
from app.ui.canvas import CanvasWidget
from app.ui.controls import ControlsPanel
from app.ui.result_widget import ResultWidget
from app.logic.simulation import SimulationEngine


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Plurigaussian Simulation")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout with QSplitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.central_widget.setLayout(QHBoxLayout())
        self.central_widget.layout().addWidget(self.main_splitter)

        # Widgets
        self.controls_widget = ControlsPanel()
        self.controls_widget.setFixedWidth(
            350
        )  # Set a fixed width for the controls panel

        fixed_width = 250
        fixed_height = 250

        # Simulation Engine
        self.simulation_engine = SimulationEngine(
            width=fixed_width, height=fixed_height
        )

        self.l_canvas_widget = CanvasWidget(width=fixed_width, height=fixed_height)
        self.p_canvas_widget = ResultWidget(width=fixed_width, height=fixed_height)
        self.p_canvas_widget.set_data(self.simulation_engine.simulate())

        self.controls_scroll_area = QScrollArea()
        self.controls_scroll_area.setWidgetResizable(True)
        self.controls_scroll_area.setWidget(self.controls_widget)
        self.controls_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Create canvas containers with titles

        l_container = QWidget()
        l_layout = QVBoxLayout(l_container)
        l_layout.setContentsMargins(0, 0, 0, 0)
        l_title = QLabel("Lithotype")
        l_title.setAlignment(Qt.AlignCenter)
        l_title.setMaximumHeight(TITLE_HEIGHT)
        l_layout.addWidget(l_title)
        l_layout.addWidget(self.l_canvas_widget, 1)  # Give canvas stretch factor of 1

        p_container = QWidget()
        p_layout = QVBoxLayout(p_container)
        p_layout.setContentsMargins(0, 0, 0, 0)
        p_title = QLabel("Realisation")
        p_title.setAlignment(Qt.AlignCenter)
        p_title.setMaximumHeight(TITLE_HEIGHT)
        p_layout.addWidget(p_title)
        p_layout.addWidget(self.p_canvas_widget, 1)  # Give canvas stretch factor of 1

        self.main_splitter.addWidget(self.controls_scroll_area)
        self.main_splitter.addWidget(l_container)
        self.main_splitter.addWidget(p_container)

        # Set initial sizes for the splitter to make L and P canvases equal
        self.main_splitter.setSizes(DEFAULT_SPLITTER_SIZES)
        self.main_splitter.setStretchFactor(0, 0)  # Fixed width for controls
        self.main_splitter.setStretchFactor(1, 1)  # Dynamic resize for L canvas
        self.main_splitter.setStretchFactor(2, 1)  # Dynamic resize for P canvas

        # Initial state: set phase 0 as default and sync brush size
        self.l_canvas_widget.set_phase(0)
        self.l_canvas_widget.set_brush_size(self.controls_widget.size_slider.value())
        self.controls_widget.update_phase_buttons(
            self.simulation_engine.get_num_phases(), self.l_canvas_widget.COLORS
        )

        # Connections
        self.l_canvas_widget.strokeFinished.connect(self.run_simulation)
        self.l_canvas_widget.strokeFinished.connect(
            lambda: self.update_undo_redo_buttons()
        )
        self.controls_widget.shapeChanged.connect(self.l_canvas_widget.set_brush_shape)
        self.controls_widget.sizeChanged.connect(self.l_canvas_widget.set_brush_size)
        self.controls_widget.phaseChanged.connect(self.l_canvas_widget.set_phase)
        self.controls_widget.regenerate.connect(self.regenerate_fields)
        self.controls_widget.clearLithotype.connect(self.clear_lithotype)
        self.controls_widget.updateParameters.connect(self.update_parameters)
        self.controls_widget.toolChanged.connect(self.l_canvas_widget.set_tool)
        self.controls_widget.undoRequested.connect(self.handle_undo)
        self.controls_widget.redoRequested.connect(self.handle_redo)
        self.controls_widget.resetToDefaults.connect(self.reset_to_defaults)
        self.controls_widget.saveState.connect(self.save_state)
        self.controls_widget.loadState.connect(self.load_state)
        self.controls_widget.exportImages.connect(self.export_images)

    def run_simulation(self, grid):
        self.simulation_engine.update_lithotypes(grid)
        p_field = self.simulation_engine.simulate()
        self.p_canvas_widget.set_data(p_field)

    def clear_lithotype(self):
        self.l_canvas_widget.grid.fill(0)  # Set all cells to phase 0
        self.l_canvas_widget.set_data(self.l_canvas_widget.grid)  # Redraw canvas
        self.l_canvas_widget.save_state()  # Save state so clear is undoable
        self.run_simulation(self.l_canvas_widget.grid)  # Trigger simulation update
        self.update_undo_redo_buttons()  # Update button states

    def regenerate_fields(self):
        p_field = self.simulation_engine.regenerate_fields()
        self.p_canvas_widget.set_data(p_field)

    def update_parameters(self):
        # Get current parameter values from the controls
        len_scale_x = self.controls_widget.len_scale_x_spinbox.value()
        len_scale_y = self.controls_widget.len_scale_y_spinbox.value()
        width = self.controls_widget.width_spinbox.value()
        height = self.controls_widget.height_spinbox.value()

        # Check if domain size changed
        if (
            width != self.simulation_engine.width
            or height != self.simulation_engine.height
        ):
            # Update domain size (this will preserve lithotypes where possible)
            self.simulation_engine.set_domain_size(width, height)
            # Update canvas widgets to match new domain size
            self.l_canvas_widget.image_size = QSize(width, height)
            self.l_canvas_widget.image = QImage(
                self.l_canvas_widget.image_size, QImage.Format_RGB32
            )
            self.l_canvas_widget.grid = self.simulation_engine.lithotypes.copy()
            self.l_canvas_widget.set_data(self.l_canvas_widget.grid)

            # P canvas also uses same dimensions (transpose is handled in data, not image size)
            self.p_canvas_widget.image_size = QSize(width, height)
            self.p_canvas_widget.image = QImage(
                self.p_canvas_widget.image_size, QImage.Format_RGB32
            )
        else:
            # Only update length scales if domain size didn't change
            self.simulation_engine.set_length_scales(len_scale_x, len_scale_y)

        # Run simulation with current lithotype
        self.run_simulation(self.l_canvas_widget.grid)

    def handle_undo(self):
        """Handle undo request from controls"""
        if self.l_canvas_widget.undo():
            self.run_simulation(self.l_canvas_widget.grid)
        self.update_undo_redo_buttons()

    def handle_redo(self):
        """Handle redo request from controls"""
        if self.l_canvas_widget.redo():
            self.run_simulation(self.l_canvas_widget.grid)
        self.update_undo_redo_buttons()

    def update_undo_redo_buttons(self):
        """Update undo/redo button states"""
        self.controls_widget.update_undo_redo_buttons(
            self.l_canvas_widget.can_undo(), self.l_canvas_widget.can_redo()
        )

    def reset_to_defaults(self):
        """Reset all parameters to defaults and clear lithotype"""
        # Reset controls to default values
        self.controls_widget.reset_to_default_values()

        # Clear and reset canvas
        self.clear_lithotype()

        # Update parameters to apply defaults
        self.update_parameters()

        # Update button states
        self.update_undo_redo_buttons()

    def save_state(self):
        """Save current state to JSON file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save State", "", "JSON Files (*.json);;All Files (*)"
        )

        if filename:
            try:
                # Collect current state
                state = {
                    "lithotype_grid": self.l_canvas_widget.grid.tolist(),
                    "parameters": {
                        "width": self.simulation_engine.width,
                        "height": self.simulation_engine.height,
                        "len_scale_x": self.simulation_engine.len_scale_x,
                        "len_scale_y": self.simulation_engine.len_scale_y,
                        "brush_size": self.l_canvas_widget.brush_size,
                        "brush_shape": self.l_canvas_widget.brush_shape,
                        "current_tool": self.l_canvas_widget.current_tool,
                        "current_phase": self.l_canvas_widget.current_phase,
                    },
                }

                # Save to file
                with open(filename, "w") as f:
                    json.dump(state, f, indent=2)

                QMessageBox.information(self, "Success", "State saved successfully!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save state: {str(e)}")

    def load_state(self):
        """Load state from JSON file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load State", "", "JSON Files (*.json);;All Files (*)"
        )

        if filename:
            try:
                # Load from file
                with open(filename, "r") as f:
                    state = json.load(f)

                # Extract data
                lithotype_grid = np.array(state["lithotype_grid"], dtype=int)
                params = state["parameters"]

                # Update controls with loaded parameters
                self.controls_widget.width_spinbox.setValue(params["width"])
                self.controls_widget.height_spinbox.setValue(params["height"])
                self.controls_widget.len_scale_x_spinbox.setValue(params["len_scale_x"])
                self.controls_widget.len_scale_y_spinbox.setValue(params["len_scale_y"])
                self.controls_widget.size_slider.setValue(params["brush_size"])
                self.controls_widget.shape_combo.setCurrentText(
                    params["brush_shape"].title()
                )

                # Set tool and phase
                if params["current_tool"] == "brush":
                    self.controls_widget.brush_tool_button.setChecked(True)
                else:
                    self.controls_widget.fill_tool_button.setChecked(True)

                # Set phase button
                if self.controls_widget.phase_buttons and 0 <= params[
                    "current_phase"
                ] < len(self.controls_widget.phase_buttons):
                    for i, btn in enumerate(self.controls_widget.phase_buttons):
                        btn.setChecked(i == params["current_phase"])

                # Update parameters (this will resize domain if needed)
                self.update_parameters()

                # Load lithotype grid
                self.l_canvas_widget.grid = lithotype_grid
                self.l_canvas_widget.set_data(lithotype_grid)

                # Clear history and add current state
                self.l_canvas_widget.history = [lithotype_grid.copy()]
                self.l_canvas_widget.history_index = 0

                # Run simulation with loaded lithotype
                self.run_simulation(lithotype_grid)

                # Update button states
                self.update_undo_redo_buttons()

                QMessageBox.information(self, "Success", "State loaded successfully!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load state: {str(e)}")

    def export_images(self):
        """Export lithotype and realization images"""
        directory = QFileDialog.getExistingDirectory(self, "Select Export Directory")

        if directory:
            try:
                # Get current timestamp for unique filenames
                from datetime import datetime

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                # Export lithotype image
                lithotype_filename = f"{directory}/lithotype_{timestamp}.png"
                lithotype_success = self.l_canvas_widget.image.save(lithotype_filename)

                # Export realization image
                realization_filename = f"{directory}/realization_{timestamp}.png"
                realization_success = self.p_canvas_widget.image.save(
                    realization_filename
                )

                if lithotype_success and realization_success:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Images exported successfully!\n\nLithotype: {lithotype_filename}\nRealization: {realization_filename}",
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Warning",
                        "Some images may not have been exported successfully.",
                    )

            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to export images: {str(e)}"
                )


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
