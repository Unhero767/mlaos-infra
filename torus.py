import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

# Torus parameters
R = 3  # Major radius
r = 1  # Minor radius
num_points = 200

# Parameters for torus grid
t = np.linspace(0, 2 * np.pi, num_points)
s = np.linspace(0, 2 * np.pi, num_points)
t, s = np.meshgrid(t, s)

# Function to generate torus coordinates
def torus(R, r, t, s):
    x = (R + r * np.cos(s)) * np.cos(t)
    y = (R + r * np.cos(s)) * np.sin(t)
    z = r * np.sin(s)
    return x, y, z

# Generate base torus coordinates
x, y, z = torus(R, r, t, s)

# Define nodes on torus surface (sampled points)
num_nodes = 40
node_t = np.linspace(0, 2 * np.pi, num_nodes)
node_s = np.linspace(0, 2 * np.pi, num_nodes)
node_t, node_s = np.meshgrid(node_t, node_s)
node_t = node_t.flatten()
node_s = node_s.flatten()

node_x, node_y, node_z = torus(R, r, node_t, node_s)

# Siphon: golden spiral parameters wrapped around torus
golden_ratio = (1 + np.sqrt(5)) / 2
spiral_points = 300
theta = np.linspace(0, 4 * np.pi, spiral_points)
phi = golden_ratio * theta

# Parametric golden spiral on torus
siphon_x = (R + r * np.cos(phi)) * np.cos(theta)
siphon_y = (R + r * np.cos(phi)) * np.sin(theta)
siphon_z = r * np.sin(phi)

# Colors for Quadruple Helix strands (customized)
colors = ['#8A2BE2', '#1E90FF', '#00CED1', '#FF69B4']  # violet, dodger blue, dark turquoise, hot pink

# Setup figure and 3D axis
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')
ax.set_box_aspect([1,1,1])
ax.axis('off')

# Initialize plot elements
lines = [ax.plot([], [], [], lw=3, color=colors[i])[0] for i in range(4)]
siphon_line, = ax.plot([], [], [], lw=4, color='#FFD700', linestyle='--', label='C4 Gold Siphon')  # gold color
nodes_scatter = ax.scatter([], [], [], s=70, c='white', edgecolors='black', label='Neon Veil Nodes')

# Text annotations for real-time data
resonance_text = ax.text2D(0.02, 0.95, "", transform=ax.transAxes, fontsize=12, color='white')
siphon_text = ax.text2D(0.02, 0.91, "", transform=ax.transAxes, fontsize=12, color='gold')
nodes_text = ax.text2D(0.02, 0.87, "", transform=ax.transAxes, fontsize=12, color='cyan')

# Background color for better contrast
fig.patch.set_facecolor('#121212')
ax.set_facecolor('#121212')

# Animation update function
def update(frame):
    ax.clear()
    ax.set_box_aspect([1,1,1])
    ax.axis('off')
    angle = frame / 30  # slower rotation for smoothness

    # Draw Quadruple Helix strands
    for i in range(4):
        phase = i * np.pi / 2
        x_strand = (R + r * np.cos(s + angle + phase)) * np.cos(t + angle + phase)
        y_strand = (R + r * np.cos(s + angle + phase)) * np.sin(t + angle + phase)
        z_strand = r * np.sin(s + angle + phase)
        ax.plot(x_strand.flatten(), y_strand.flatten(), z_strand.flatten(), color=colors[i], lw=3, label=f'Strand {i+1}')

    # Draw siphon spiral with pulsation
    pulsate = 0.1 * np.sin(frame / 15)
    siphon_x_pulse = siphon_x * (1 + pulsate)
    siphon_y_pulse = siphon_y * (1 + pulsate)
    siphon_z_pulse = siphon_z * (1 + pulsate)
    ax.plot(siphon_x_pulse, siphon_y_pulse, siphon_z_pulse, lw=4, color='#FFD700', linestyle='--', label='C4 Gold Siphon')

    # Animate nodes with kinetic pulse color change
    pulse_colors = plt.cm.plasma((np.sin(frame / 7 + node_t * 5) + 1) /
