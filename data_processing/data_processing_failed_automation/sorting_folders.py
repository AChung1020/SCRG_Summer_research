import os
import shutil

def sort_images(base_dir, is_thermal):
    image_type = "thermal" if is_thermal else "optical"
    
    for subdir in os.listdir(base_dir):
        subdir_path = os.path.join(base_dir, subdir)
        if not os.path.isdir(subdir_path):
            continue

        # Create output directories for this subdirectory
        output_dirs = {
            'ProOne_even': os.path.join(subdir_path, f'even_ProOne_{image_type}'),
            'ProOne_odd': os.path.join(subdir_path, f'odd_ProOne_{image_type}'),
            'E8XT_even': os.path.join(subdir_path, f'even_E8XT_{image_type}'),
            'E8XT_odd': os.path.join(subdir_path, f'odd_E8XT_{image_type}')
        }

        # Create directories if they do not exist
        for dir_path in output_dirs.values():
            os.makedirs(dir_path, exist_ok=True)

        # Sort files in this subdirectory
        for filename in os.listdir(subdir_path):
            if filename.endswith(f"_{image_type}.jpg"):
                base_name = os.path.splitext(filename)[0].replace(f"_{image_type}", "")
                parts = base_name.split('_')
                if len(parts) < 4:
                    continue
                model = parts[2]
                try:
                    number = int(parts[3])
                except ValueError:
                    continue

                if 'ProOne' in filename:
                    subdir_type = 'ProOne_even' if number % 2 == 0 else 'ProOne_odd'
                elif 'E8XT' in filename:
                    subdir_type = 'E8XT_even' if number % 2 == 0 else 'E8XT_odd'
                else:
                    continue

                src_path = os.path.join(subdir_path, filename)
                dst_path = os.path.join(output_dirs[subdir_type], filename)
                shutil.move(src_path, dst_path)

        print(f"Sorted {image_type} images in {subdir}")

def main():
    thermal_dir = r'C:\Users\andre\OneDrive\Desktop\SCRG\Thermal Images'
    visible_dir = r'C:\Users\andre\OneDrive\Desktop\SCRG\Optical Images'

    sort_images(thermal_dir, is_thermal=True)
    sort_images(visible_dir, is_thermal=False)

    print("All files have been sorted into their respective directories.")

if __name__ == "__main__":
    main()