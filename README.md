# Interactive Plurigaussian Simulation App

This is an interactive desktop application built with PyQt and GSTools, designed to allow users to draw lithotype fields (L) on a grid and visualize real-time Plurigaussian Simulation (PGS) outputs (P). It's a tool for geoscientists and enthusiasts to explore geostatistical concepts interactively.

## Features

*   **Interactive Grid Editor**: Draw lithotypes on a 150x150 grid.
*   **Brush Tools**: Utilize circle and triangle brush shapes with adjustable size and add/subtract modes.
*   **Fixed 5 Phases**: Work with 5 predefined categorical phases (0-4), with clear color mapping (Phase 0: Black, Phase 1: White, Phase 2: Red, Phase 3: Green, Phase 4: Blue).
*   **Real-time Simulation**: Side-by-side display of the lithotype (L) and the simulated plurigaussian field (P), updating dynamically with each edit.
*   **Regenerate Random Fields**: Button to sample new realizations of the underlying random fields.
*   **Clear Lithotype**: Button to reset the lithotype grid to all Phase 0.
*   **Adjustable Length Scales**: Input fields for controlling the X and Y length scales of the random fields, with debounced updates for smooth interaction.
*   **Adjustable Domain Size**: Input fields for setting the width and height of the simulation grid (defaulting to 150x150).
*   **Responsive Layout**: A 3-column layout (Controls | Lithotype | Simulation) with a fixed-width, vertically scrollable controls panel and dynamically resizing canvas areas.

## Directory Structure

```
project_root/
├── app/
│   ├── main.py           # Application entry point
│   ├── ui/               # PyQt UI modules
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── canvas.py     # Custom drawing widget for lithotype
│   │   ├── controls.py   # UI controls (brush settings, phase selector, simulation params)
│   │   └── result_widget.py # Read-only widget for simulation output
│   └── logic/
│       ├── __init__.py
│       ├── data_model.py # (Currently unused, placeholder for future data structures)
│       └── simulation.py # GSTools integration and PGS logic
├── requirements.txt      # Python dependencies
└── README.md             # This README file
```

## Installation

It is recommended to use a `conda` environment for managing dependencies.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/interactive-plurigaussian-simulation.git
    cd interactive-plurigaussian-simulation
    ```

2.  **Create and activate a conda environment (recommended)**:
    ```bash
    conda create -n intPGS python=3.9
    conda activate intPGS
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the application, execute the `main.py` script:

```bash
python app/main.py
```

The application window will open with the default 150x150 grid, 5 phases, and length scales of 15. You can then interact with the controls to draw lithotypes, regenerate simulations, and adjust parameters.

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue. If you'd like to contribute code, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.