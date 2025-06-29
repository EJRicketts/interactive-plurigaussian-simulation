from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QComboBox, 
                             QSlider, QPushButton, QToolButton, QHBoxLayout,
                             QLabel, QSpinBox, QDoubleSpinBox, QButtonGroup)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QColor

class ControlsPanel(QWidget):
    shapeChanged = pyqtSignal(str)
    sizeChanged = pyqtSignal(int)
    phaseChanged = pyqtSignal(int)
    regenerate = pyqtSignal()
    lengthScaleChanged = pyqtSignal(float, float)
    clearLithotype = pyqtSignal()
    toolChanged = pyqtSignal(str)
    updateParameters = pyqtSignal()
    undoRequested = pyqtSignal()
    redoRequested = pyqtSignal()
    resetToDefaults = pyqtSignal()
    saveState = pyqtSignal()
    loadState = pyqtSignal()
    exportImages = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)

        # Brush Controls
        brush_group = QGroupBox("Brush Settings")
        brush_layout = QVBoxLayout()
        brush_group.setLayout(brush_layout)

        self.shape_combo = QComboBox()
        self.shape_combo.setToolTip("Select the shape of the brush.")
        self.shape_combo.addItems(["Circle", "Triangle", "Square"])
        self.shape_combo.currentTextChanged.connect(self.shapeChanged)
        brush_layout.addWidget(QLabel("Shape:"))
        brush_layout.addWidget(self.shape_combo)

        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setToolTip("Adjust the size of the brush.")
        self.size_slider.setRange(1, 75)
        self.size_slider.setValue(25)
        self.size_slider.valueChanged.connect(self.sizeChanged)
        brush_layout.addWidget(self.size_slider)

        tool_layout = QHBoxLayout()
        self.brush_tool_button = QPushButton("Brush")
        self.brush_tool_button.setCheckable(True)
        self.brush_tool_button.setChecked(True) # Default to brush tool
        self.brush_tool_button.toggled.connect(lambda checked: self._on_tool_toggled("brush", checked))
        tool_layout.addWidget(self.brush_tool_button)

        self.fill_tool_button = QPushButton("Fill")
        self.fill_tool_button.setCheckable(True)
        self.fill_tool_button.toggled.connect(lambda checked: self._on_tool_toggled("fill", checked))
        tool_layout.addWidget(self.fill_tool_button)

        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)
        self.tool_group.addButton(self.brush_tool_button)
        self.tool_group.addButton(self.fill_tool_button)
        
        brush_layout.addLayout(tool_layout)
        
        # Undo/Redo buttons
        undo_redo_layout = QHBoxLayout()
        self.undo_button = QPushButton("Undo")
        self.undo_button.setToolTip("Undo last action (Ctrl+Z)")
        self.undo_button.clicked.connect(self.undoRequested)
        self.undo_button.setEnabled(False)  # Start disabled
        undo_redo_layout.addWidget(self.undo_button)
        
        self.redo_button = QPushButton("Redo")
        self.redo_button.setToolTip("Redo last undone action (Ctrl+Y)")
        self.redo_button.clicked.connect(self.redoRequested)
        self.redo_button.setEnabled(False)  # Start disabled
        undo_redo_layout.addWidget(self.redo_button)
        
        brush_layout.addLayout(undo_redo_layout)
        
        self.layout.addWidget(brush_group)

        # Phase Controls
        phase_group = QGroupBox("Phase Selection")
        phase_layout = QVBoxLayout()
        phase_group.setLayout(phase_layout)

        self.phase_buttons_layout = QHBoxLayout()
        phase_layout.addLayout(self.phase_buttons_layout)
        self.phase_buttons = []

        self.layout.addWidget(phase_group)

        # Simulation Controls
        sim_group = QGroupBox("Simulation")
        sim_layout = QVBoxLayout()
        sim_group.setLayout(sim_layout)

        self.regenerate_button = QPushButton("Regenerate Random Fields")
        self.regenerate_button.setToolTip("Generate a new set of random fields for the simulation.")
        self.regenerate_button.clicked.connect(self.regenerate)
        sim_layout.addWidget(self.regenerate_button)

        self.clear_lithotype_button = QPushButton("Clear Lithotype")
        self.clear_lithotype_button.setToolTip("Clear the lithotype grid to phase 0.")
        self.clear_lithotype_button.clicked.connect(self.clearLithotype)
        sim_layout.addWidget(self.clear_lithotype_button)
        
        self.update_parameters_button = QPushButton("Update Parameters")
        self.update_parameters_button.setToolTip("Apply length scale changes and regenerate fields while keeping lithotype.")
        self.update_parameters_button.clicked.connect(self.updateParameters)
        sim_layout.addWidget(self.update_parameters_button)
        
        self.reset_defaults_button = QPushButton("Reset to Defaults")
        self.reset_defaults_button.setToolTip("Reset all parameters to default values and clear lithotype.")
        self.reset_defaults_button.clicked.connect(self.resetToDefaults)
        sim_layout.addWidget(self.reset_defaults_button)
        
        # Save/Load buttons
        save_load_layout = QHBoxLayout()
        self.save_button = QPushButton("Save State")
        self.save_button.setToolTip("Save current lithotype and parameters to file.")
        self.save_button.clicked.connect(self.saveState)
        save_load_layout.addWidget(self.save_button)
        
        self.load_button = QPushButton("Load State")
        self.load_button.setToolTip("Load lithotype and parameters from file.")
        self.load_button.clicked.connect(self.loadState)
        save_load_layout.addWidget(self.load_button)
        
        sim_layout.addLayout(save_load_layout)
        
        self.export_button = QPushButton("Export Images")
        self.export_button.setToolTip("Export lithotype and realization as PNG images.")
        self.export_button.clicked.connect(self.exportImages)
        sim_layout.addWidget(self.export_button)

        

        # Length Scale Inputs
        length_scale_group = QGroupBox("Length Scales")
        length_scale_layout = QHBoxLayout()
        length_scale_group.setLayout(length_scale_layout)

        x_layout = QVBoxLayout()
        x_layout.addWidget(QLabel("Length Scale X:"))
        self.len_scale_x_spinbox = QDoubleSpinBox()
        self.len_scale_x_spinbox.setRange(1.0, 100.0)
        self.len_scale_x_spinbox.setValue(15.0)
        self.len_scale_x_spinbox.setSingleStep(1.0)
        # Remove automatic updates - will be triggered by button instead
        x_layout.addWidget(self.len_scale_x_spinbox)
        length_scale_layout.addLayout(x_layout)

        y_layout = QVBoxLayout()
        y_layout.addWidget(QLabel("Length Scale Y:"))
        self.len_scale_y_spinbox = QDoubleSpinBox()
        self.len_scale_y_spinbox.setRange(1.0, 100.0)
        self.len_scale_y_spinbox.setValue(15.0)
        self.len_scale_y_spinbox.setSingleStep(1.0)
        # Remove automatic updates - will be triggered by button instead
        y_layout.addWidget(self.len_scale_y_spinbox)
        length_scale_layout.addLayout(y_layout)
        self.layout.addWidget(length_scale_group)

        # Domain Size Inputs
        domain_size_group = QGroupBox("Domain Size")
        domain_size_layout = QHBoxLayout()
        domain_size_group.setLayout(domain_size_layout)

        width_layout = QVBoxLayout()
        width_layout.addWidget(QLabel("Width:"))
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(50, 500)
        self.width_spinbox.setValue(250)
        self.width_spinbox.setSingleStep(10)
        width_layout.addWidget(self.width_spinbox)
        domain_size_layout.addLayout(width_layout)

        height_layout = QVBoxLayout()
        height_layout.addWidget(QLabel("Height:"))
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(50, 500)
        self.height_spinbox.setValue(250)
        self.height_spinbox.setSingleStep(10)
        height_layout.addWidget(self.height_spinbox)
        domain_size_layout.addLayout(height_layout)
        self.layout.addWidget(domain_size_group)

        self.layout.addWidget(sim_group)

        

    

    def _on_tool_toggled(self, tool_name, checked):
        if checked:
            self.toolChanged.emit(tool_name)

    def update_phase_buttons(self, num_phases, colors):
        # Clear existing buttons
        for button in self.phase_buttons:
            self.phase_buttons_layout.removeWidget(button)
            button.deleteLater()
        self.phase_buttons = []

        for i in range(num_phases): # Dynamically display phases based on num_phases
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(colors[i]))
            icon = QIcon(pixmap)
            
            button = QToolButton()
            button.setIcon(icon)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, phase=i: self.phase_button_clicked(phase, checked))
            
            self.phase_buttons_layout.addWidget(button)
            self.phase_buttons.append(button)

        if self.phase_buttons:
            self.phase_buttons[0].setChecked(True)

    def phase_button_clicked(self, phase, checked):
        if checked:
            self.phaseChanged.emit(phase)
            for i, btn in enumerate(self.phase_buttons):
                if i != phase:
                    btn.setChecked(False)

    def update_undo_redo_buttons(self, can_undo, can_redo):
        """Update the enabled state of undo/redo buttons"""
        self.undo_button.setEnabled(can_undo)
        self.redo_button.setEnabled(can_redo)

    def reset_to_default_values(self):
        """Reset all controls to their default values"""
        # Default values
        default_brush_size = 25
        default_len_scale = 15.0
        default_domain_width = 250
        default_domain_height = 250
        
        # Reset controls
        self.size_slider.setValue(default_brush_size)
        self.shape_combo.setCurrentText("Circle")
        self.len_scale_x_spinbox.setValue(default_len_scale)
        self.len_scale_y_spinbox.setValue(default_len_scale)
        self.width_spinbox.setValue(default_domain_width)
        self.height_spinbox.setValue(default_domain_height)
        
        # Reset tool selection
        self.brush_tool_button.setChecked(True)
        self.fill_tool_button.setChecked(False)
        
        # Reset phase selection to phase 0
        if self.phase_buttons:
            for i, btn in enumerate(self.phase_buttons):
                btn.setChecked(i == 0)