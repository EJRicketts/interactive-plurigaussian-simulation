import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QScrollArea
from PyQt5.QtCore import Qt
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
        
        initial_width = self.controls_widget.domain_width_spinbox.value()
        initial_height = self.controls_widget.domain_height_spinbox.value()

        # Simulation Engine
        self.simulation_engine = SimulationEngine(width=initial_width, height=initial_height)

        self.l_canvas_widget = CanvasWidget(width=initial_width, height=initial_height)
        self.p_canvas_widget = ResultWidget(width=initial_width, height=initial_height)
        self.p_canvas_widget.set_data(self.simulation_engine.simulate())

        self.controls_scroll_area = QScrollArea()
        self.controls_scroll_area.setWidgetResizable(True)
        self.controls_scroll_area.setWidget(self.controls_widget)
        self.controls_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.main_splitter.addWidget(self.controls_scroll_area)
        self.main_splitter.addWidget(self.l_canvas_widget)
        self.main_splitter.addWidget(self.p_canvas_widget)

        # Set initial sizes for the splitter to make L and P canvases equal
        self.main_splitter.setSizes([300, 600, 600]) # Example: Controls, L, P
        self.main_splitter.setStretchFactor(0, 0) # Fixed width for controls
        self.main_splitter.setStretchFactor(1, 1) # Dynamic resize for L canvas
        self.main_splitter.setStretchFactor(2, 1) # Dynamic resize for P canvas

        # Initial state: set phase 0 as default
        self.l_canvas_widget.set_phase(0)
        self.controls_widget.update_phase_buttons(
            self.simulation_engine.get_num_phases(),
            self.l_canvas_widget.COLORS
        )

        # Connections
        self.l_canvas_widget.strokeFinished.connect(self.run_simulation)
        self.controls_widget.shapeChanged.connect(self.l_canvas_widget.set_brush_shape)
        self.controls_widget.sizeChanged.connect(self.l_canvas_widget.set_brush_size)
        self.controls_widget.modeChanged.connect(self.l_canvas_widget.set_draw_mode)
        self.controls_widget.phaseChanged.connect(self.l_canvas_widget.set_phase)
        self.controls_widget.regenerate.connect(self.regenerate_fields)
        self.controls_widget.clearLithotype.connect(self.clear_lithotype)
        self.controls_widget.lengthScaleChanged.connect(self.update_length_scales)
        self.controls_widget.domainSizeChanged.connect(self.set_domain_size)
        

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

    def set_domain_size(self, width, height):
        self.l_canvas_widget.set_size(width, height)
        self.p_canvas_widget.set_size(width, height)
        self.simulation_engine.set_domain_size(width, height)
        self.run_simulation(self.l_canvas_widget.grid)

    def update_length_scales(self, len_scale_x, len_scale_y):
        self.simulation_engine.set_length_scales(len_scale_x, len_scale_y)
        self.run_simulation(self.l_canvas_widget.grid)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())