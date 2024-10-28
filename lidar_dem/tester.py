import numpy as np
import matplotlib.pyplot as plt

def generate_lidar_data(grid_size, z_min, z_max, mean_z, std_z):
    data = []
    for x in range(-grid_size, grid_size + 1):
        for y in range(-grid_size, grid_size + 1):
            z = np.clip(np.random.normal(mean_z, std_z), z_min, z_max)
            data.append({'x': x, 'y': y, 'z': z})
    return data

def calculate_los(data, tower):
    output_data = []
    tower_x, tower_y, tower_z = tower
    radius = 600
    grid = {(point['x'], point['y']): point['z'] for point in data}
    
    for point in data:
        x, y, z = point['x'], point['y'], point['z']
        distance = np.sqrt((x - tower_x)**2 + (y - tower_y)**2)
        if distance > radius:
            los = 0
        else:
            los = 1
            # Check for shadow casting
            num_steps = int(distance)
            for step in range(1, num_steps + 1):
                intermediate_x = int(tower_x + step * (x - tower_x) / distance)
                intermediate_y = int(tower_y + step * (y - tower_y) / distance)
                if (intermediate_x, intermediate_y) in grid:
                    intermediate_z = grid[(intermediate_x, intermediate_y)]
                    if intermediate_z > tower_z:
                        los = 0
                        break
        output_data.append({'x': x, 'y': y, 'los': los})
    return output_data

def visualize_data(data, tower):
    x_coords = [point['x'] for point in data]
    y_coords = [point['y'] for point in data]
    los_values = [point['los'] for point in data]

    colors = ['green' if los == 1 else 'red' for los in los_values]

    plt.scatter(x_coords, y_coords, c=colors)
    plt.scatter(tower[0], tower[1], c='blue', marker='o', s=100, label='Tower')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('DEM Map with Line of Sight')
    plt.legend()
    plt.show()

# Parameters
grid_size = 100
z_min = 3
z_max = 35
mean_z = 19
std_z = 8
tower = (0, 0, 30)

# Generate Lidar Data
lidar_data = generate_lidar_data(grid_size, z_min, z_max, mean_z, std_z)

# Calculate Line of Sight
output_data = calculate_los(lidar_data, tower)

# Visualize Data
visualize_data(output_data, tower)