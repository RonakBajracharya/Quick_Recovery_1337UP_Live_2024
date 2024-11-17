from PIL import Image, ImageDraw
from itertools import permutations

# Load the QR code image
qr_code_image = Image.open("qr.png")
width, height = qr_code_image.size
half_width, half_height = width // 2, height // 2

# Define the squares
squares = {
    "1": (0, 0, half_width, half_height),
    "2": (half_width, 0, width, half_height),
    "3": (0, half_height, half_width, height),
    "4": (half_width, half_height, width, height)
}

# Function to split squares into triangles
def split_square_into_triangles(img, box):
    x0, y0, x1, y1 = box
    a_triangle_points = [(x0, y0), (x1, y0), (x0, y1)]
    b_triangle_points = [(x1, y1), (x1, y0), (x0, y1)]

    def crop_triangle(points):
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.polygon(points, fill=255)
        triangle_img = Image.new("RGBA", img.size)
        triangle_img.paste(img, (0, 0), mask)
        return triangle_img.crop((x0, y0, x1, y1))

    return crop_triangle(a_triangle_points), crop_triangle(b_triangle_points)

# Prepare triangle images
triangle_images = {}
for key, box in squares.items():
    triangle_images[f"{key}a"], triangle_images[f"{key}b"] = split_square_into_triangles(qr_code_image, box)

# Get all permutations of orders
orders = list(permutations(["1", "2", "3", "4"]))

# Iterate through all permutations
for a_order_tuple in orders:
    a_order = list(a_order_tuple)
    b_order = list(reversed(a_order))

    # Create a new reconstructed image
    reconstructed_image = Image.new("RGBA", qr_code_image.size)

    # Define positions for the final assembly
    final_positions = [
        (0, 0),
        (half_width, 0),
        (0, half_height),
        (half_width, half_height)
    ]

    # Assemble the new image
    for i in range(4):
        a_triangle = triangle_images[f"{a_order[i]}a"]
        b_triangle = triangle_images[f"{b_order[i]}b"]
        combined_square = Image.new("RGBA", (half_width, half_height))
        combined_square.paste(a_triangle, (0, 0))
        combined_square.paste(b_triangle, (0, 0), b_triangle)
        reconstructed_image.paste(combined_square, final_positions[i])

    # Save the image with the appropriate filename
    output_filename = f"{''.join(a_order)}_{''.join(b_order)}.png"
    reconstructed_image.save(output_filename)
    print(f"Saved: {output_filename}")
