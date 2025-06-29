import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QScrollArea
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage
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
        self.controls_widget.setFixedWidth(300) # Set a fixed width for the controls panel
        
        fixed_width = 250
        fixed_height = 250

        # Simulation Engine
        self.simulation_engine = SimulationEngine(width=fixed_width, height=fixed_height)

        self.l_canvas_widget = CanvasWidget(width=fixed_width, height=fixed_height)
        self.p_canvas_widget = ResultWidget(width=fixed_width, height=fixed_height)
        self.p_canvas_widget.set_data(self.simulation_engine.simulate())

        self.controls_scroll_area = QScrollArea()
        self.controls_scroll_area.setWidgetResizable(True)
        self.controls_scroll_area.setWidget(self.controls_widget)
        self.controls_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Create canvas containers with titles
        from PyQt5.QtWidgets import QVBoxLayout, QLabel
        
        l_container = QWidget()
        l_layout = QVBoxLayout(l_container)
        l_layout.setContentsMargins(0, 0, 0, 0)
        l_title = QLabel("Lithotype")
        l_title.setAlignment(Qt.AlignCenter)
        l_title.setMaximumHeight(20)
        l_layout.addWidget(l_title)
        l_layout.addWidget(self.l_canvas_widget, 1)  # Give canvas stretch factor of 1
        
        p_container = QWidget()
        p_layout = QVBoxLayout(p_container)
        p_layout.setContentsMargins(0, 0, 0, 0)
        p_title = QLabel("Realisation")
        p_title.setAlignment(Qt.AlignCenter)
        p_title.setMaximumHeight(20)
        p_layout.addWidget(p_title)
        p_layout.addWidget(self.p_canvas_widget, 1)  # Give canvas stretch factor of 1
        
        self.main_splitter.addWidget(self.controls_scroll_area)
        self.main_splitter.addWidget(l_container)
        self.main_splitter.addWidget(p_container)

        # Set initial sizes for the splitter to make L and P canvases equal
        self.main_splitter.setSizes([300, 600, 600]) # Example: Controls, L, P
        self.main_splitter.setStretchFactor(0, 0) # Fixed width for controls
        self.main_splitter.setStretchFactor(1, 1) # Dynamic resize for L canvas
        self.main_splitter.setStretchFactor(2, 1) # Dynamic resize for P canvas

        # Initial state: set phase 0 as default and sync brush size
        self.l_canvas_widget.set_phase(0)
        self.l_canvas_widget.set_brush_size(self.controls_widget.size_slider.value())
        self.controls_widget.update_phase_buttons(
            self.simulation_engine.get_num_phases(),
            self.l_canvas_widget.COLORS
        )

        # Connections
        self.l_canvas_widget.strokeFinished.connect(self.run_simulation)
        self.controls_widget.shapeChanged.connect(self.l_canvas_widget.set_brush_shape)
        self.controls_widget.sizeChanged.connect(self.l_canvas_widget.set_brush_size)
        self.controls_widget.phaseChanged.connect(self.l_canvas_widget.set_phase)
        self.controls_widget.regenerate.connect(self.regenerate_fields)
        self.controls_widget.clearLithotype.connect(self.clear_lithotype)
        self.controls_widget.updateParameters.connect(self.update_parameters)
        self.controls_widget.toolChanged.connect(self.l_canvas_widget.set_tool)
        

    def run_simulation(self, grid):
        self.simulation_engine.update_lithotypes(grid)
        p_field = self.simulation_engine.simulate()
        self.p_canvas_widget.set_data(p_field)

    def clear_lithotype(self):
        self.l_canvas_widget.grid.fill(0) # Set all cells to phase 0
        self.l_canvas_widget.set_data(self.l_canvas_widget.grid) # Redraw canvas
        self.run_simulation(self.l_canvas_widget.grid) # Trigger simulation update

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
        if width != self.simulation_engine.width or height != self.simulation_engine.height:
            # Update domain size (this will preserve lithotypes where possible)
            self.simulation_engine.set_domain_size(width, height)
            # Update canvas widgets to match new domain size
            self.l_canvas_widget.image_size = QSize(width, height)
            self.l_canvas_widget.image = QImage(self.l_canvas_widget.image_size, QImage.Format_RGB32)
            self.l_canvas_widget.grid = self.simulation_engine.lithotypes.copy()
            self.l_canvas_widget.set_data(self.l_canvas_widget.grid)
            
            # P canvas also uses same dimensions (transpose is handled in data, not image size)
            self.p_canvas_widget.image_size = QSize(width, height)
            self.p_canvas_widget.image = QImage(self.p_canvas_widget.image_size, QImage.Format_RGB32)
        else:
            # Only update length scales if domain size didn't change
            self.simulation_engine.set_length_scales(len_scale_x, len_scale_y)
            
        # Run simulation with current lithotype
        self.run_simulation(self.l_canvas_widget.grid)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())