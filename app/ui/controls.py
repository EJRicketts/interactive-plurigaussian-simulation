from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QComboBox, 
                             QSlider, QPushButton, QToolButton, QHBoxLayout,
                             QLabel, QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QColor

class ControlsPanel(QWidget):
    shapeChanged = pyqtSignal(str)
    sizeChanged = pyqtSignal(int)
    modeChanged = pyqtSignal(str)
    phaseChanged = pyqtSignal(int)
    regenerate = pyqtSignal()
    lengthScaleChanged = pyqtSignal(float, float)
    clearLithotype = pyqtSignal()
    domainSizeChanged = pyqtSignal(int, int)
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
        self.shape_combo.addItems(["Circle", "Triangle"])
        self.shape_combo.currentTextChanged.connect(self.shapeChanged)
        brush_layout.addWidget(QLabel("Shape:"))
        brush_layout.addWidget(self.shape_combo)

        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setToolTip("Adjust the size of the brush.")
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(20)
        self.size_slider.valueChanged.connect(self.sizeChanged)
        brush_layout.addWidget(QLabel("Size:"))
        brush_layout.addWidget(self.size_slider)

        self.mode_button = QPushButton("Mode: Add")
        self.mode_button.setToolTip("Toggle between adding and subtracting phases.")
        self.mode_button.setCheckable(True)
        self.mode_button.toggled.connect(self.on_mode_toggled)
        brush_layout.addWidget(self.mode_button)
        
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
        self.len_scale_x_spinbox.valueChanged.connect(lambda value: self.lengthScaleChanged.emit(value, self.len_scale_y_spinbox.value()))
        x_layout.addWidget(self.len_scale_x_spinbox)
        length_scale_layout.addLayout(x_layout)

        y_layout = QVBoxLayout()
        y_layout.addWidget(QLabel("Length Scale Y:"))
        self.len_scale_y_spinbox = QDoubleSpinBox()
        self.len_scale_y_spinbox.setRange(1.0, 100.0)
        self.len_scale_y_spinbox.setValue(15.0)
        self.len_scale_y_spinbox.setSingleStep(1.0)
        self.len_scale_y_spinbox.valueChanged.connect(lambda value: self.lengthScaleChanged.emit(self.len_scale_x_spinbox.value(), value))
        y_layout.addWidget(self.len_scale_y_spinbox)
        length_scale_layout.addLayout(y_layout)
        self.layout.addWidget(length_scale_group)

        self.layout.addWidget(sim_group)

        # Domain Size Inputs
        domain_size_group = QGroupBox("Domain Size (pixels)")
        domain_size_layout = QVBoxLayout()
        domain_size_group.setLayout(domain_size_layout)

        self.domain_width_spinbox = QSpinBox()
        self.domain_width_spinbox.setRange(50, 500)
        self.domain_width_spinbox.setValue(200)
        self.domain_width_spinbox.valueChanged.connect(lambda value: self.domainSizeChanged.emit(value, self.domain_height_spinbox.value()))
        domain_size_layout.addWidget(QLabel("Width:"))
        domain_size_layout.addWidget(self.domain_width_spinbox)

        self.domain_height_spinbox = QSpinBox()
        self.domain_height_spinbox.setRange(50, 500)
        self.domain_height_spinbox.setValue(200)
        self.domain_height_spinbox.valueChanged.connect(lambda value: self.domainSizeChanged.emit(self.domain_width_spinbox.value(), value))
        domain_size_layout.addWidget(QLabel("Height:"))
        domain_size_layout.addWidget(self.domain_height_spinbox)
        self.layout.addWidget(domain_size_group)

    

    def on_mode_toggled(self, checked):
        if checked:
            self.mode_button.setText("Mode: Subtract")
            self.modeChanged.emit("subtract")
        else:
            self.mode_button.setText("Mode: Add")
            self.modeChanged.emit("add")

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