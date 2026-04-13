import cupy as cp

def add_alpha_GPU(img):
    if img.shape[2] == 3:  # Add alpha channel if missing
        # Create an alpha channel of 255 (fully opaque) on the GPU
        alpha_channel = cp.ones((img.shape[0], img.shape[1], 1), dtype=img.dtype) * 255
        # Concatenate the alpha channel to the input image
        return cp.concatenate((img, alpha_channel), axis=2)
    return img


def overlay_images_GPU(image2, image1, offset_x, offset_y):
    """
    Overlays image2 onto image1 at cords
    """
    # Ensure both images have alpha channels
    image1 = add_alpha_GPU(image1)
    image2 = add_alpha_GPU(image2)

    x_min = min(0, offset_x)
    y_min = min(0, offset_y)
    x_max = max(image1.shape[1], offset_x + image2.shape[1])
    y_max = max(image1.shape[0], offset_y + image2.shape[0])

    canvas_width = x_max - x_min
    canvas_height = y_max - y_min

    canvas = cp.zeros((canvas_height, canvas_width, 4), dtype=image1.dtype)
    y1_start = -y_min
    x1_start = -x_min
    canvas[y1_start:y1_start + image1.shape[0], x1_start:x1_start + image1.shape[1]] = image1

    y2_start = offset_y - y_min
    x2_start = offset_x - x_min
    overlay_region = canvas[y2_start:y2_start + image2.shape[0], x2_start:x2_start + image2.shape[1]]

    # Split RGBA channels
    r1, g1, b1, a1 = cp.dsplit(overlay_region, 4)
    r2, g2, b2, a2 = cp.dsplit(image2, 4)

    #alpha channels to [0, 1]
    a1 = a1 / 255.0
    a2 = a2 / 255.0

    # Blend images
    r = r1 * (1 - a2) + r2 * a2
    g = g1 * (1 - a2) + g2 * a2
    b = b1 * (1 - a2) + b2 * a2
    a = cp.clip(a1 + a2 * (1 - a1), 0, 1)

    #combine
    blended_region = cp.dstack((r, g, b, a * 255)).astype(cp.uint8)

    canvas[y2_start:y2_start + image2.shape[0], x2_start:x2_start + image2.shape[1]] = blended_region

    return canvas, 0, 0


