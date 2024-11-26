import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, help="path to directory with files to be renamed")
    parser.add_argument("-pr", "--prefix", type=str, default="", help="prefix to be added to filenames")
    parser.add_argument("-sf", "--suffix", type=str, default="", help="suffix to be added to filenames")
    parser.add_argument("-r", "--remove", type=str, default="", help="text to be removed from filenames")
    parser.add_argument("-sw", "--switch", type=str, default="", help="text to removed if is present or added if is not")
    return parser.parse_args()

def rename_files_in_directory(directory, prefix="", suffix="", remove="", switch="", start_index=1):
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        files.sort()

        for i, file in enumerate(files, start=start_index):
            file_extension = os.path.splitext(file)[1]
            new_core = file.replace(remove, "").replace(file_extension, "")
            if switch in new_core:
                new_core = new_core.replace(switch, "")
            else:
                new_core = f"{new_core}{switch}"
            new_name = f"{prefix}{new_core}{suffix}{file_extension}"
            print(f"{file} -> {new_name}")
            old_path = os.path.join(directory, file)
            new_path = os.path.join(directory, new_name)
            os.rename(old_path, new_path)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("renaming...")
    args = parse_args()

    rename_files_in_directory(args.path, args.prefix, args.suffix, args.remove, args.switch)
