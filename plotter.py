#!/usr/bin/env python3
import os, glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm

INPUT_DIR  = "iozone_csv"
OUTPUT_DIR = "iozone_plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def make_plot_from_csv(csv_path: str):
    df = pd.read_csv(csv_path)

    # basic check
    if "kb" not in df.columns:
        raise ValueError(f"'kb' column not found in {csv_path}")

    # Axis values
    y_vals = df["kb"].to_numpy()
    x_vals = df.columns[1:].astype(int).to_numpy()
    Z      = df.iloc[:, 1:].to_numpy(dtype=float)
    Z_filled = np.nan_to_num(Z, nan=0.0)

    # Uniform visual spacing
    xi = np.arange(len(x_vals))
    yi = np.arange(len(y_vals))
    XI, YI = np.meshgrid(xi, yi)

    # Use CSV base name (without extension) for dynamic labels
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    label_name = base_name.replace("_", " ").title()

    fig = plt.figure(figsize=(10,6))
    ax  = fig.add_subplot(111, projection='3d')

    surf = ax.plot_surface(XI, YI, Z_filled,
                           cmap=cm.get_cmap('turbo', 256),
                           edgecolor='none')

    ax.set_title(label_name, fontsize=10)
    ax.set_xlabel("Reclen", fontsize=8)
    ax.set_ylabel("kB", fontsize=8)
    ax.set_zlabel(label_name, fontsize=8)   # z-axis reflects CSV name

    ax.set_xticks(xi)
    ax.set_xticklabels(x_vals, fontsize=6)
    ax.set_yticks(yi)
    ax.set_yticklabels(y_vals, fontsize=6)
    ax.tick_params(axis='z', labelsize=6)

    ax.view_init(elev=25, azim=-60)

    cbar = fig.colorbar(surf, shrink=0.6, aspect=10, pad=0.1)
    cbar.set_label(label_name, fontsize=8)
    cbar.ax.tick_params(labelsize=6)

    out_path = os.path.join(OUTPUT_DIR, f"{base_name}.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    return out_path

def main():
    csv_files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.csv")))
    if not csv_files:
        raise SystemExit(f"No CSV files found in '{INPUT_DIR}'")

    for csv in csv_files:
        out = make_plot_from_csv(csv)
        print(f"Saved: {out}")

if __name__ == "__main__":
    main()
