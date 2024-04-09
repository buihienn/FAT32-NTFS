import cmd
from typing import Union
from FAT32 import FAT32
class UI(cmd.Cmd):
    intro = ("COMMANDS LIST.\n"
             "1. Type 'info' to print information of volume.\n"
             "2. Type 'tree' to print root directory tree.\n"
             "3. Type 'data + filename' to retrieve file content.\n"
             "     - First, you have to be into the directory that contains this file.\n"
             "4. Type 'cd + directory' to change the current directory.\n"
             "5. Type 'exit' to quit the program.\n")

    def __init__(self, fat32_volume) -> None:
        super().__init__()
        self.volume = fat32_volume
        self.updateDirectory()

    def updateDirectory(self):
        UI.prompt = f'┌──[{self.volume.getCWD()}]\n└──$ '

    def do_cd(self, arg):
        try:
            self.volume.move_to_directory(arg)
            self.updateDirectory()
        except Exception as e:
            print(f"[ERROR] {e}")

    def do_tree(self, arg):
        def printTree(entry, prefix="", last=False):
            print(f'{prefix + ("└── " if last else "├── ") + entry["Name"]:<40}', end=' ')
            
            # Print status of file/folder
            entryStatus = entry["Name"][:1]
            if entryStatus == b'\xe5':
                print(f'{"| Deleted":<30}', end="  ")
            elif entryStatus == b'\x00':
                print(f'{"| Empty":<30}', end="  ")
            elif entryStatus == b'\x05':
                print(f'{"| Initial character is 0xE5":<30}', end="  ")
            else:
                print(f'{"| DOT Entry":<30}', end="  ")

            # Print size of file/folder
            print("| Size: " + str(entry["Size"]))

            # Check if it's an archive
            if entry["Flags"] & 0b100000:
                return

            self.volume.move_to_directory(entry["Name"])
            entries = self.volume.get_directory_info()
            numberOfEntry = len(entries)

            for i in range(numberOfEntry):
                if entries[i]["Name"] in (".", ".."):
                    continue
                prefixChar = "    " if last else "│   "
                printTree(entries[i], prefix + prefixChar, i == numberOfEntry - 1)

            self.volume.move_to_directory("..")

        cwd = self.volume.getCWD()
        try:
            print(cwd)
            entries = self.volume.get_directory_info()
            numberOfEntry = len(entries)

            for i in range(numberOfEntry):
                if entries[i]["Name"] in (".", ".."):
                    continue
                printTree(entries[i], "", i == numberOfEntry - 1)

        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            self.volume.move_to_directory(cwd)

    def do_data(self, arg):
        if arg == "":
            print(f"[ERROR] Please provide a path")
            return
        try:
            print(self.volume.get_File_content(arg))

        except Exception as e:
            print(f"[ERROR] {e}")

    def do_info(self, arg):
        print(self.volume)

    def do_exit(self, arg):
        print('Exit the program...')
        self.close()
        return True

    def close(self):
        if self.volume:
            del self.volume
            self.volume = None