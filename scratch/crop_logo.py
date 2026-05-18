from PIL import Image, ImageDraw
import numpy as np

img_path = r"c:\Users\hp\OneDrive\Desktop\django\CleanPortal\accounts\static\accounts\images\newlogo.png"
img = Image.open(img_path).convert("RGBA")
data = np.array(img)

# Corner background color
bg_color = data[0, 0]
print(f"Background color: {bg_color}")

# Distance from background to identify the emblem pixels
dist = np.linalg.norm(data[:, :, :3].astype(float) - bg_color[:3].astype(float), axis=2)
non_bg = dist > 15

# Crop strictly to the emblem rows (90 to 640)
y_indices, x_indices = np.where(non_bg)
emblem_mask = (y_indices >= 90) & (y_indices <= 640)
emblem_y = y_indices[emblem_mask]
emblem_x = x_indices[emblem_mask]

min_y, max_y = emblem_y.min(), emblem_y.max()
min_x, max_x = emblem_x.min(), emblem_x.max()

print(f"Emblem bounding box: X: ({min_x}, {max_x}), Y: ({min_y}, {max_y})")

# Crop the emblem
emblem = img.crop((min_x, min_y, max_x, max_y))

# Let's make it a perfect square
w, h = emblem.size
size = max(w, h)
square_emblem = Image.new("RGBA", (size, size), (255, 255, 255, 0))
# Center the emblem inside the square
square_emblem.paste(emblem, ((size - w) // 2, (size - h) // 2))

# Make it a clean circular mask to remove any residual background corners
mask = Image.new("L", (size, size), 0)
draw = ImageDraw.Draw(mask)
# Draw a solid circle
draw.ellipse((0, 0, size, size), fill=255)

# Apply mask to alpha channel
final_emblem = Image.new("RGBA", (size, size), (255, 255, 255, 0))
final_emblem.paste(square_emblem, (0, 0), mask=mask)

# Save the emblem
out_path = r"c:\Users\hp\OneDrive\Desktop\django\CleanPortal\accounts\static\accounts\images\newlogo_emblem.png"
final_emblem.save(out_path)
print(f"Saved transparent emblem logo to {out_path}")
