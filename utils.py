import json
import os
import shutil

from tqdm import tqdm


with open("settings.json", "r") as file:
    settings = json.load(file)

class SortingFiles:
    def __init__(self):
        with open(settings["bad_tlds_list"], 'r') as file:
            bad_tlds = file.readlines()

        with open(settings["bad_domains_list"], 'r') as file:
            domains = file.readlines()

        self.tlds = bad_tlds
        self.domains = domains

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
sorting_files = SortingFiles()

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

    total = sum(1 for _ in open(input_file, 'r', errors="replace"))

    with open(input_file, "r", encoding="utf-8", errors="replace") as f:
        for fline in tqdm(f, total=total):

            line = fline.strip()
            clean_line = line.replace(" ", "")
            if not len(clean_line.split("@")) > 1: continue

            domain = clean_line.split("@")[1].split(":")[0].lower()

            if len(domain) < 2: continue

            if not any(ue in domain for ue in sorting_files.domains):
                if not any(b + "." in line or b + "/" in line or b + "\\" in domain for b in sorting_files.tlds):
                    save_list(clean_line.strip())
                else:
                    save_trash_list(clean_line.strip())
            else:
                save_trash_list(clean_line.strip())

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