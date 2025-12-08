import json
import os
import shutil

from tqdm import tqdm


with open("settings.json", "r") as file:
    settings = json.load(file)


class FileControl:
    def __init__(self):
        self.good_file = None
        self.trash_file = None

    def open_new_good_file(self, path, flag):
        if self.good_file is not None: self.good_file.close()
        self.good_file = open(path, flag, encoding="utf-8", errors="replace")

    def open_new_trash_file(self, path, flag):
        if self.trash_file is not None: self.trash_file.close()
        self.trash_file = open(path, flag, encoding="utf-8", errors="replace")

    def close_all_files(self):
        self.good_file.close()
        self.trash_file.close()


class SizeControl:
    good_current_size: int = 0
    good_file_index: int = 1

    trash_current_size: int = 0
    trash_file_index: int = 1

    def __init__(self, restrictions):
        self.restrictions = restrictions

    def size_good_up(self):
        self.good_current_size = self.good_current_size + 1

    def refresh_goods(self):
        self.good_current_size = 0
        self.good_file_index += 1

    def size_trash_up(self):
        self.trash_current_size = self.trash_current_size + 1

    def refresh_trashes(self):
        self.trash_current_size = 0
        self.trash_file_index += 1

size_control = SizeControl(settings["restrictions_lines_per_one_file"])
file_control = FileControl()

def check_start_dirs() -> bool:
    if os.path.isdir(settings['input_dir']) and os.path.isdir(settings['output_dir']):
        for name in os.listdir(settings["output_dir"]):
            file_path = os.path.join(settings["output_dir"], name)
            if os.path.isfile(file_path):
                if ".gitkeep" not in name:
                    os.remove(file_path)

        shutil.rmtree(f"{settings["output_dir"]}/errors", ignore_errors=True)
        os.makedirs(f"{settings["output_dir"]}/errors")

        return True
    else:
        return False


def get_input_files() -> list:
    dir_path = settings['input_dir']

    files_name = [
        f for f in os.listdir(dir_path)
        if os.path.isfile(os.path.join(dir_path, f)) and not f.startswith(".")
    ]

    return files_name


def sorting_ulp_list(file_name: str):
    input_file = os.path.join(settings["input_dir"], file_name)

    # Read bad tlds once
    with open(settings["bad_tlds_list"], "r", encoding="utf-8") as f:
        bad_tlds = {line.strip() for line in f}

    total = sum(1 for _ in open(input_file, 'r', errors="replace"))

    with open(input_file, "r", encoding="utf-8", errors="replace") as f:
        for fline in tqdm(f, total=total):
            line = fline.strip()
            if len(line) < 5: continue
            clean = line.replace(" ", "")

            # Check useful endpoints
            if any(ue in line for ue in settings["useful_endpoints"]):

                # Check bad tlds
                if not any(b + "." in line or b + "/" in line or b + "\\" in line for b in bad_tlds):
                    save_list(clean.strip())
                else:
                    save_trash_list(clean.strip())
            else:
                save_trash_list(clean.strip())

    return True


def save_list(sorted_line: str):
    if size_control.good_current_size >= size_control.restrictions:
        size_control.refresh_goods()

        file_control.open_new_good_file(f"{settings['output_dir']}/{size_control.good_file_index}.txt", "a")

    size_control.size_good_up()

    if file_control.good_file is None:
        file_control.open_new_good_file(f"{settings['output_dir']}/{size_control.good_file_index}.txt", "a")
    file_control.good_file.write(sorted_line + "\n")


def save_trash_list(trash_line: str):
    if size_control.trash_current_size >= size_control.restrictions:
        size_control.refresh_trashes()

        file_control.open_new_trash_file(f"{settings['output_dir']}/errors/{size_control.trash_file_index}.txt", "a")

    size_control.size_trash_up()

    if file_control.trash_file is None:
        file_control.open_new_trash_file(f"{settings['output_dir']}/errors/{size_control.trash_file_index}.txt", "a")
    file_control.trash_file.write(trash_line + "\n")


def close_all_files():
    file_control.close_all_files()