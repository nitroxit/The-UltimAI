import win32api
import time
import os
import uuid
import ctypes
import numpy as np
import cv2
import mss

# Configuration
toggle_key = 0xBE  # Virtual key code for the period (.)
image_size = 640  # Size of the screenshots
screenshot_interval = 0.25  # Delay between screenshots in seconds
images_folder_path = 'images'

# Screen dimensions
half_screen_x = int(ctypes.windll.user32.GetSystemMetrics(0) / 2)
half_screen_y = int(ctypes.windll.user32.GetSystemMetrics(1) / 2)
camera = mss.mss()
last_screenshot_time = 0
screenshot_enabled = False  # Screenshot functionality toggle
screenshot_count = 0

# Define the bounding box for the screenshot
screenshot_area = {
    'left': int(half_screen_x - image_size // 2),
    'top': int(half_screen_y - image_size // 2),
    'width': int(image_size),
    'height': int(image_size)
}

# Create the images folder if it doesn't exist
if not os.path.exists(images_folder_path):
    print('Creating images folder...')
    os.mkdir(images_folder_path)

# Helper Functions
def is_left_mouse_button_pressed():
    """Check if the left mouse button is pressed."""
    return win32api.GetKeyState(0x01) < 0

def is_toggle_key_pressed():
    """Check if the toggle key (period key) is pressed."""
    return win32api.GetAsyncKeyState(toggle_key) & 0x8000  # High bit indicates key press

# Main Loop
print("Press '.' to toggle screenshot functionality on or off.")
while True:
    # Check if the toggle key (period) is pressed
    if is_toggle_key_pressed():
        screenshot_enabled = not screenshot_enabled
        print(f'Screenshot functionality {"enabled" if screenshot_enabled else "disabled"}')
        time.sleep(0.3)  # Debounce to prevent rapid toggling

    if screenshot_enabled and is_left_mouse_button_pressed():
        current_time = time.perf_counter()
        if current_time - last_screenshot_time > screenshot_interval:
            screenshot_frame = np.array(camera.grab(screenshot_area))
            if screenshot_frame is not None:
                screenshot_name = f'image{screenshot_count + 1}.jpg'  # Sequential naming
                screenshot_path = os.path.join(images_folder_path, screenshot_name)
                cv2.imwrite(screenshot_path, screenshot_frame)
                last_screenshot_time = current_time
                screenshot_count += 1
                print(f'Screenshot saved: {screenshot_path} (Total screenshots: {screenshot_count})')