import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import os

class AFI_FField_Heatmap:
    """
    DT-03: Spatial F-field heatmap over HORSE CFT floor plan.
    Interpolates F values from discrete sensor points to continuous field using RBF.
    Dimensions: 30.30m x 18.30m (Based on WILDONE plans Nov 2025).
    """
    
    SENSOR_LOCATIONS = {
        "Sala_Multiusos": (6.85, 3.85),
        "Biblioteca": (17.30, 3.35),
        "Auditorio": (17.30, 12.05),
        "Circulacao_GF": (3.40, 11.75),
        "Zona_Social": (10.20, 9.70),
        "Sala_A": (4.10, 11.45),
        "Sala_B": (11.13, 11.45)
    }

    FREEDOM_CMAP = LinearSegmentedColormap.from_list(
        "freedom",
        [(0.0, "#ff453a"), (0.3, "#ff9f0a"), (0.6, "#30d158"), (1.0, "#0a84ff")],
        N=256
    )

    def render_field(self, output_path="horse_cft_f_field.png"):
        print("Generating HORSE CFT F-Field Spatial Map...")
        
        # Simulated F-values for a typical busy morning
        F_values = {
            "Sala_Multiusos": 0.85, "Biblioteca": 0.72,
            "Auditorio": 0.35, "Circulacao_GF": 0.65,
            "Zona_Social": 0.55, "Sala_A": 0.80, "Sala_B": 0.82
        }

        coords = np.array(list(self.SENSOR_LOCATIONS.values()))
        F_measured = np.array(list(F_values.values()))

        x_grid = np.linspace(0, 30.30, 303)
        y_grid = np.linspace(0, 18.30, 183)
        X, Y = np.meshgrid(x_grid, y_grid)
        grid_pts = np.column_stack([X.ravel(), Y.ravel()])

        rbf = RBFInterpolator(coords, F_measured, kernel='thin_plate_spline', smoothing=0.1)
        F_field = rbf(grid_pts).reshape(X.shape)
        F_field = np.clip(F_field, 0.0, 1.0)
        
        F_field = gaussian_filter(F_field, sigma=1.5)

        fig, ax = plt.subplots(figsize=(12, 7), facecolor='#1a1a1a')
        ax.set_facecolor('#0d0d0d')

        im = ax.imshow(
            F_field, origin='lower', extent=[0, 30.30, 0, 18.30],
            cmap=self.FREEDOM_CMAP, vmin=0.0, vmax=1.0, alpha=0.88
        )

        for sid, (x, y) in self.SENSOR_LOCATIONS.items():
            F = F_values[sid]
            ax.scatter(x, y, s=100, c='white', zorder=5, edgecolors='gray')
            ax.annotate(f"{sid}\nF={F:.2f}", (x, y), textcoords="offset points",
                        xytext=(0, 10), ha='center', fontsize=8, color='white', weight='bold')

        cbar = fig.colorbar(im, ax=ax, fraction=0.02, pad=0.02)
        cbar.set_label('Freedom Index (F = P/D)', color='white', fontsize=10)
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')

        ax.set_xlabel("Building length (m)", color='#888888')
        ax.set_ylabel("Building width (m)", color='#888888')
        ax.tick_params(colors='#888888')
        ax.set_title("HORSE CFT — AFI Spatial F-Field Heatmap", color='white', fontsize=14, pad=15)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, facecolor='#1a1a1a')
        print(f"Success! High-res heatmap saved to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    heatmap = AFI_FField_Heatmap()
    heatmap.render_field()
