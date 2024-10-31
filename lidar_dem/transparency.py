from PIL import Image

# Open the PNG image
image = Image.open("Screenshot 2024-10-30 143403.png").convert("RGBA")

# Get the data of the image
data = image.getdata()

# Define the transparency level (0 to 255, where 0 is fully transparent and 255 is fully opaque)
transparency_level = 200  # Example: 50% transparency

# Create a new data list with adjusted transparency
new_data = []
for item in data:
    # Change the alpha value to the desired transparency level
    new_data.append((item[0], item[1], item[2], transparency_level))

# Update the image data with the new transparency values
image.putdata(new_data)

# Save the new image
# image.save(r"C:\Users\User\Documents\azhar_local_code\ikeja\new_image.png")
image.save(r"C:\Users\User\Pictures\new_image.png")

print("Transparency adjusted and new image saved.")