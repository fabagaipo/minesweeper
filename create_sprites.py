from PIL import Image, ImageDraw, ImageFont

def create_cell(size=30, state='covered'):
    img = Image.new('RGB', (size, size), '#c0c0c0')
    draw = ImageDraw.Draw(img)
    
    if state == 'covered':
        # Light gray background with 3D effect
        draw.line([(0, size-1), (0, 0), (size-1, 0)], fill='#ffffff', width=2)  # Top-left highlight
        draw.line([(1, size-1), (size-1, size-1), (size-1, 1)], fill='#808080', width=2)  # Bottom-right shadow
    elif state == 'uncovered':
        # Lighter background for better number visibility
        draw.rectangle([0, 0, size-1, size-1], fill='#d8d8d8')
        draw.rectangle([0, 0, size-1, size-1], outline='#b0b0b0')
    
    return img

def create_mine(size=30):
    img = create_cell(size, 'uncovered')
    draw = ImageDraw.Draw(img)
    
    # Draw mine circle
    padding = size // 4
    draw.ellipse([padding, padding, size-padding-1, size-padding-1], fill='black')
    
    # Draw spikes
    center = size // 2
    spike_length = size // 3
    
    # Horizontal and vertical spikes
    draw.line([(center, padding//2), (center, size-padding//2)], fill='black', width=3)
    draw.line([(padding//2, center), (size-padding//2, center)], fill='black', width=3)
    
    # Diagonal spikes
    draw.line([(padding, padding), (size-padding, size-padding)], fill='black', width=3)
    draw.line([(padding, size-padding), (size-padding, padding)], fill='black', width=3)
    
    # Add highlight
    highlight_pos = padding + 2
    draw.ellipse([highlight_pos, highlight_pos, highlight_pos+4, highlight_pos+4], fill='white')
    
    return img

def create_flag(size=30):
    img = create_cell(size, 'covered')
    draw = ImageDraw.Draw(img)
    
    # Draw flag pole
    pole_x = size * 2 // 3
    draw.line([(pole_x, size//4), (pole_x, size*3//4)], fill='black', width=2)
    
    # Draw triangular flag
    flag_points = [
        (pole_x-2, size//4),  # Top of pole
        (size//3, size*3//8),  # Tip of flag
        (pole_x-2, size//2)    # Bottom of flag
    ]
    draw.polygon(flag_points, fill='#ff0000')
    
    # Draw base
    base_y = size * 3 // 4
    base_width = size // 4
    draw.rectangle([pole_x - base_width//2, base_y, 
                   pole_x + base_width//2, base_y + 2], 
                  fill='black')
    
    return img

def create_wrong_mine(size=30):
    img = create_cell(size, 'uncovered')
    draw = ImageDraw.Draw(img)
    
    # Draw X with thicker lines and better contrast
    padding = size // 4
    # Draw black outline
    for offset in [-1, 0, 1]:
        draw.line([(padding+offset, padding), (size-padding+offset, size-padding)], 
                  fill='black', width=3)
        draw.line([(padding+offset, size-padding), (size-padding+offset, padding)], 
                  fill='black', width=3)
    # Draw red X
    draw.line([(padding, padding), (size-padding, size-padding)], 
              fill='#ff0000', width=2)
    draw.line([(padding, size-padding), (size-padding, padding)], 
              fill='#ff0000', width=2)
    
    return img

def create_number(number, size=30):
    colors = {
        1: '#0000FF',  # Blue
        2: '#008000',  # Green
        3: '#FF0000',  # Red
        4: '#000080',  # Navy
        5: '#800000',  # Maroon
        6: '#008080',  # Teal
        7: '#000000',  # Black
        8: '#808080'   # Gray
    }
    
    # Create uncovered cell as base
    img = create_cell(size, 'uncovered')
    draw = ImageDraw.Draw(img)
    
    # Use a large, bold font
    try:
        font_size = int(size * 0.8)  # Use 80% of cell size
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', size=font_size)
    except:
        font = ImageFont.load_default()
    
    # Draw number
    color = colors.get(number, '#000000')
    number_str = str(number)
    
    # Get text size
    bbox = draw.textbbox((0, 0), number_str, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 1  # Slight upward adjustment
    
    # Draw the number with a subtle shadow for better visibility
    shadow_color = '#FFFFFF'
    shadow_offset = 1
    draw.text((x+shadow_offset, y+shadow_offset), number_str, font=font, fill=shadow_color)
    draw.text((x, y), number_str, font=font, fill=color)
    
    return img

# Create and save all sprites
size = 40  # Larger size for better visibility

def save_image(img, path):
    # Convert to RGB mode and save as GIF (better tkinter compatibility)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.save(path.replace('.png', '.gif'), 'GIF')

# Basic cells
save_image(create_cell(size), 'assets/cell_covered.png')
save_image(create_cell(size, 'uncovered'), 'assets/cell_uncovered.png')

# Mine and flag
save_image(create_mine(size), 'assets/mine.png')
save_image(create_flag(size), 'assets/flag.png')
save_image(create_wrong_mine(size), 'assets/wrong_mine.png')

# Numbers
for i in range(1, 9):
    save_image(create_number(i, size), f'assets/number_{i}.png')
