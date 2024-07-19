import os
from PIL import Image
from moviepy.editor import ImageSequenceClip
import numpy as np

def load_number_images():
    number_images = {}
    missing_images = []
    assets_dir = 'Assets'  # Directory where images are stored
    
    for i in range(10):
        try:
            number_images[i] = Image.open(os.path.join(assets_dir, f"{i}.png")).convert("RGB")
        except FileNotFoundError:
            missing_images.append(f"{i}.png")
    try:
        number_images['colon'] = Image.open(os.path.join(assets_dir, "colon.png")).convert("RGB")
    except FileNotFoundError:
        missing_images.append("colon.png")
    
    if missing_images:
        print(f"Error, missing image: {', '.join(missing_images)}")
        exit(1)
    
    return number_images

def resize_image_to_max_size(img, max_size):
    """ Resize image to fit within max_size while maintaining aspect ratio. """
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    return img

def create_frame(number_images, hrs, mins, secs, max_size):
    def concatenate_images(images):
        widths, heights = zip(*(img.size for img in images))
        total_width = sum(widths)
        max_height = max(heights)
        new_img = Image.new('RGB', (total_width, max_height))
        x_offset = 0
        for img in images:
            new_img.paste(img, (x_offset, 0))
            x_offset += img.width
        return new_img

    time_string = f"{hrs:02}:{mins:02}:{secs:02}"
    
    images = []
    for char in time_string:
        if char.isdigit():
            img = number_images[int(char)]
        else:
            img = number_images['colon']
        
        # Resize image to match max height while maintaining aspect ratio
        img = resize_image_to_max_size(img, max_size)
        images.append(img)

    frame = concatenate_images(images)
    # Resize final frame to max size to ensure uniformity
    frame = frame.resize(max_size, Image.Resampling.LANCZOS)
    return frame

def timer(hours, minutes, seconds, number_images, max_size):
    total_seconds = hours * 3600 + minutes * 60 + seconds
    frames = []
    while total_seconds >= 0:
        hrs, remainder = divmod(total_seconds, 3600)
        mins, secs = divmod(remainder, 60)
        frame = create_frame(number_images, hrs, mins, secs, max_size)
        frames.append(np.array(frame))
        total_seconds -= 1
    return frames

def stopwatch(duration_hours, number_images, max_size):
    total_seconds = duration_hours * 3600
    frames = []
    for elapsed_seconds in range(total_seconds + 1):
        hrs, remainder = divmod(elapsed_seconds, 3600)
        mins, secs = divmod(remainder, 60)
        frame = create_frame(number_images, hrs, mins, secs, max_size)
        frames.append(np.array(frame))
    return frames

def save_frames_to_video(frames, filename, fps=1):
    if not frames:
        raise ValueError("No frames to save to video.")
    # Check that all frames have the same size
    first_frame_size = frames[0].shape[:2]
    for frame in frames:
        if frame.shape[:2] != first_frame_size:
            raise ValueError("All frames must have the same size.")
    # Try different codecs
    try:
        clip = ImageSequenceClip(frames, fps=fps)
        clip.write_videofile(filename, codec='libx264')  # Default codec
    except Exception as e:
        print(f"Error during video creation: {e}")
        print("Trying with an alternative codec...")
        try:
            clip = ImageSequenceClip(frames, fps=fps)
            clip.write_videofile(filename, codec='mpeg4')  # Alternative codec
        except Exception as e:
            print(f"Error during video creation with alternative codec: {e}")
            exit(1)

def main():
    number_images = load_number_images()
    
    # Determine the maximum size among all images
    max_width = max(img.width for img in number_images.values())
    max_height = max(img.height for img in number_images.values())
    max_size = (max_width, max_height)
    
    while True:
        print("Choose an option:")
        print("1. Timer")
        print("2. Stopwatch")
        choice = input("Enter the number of your choice: ")
        
        if choice == '1':
            try:
                hours = int(input("Hours: "))
                minutes = int(input("Minutes: "))
                seconds = int(input("Seconds: "))
                frames = timer(hours, minutes, seconds, number_images, max_size)
                save_frames_to_video(frames, 'timer.mp4', fps=1)
                print("Timer video saved as 'timer.mp4'")
            except ValueError as e:
                print(f"Error: {e}")
        elif choice == '2':
            try:
                duration_hours = int(input("Duration in hours: "))
                frames = stopwatch(duration_hours, number_images, max_size)
                save_frames_to_video(frames, 'stopwatch.mp4', fps=1)
                print("Stopwatch video saved as 'stopwatch.mp4'")
            except ValueError as e:
                print(f"Error: {e}")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
