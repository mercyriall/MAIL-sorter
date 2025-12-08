from utils import *
import json
from colorama import init, Fore
init(autoreset=True)


with open("settings.json", "r") as file:
    settings = json.load(file)


def run():
    input("==Any button for start==")

    if not check_start_dirs():
        print(f"==Directories not found "
              f"{Fore.RED}{{{settings['input_dir']}{Fore.RESET}"
              f" or {Fore.RED}{settings['output_dir']}}}{Fore.RESET}==")
        input("==Any button for exit==")
        return 0

    files_name: list = get_input_files()
    if not files_name:
        print(Fore.RED + "==Input files not found==")
        input("==Any button for exit==")
        return 0

    for i in range(len(files_name)):
        print(f"=={files_name[i]} -> {i}/{len(files_name)}==")
        if not sorting_ulp_list(files_name[i]):
            print(Fore.RED + f"=={files_name[i]} sorting error not found==")

    close_all_files()
    print(Fore.GREEN + "==All done!==")
    input("==Any button for exit==")
    return 0

if __name__ == '__main__':
    run()