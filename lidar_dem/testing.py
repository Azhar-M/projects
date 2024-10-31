import numpy as np
import matplotlib.pyplot as plt


POLE_HEIGHT = 100
GROUND_LEVEL = 0
TERRAIN_LENGTH = 1000
MAX_HEIGHT = 25
DISTANCE_STEP = 1
# Create an array of 30 numbers representing the height (0-10) of a land cross-section
# Initialize the array

# np.random.seed(0)  # for reproducibility
land_heights_gradual = [np.random.randint(GROUND_LEVEL, MAX_HEIGHT)]
# land_heights_gradual = [0 for _ in range(TERRAIN_LENGTH)]
# land_heights_gradual[100] = 10
# land_heights_gradual[200] = 20
# land_heights_gradual[300] = 30
shadow_arr = [1 for _ in range(TERRAIN_LENGTH)]
# Define the maximum change in height between neighboring points for gradual transitions
max_step = 1


# Generate heights with gradual progression
for _ in range(TERRAIN_LENGTH - 1):  # 29 more points to reach 30
    change = np.random.randint(-max_step, max_step + 1)  # Random step between -2 and 2
    new_height = max(
        GROUND_LEVEL, min(MAX_HEIGHT, land_heights_gradual[-1] + change)
    )  # Keep heights within 0 and 10
    land_heights_gradual.append(new_height)

#######################################################################################
# delta_x = 1
shadow_index = 0
for i in range(len(land_heights_gradual) - 1):
    if land_heights_gradual[i + 1] > land_heights_gradual[shadow_index]:
        # Shadow cannot be cast
        shadow_index = i + 1
        continue
    # Shadow could be cast?
    # Calculate expected height for next block
    # print("LAND HEIGHTS:", land_heights_gradual[i])
    delta_x = ((i + 1) - shadow_index) * DISTANCE_STEP
    delta_h = ((delta_x * POLE_HEIGHT) / i) if i else 0
    # Shadow is cast
    if land_heights_gradual[i + 1] < land_heights_gradual[shadow_index] - delta_h:
        # shadow_index = i
        shadow_arr[i + 1] = 0  # land_heights_gradual[i + 1]
    else:
        shadow_index = i + 1


#######################################################################################

# Overlay the shadow with the plot:
x_location = [i for i in range(TERRAIN_LENGTH)]

# Plot a histogram of the array
plt.figure(figsize=(8, 5))
# plt.hist(land_heights, bins=range(12), edgecolor='black', align='left', color='skyblue')
# plt.plot(land_heights_gradual)
plt.scatter(GROUND_LEVEL, POLE_HEIGHT)
plt.scatter(x_location, land_heights_gradual, c=shadow_arr, s=0.8)
# plt.scatter(x_location, shadow_arr)  # , s=0.5)
# plt.title("Histogram of Land Heights")
# plt.xlabel("Height")
# plt.ylabel("Frequency")
# plt.xticks(range(11))
plt.show()
