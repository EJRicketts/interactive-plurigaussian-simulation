# Interactive Plurigaussian Simulation

An interactive desktop application for exploring Plurigaussian Simulation (PGS) in geostatistical modeling.

## Description

This tool provides an intuitive interface for understanding and experimenting with Plurigaussian Simulation, a powerful geostatistical method used in subsurface modeling and geological characterization. The application allows users to interactively define lithotypes and observe how they influence the realisations.

## Purpose

The primary objective of this tool is to facilitate the exploration and understanding of lithotype relationships in geostatistical simulations. It serves as:

- **Educational Resource**: Provides hands-on experience with PGS concepts for students and researchers
- **Research Tool**: Enables rapid prototyping and testing of lithotype configurations
- **Visualization Platform**: Offers real-time feedback on the relationship between lithotype constraints and simulated fields
- **Interactive Learning**: Bridges the gap between theoretical understanding and practical application of PGS methods

## Features

### Interactive Modeling Environment
- **Real-time Simulation**: Instantaneous PGS updates as lithotypes are modified
- **Multi-phase Support**: Work with up to 5 categorical phases with distinct visual representation
- **Flexible Drawing Tools**: Multiple brush shapes (circle, triangle, square) with adjustable sizes
- **Fill Tool**: Rapid lithotype assignment using flood-fill algorithms

### Geostatistical Controls
- **Adjustable Correlation Lengths**: Independent control of X and Y direction correlation scales
- **Random Field Regeneration**: Sample new realizations while maintaining lithotype constraints

## Installation

### Prerequisites
- Python 3.9 or higher
- Conda package manager (recommended)

### Dependencies
The application requires the following Python packages:
- `PyQt5` - GUI framework
- `gstools` - Geostatistical simulation library
- `numpy` - Numerical computing

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/interactive-plurigaussian-simulation.git
   cd interactive-plurigaussian-simulation
   ```

2. **Create a conda environment** (recommended):
   ```bash
   conda create -n pgs-interactive python=3.9
   conda activate pgs-interactive
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app/main.py
   ```

## Usage

Launch the application and begin by selecting lithotype phases from the control panel. Use the drawing tools to create lithotype patterns on the left canvas, and observe the corresponding PGS simulation results on the right canvas. Adjust correlation lengths and regenerate random fields to explore different scenarios.

## Contributing

Contributions are welcome from the academic and research community. Please fork the repository and submit pull requests for any enhancements or bug fixes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
