import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

def los(coord_dict, tower_coords):
    # Extract x, y, z values from coord_dict
    x = np.array([coord['x'] for coord in coord_dict])
    y = np.array([coord['y'] for coord in coord_dict])
    z = np.array([coord['z'] for coord in coord_dict])
    
    # Extract tower coordinates and radius
    tower_x = tower_coords['x']
    tower_y = tower_coords['y']
    tower_z = tower_coords['z']
    r = tower_coords['rad']
    
    # Create a meshgrid
    x_1, y_1 = np.meshgrid(np.unique(x), np.unique(y))
    
    # Initialize z array with values between 0 and 20
    z_1 = np.zeros_like(x_1, dtype=float)
    for coord in coord_dict:
        xi = np.where(x_1[0] == coord['x'])[0][0]
        yi = np.where(y_1[:, 0] == coord['y'])[0][0]
        z_1[yi, xi] = coord['z']
    
    # Set the tower's coordinates to the specified z value
    tower_index = (x_1 == tower_x) & (y_1 == tower_y)
    z_1[tower_index] = tower_z
    
    # Plot the points using plt.imshow
    plt.imshow(z_1, extent=(x.min(), x.max(), y.min(), y.max()), origin='lower', cmap='plasma')
    plt.colorbar(label='Z value')
    
    # Highlight the tower's coordinates in red
    plt.scatter(tower_x, tower_y, color='red', marker='o')
    
    # Draw a circle centered at the tower's coordinates with the specified radius
    circle = plt.Circle((tower_x, tower_y), r, color='white', fill=False)
    plt.gca().add_patch(circle)
    
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Line of Sight Plot')
    plt.grid(True)
    plt.axis('equal')  # Ensure the aspect ratio is equal to make the circle look like a circle

def draw_radial_lines(coord_dict, tower_coords):
    # Call the los function to plot the initial setup
    los(coord_dict, tower_coords)
    
    # Extract tower coordinates and radius
    tower_x = tower_coords['x']
    tower_y = tower_coords['y']
    tower_z = tower_coords['z']
    r = tower_coords['rad']
    
    # Draw radial lines from the center point to the points where z < tower_coords['z']
    for coord in coord_dict:
        if coord['z'] < tower_z:
            # Calculate the direction vector
            dx = coord['x'] - tower_x
            dy = coord['y'] - tower_y
            distance = np.sqrt(dx**2 + dy**2)
            
            # Normalize the direction vector and scale to the circle radius
            if distance != 0:
                dx = dx / distance * r
                dy = dy / distance * r
            
            # Draw the line from the center to the circle radius
            plt.plot([tower_x, tower_x + dx], [tower_y, tower_y + dy], color='white', linestyle='--')
    
    plt.show()

# Example usage with finer-grained coord_dict
coord_dict = [
    {'x': x, 'y': y, 'z': 10}
    for x in range(-10, 11, 2)
    for y in range(-10, 11, 2)
]

tower_coords = {'x': 0, 'y': 0, 'z': 30, 'rad': 9}

draw_radial_lines(coord_dict, tower_coords)