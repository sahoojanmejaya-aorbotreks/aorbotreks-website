from rembg import remove
from PIL import Image

def remove_background(input_path, output_path):
    input_image = Image.open(input_path)
    output_image = remove(input_image)
    output_image.save(output_path)
    print(f"Background removed successfully! Output saved as '{output_path}'")

# Process both images
images = [
    ('Woman receiving a spam letter.png', 'woman_nobg.png'),
    ('refer.jpg', 'refer_nobg.png')
]

for input_path, output_path in images:
    remove_background(input_path, output_path)
