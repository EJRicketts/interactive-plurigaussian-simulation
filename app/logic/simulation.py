import numpy as np
import gstools as gs


class SimulationEngine:
    def __init__(self, width=250, height=250, len_scale_x=10.0, len_scale_y=10.0):
        self.width = width
        self.height = height
        self.grid_shape = (height, width)
        self.lithotypes = np.zeros(self.grid_shape)
        self.len_scale_x = len_scale_x
        self.len_scale_y = len_scale_y
        self.num_phases = 6

        # Define coordinates for the structured grid
        x = np.arange(0, width, 1)  # x-coordinates (columns)
        y = np.arange(0, height, 1)  # y-coordinates (rows)
        self.coords = [
            y,
            x,
        ]  # GSTools expects [y, x] for (rows, columns) array

        # Create two independent SRFs for a 2D PGS
        self.model1 = gs.Gaussian(
            dim=2, var=1.0, len_scale=[self.len_scale_x, self.len_scale_y]
        )
        self.srf1 = gs.SRF(self.model1)

        self.model2 = gs.Gaussian(
            dim=2, var=1.0, len_scale=[self.len_scale_x, self.len_scale_y]
        )
        self.srf2 = gs.SRF(self.model2)

        self.pgs = None
        self.thresholds = [
            0.16,
            0.32,
            0.48,
            0.64,
            0.8,
        ]  # Fixed thresholds for 6 phases (0-5)

        self.regenerate_fields()

    def set_length_scales(self, len_scale_x, len_scale_y):
        self.len_scale_x = len_scale_x
        self.len_scale_y = len_scale_y
        self.model1.len_scale = [self.len_scale_x, self.len_scale_y]
        self.model2.len_scale = [self.len_scale_x, self.len_scale_y]
        self.regenerate_fields()

    def set_domain_size(self, width, height):
        """Update domain size and reinitialize grid and coordinates"""
        self.width = width
        self.height = height
        self.grid_shape = (height, width)

        # Preserve existing lithotypes if possible, otherwise reset
        old_lithotypes = self.lithotypes.copy()
        self.lithotypes = np.zeros(self.grid_shape)

        # Copy over lithotypes that fit in the new grid
        min_height = min(old_lithotypes.shape[0], height)
        min_width = min(old_lithotypes.shape[1], width)
        self.lithotypes[:min_height, :min_width] = old_lithotypes[
            :min_height, :min_width
        ]

        # Update coordinates for new grid size
        x = np.arange(0, width, 1)  # x-coordinates (columns)
        y = np.arange(0, height, 1)  # y-coordinates (rows)
        self.coords = [y, x]

        # Regenerate fields with new domain size
        self.regenerate_fields()

    def update_lithotypes(self, grid: np.ndarray):
        self.lithotypes = grid

    def get_num_phases(self):
        return self.num_phases

    def simulate(self):
        # Get the continuous field from the PGS model
        continuous_field = self.pgs(self.lithotypes)

        return continuous_field.astype(int)

    def regenerate_fields(self):
        seed1 = np.random.randint(0, 2**32 - 1)
        seed2 = np.random.randint(0, 2**32 - 1)

        field1 = self.srf1.structured(self.coords, seed=seed1)
        field2 = self.srf2.structured(self.coords, seed=seed2)

        # The PGS class itself doesn't take thresholds
        self.pgs = gs.PGS(dim=2, fields=[field1, field2])
        return self.simulate()
