from NTFS import NTFS
import os

def listAvailableVolumes():
    # Danh sách các ổ đĩa có sẵn trên hệ thống
    volumes = [chr(x) + ":" for x in range(65, 91) if os.path.exists(chr(x) + ":")]
    # In ra danh sách các ổ đĩa
    if volumes:
        print("Available volumes:")
        for i, volume in enumerate(volumes, start=1):
            print(f"{i}. {volume}")
    else:
        print("")


def main():
    # list_volume = []
    
    # for volume in range(ord('A'), ord('Z')):
    #     if os.path.exists(chr(volume) + ":"):
    #         list_volume.append(chr(volume) + ":")
            
    # print("Volume list:")

    # for i, volume_path in enumerate(list_volume):
    #     print(f"{i + 1}/", volume_path)

    volumes = [chr(x) + ":" for x in range(65, 91) if os.path.exists(chr(x) + ":")]
    # In ra danh sách các ổ đĩa
    if volumes:
        print("Available volumes:")
        for i, volume in enumerate(volumes, start=1):
            print(f"{i}. {volume}")
    else:
        print("")

    try:
        choice = int(input("Choose a volume: "))
        if choice <= 0 or choice > len(volumes):
            raise ValueError("Invalid choice!")
    except ValueError as e:
        print(f"[ERROR] {e}")
        return
    
    volumePath = volumes[choice - 1]
    vol = NTFS(volumePath)
    while True:
        print("\nMenu:")
        print("1. Check if volume is FAT32")
        print("2. Display directory tree")
        print("3. Delete file")
        print("4. Exit")
        
        try:
            choice = int(input("Choose an option: "))
            if choice == 1:
                if vol.detectFormat(volumePath):
                    print("Volume is NTFS")
                else:
                    print("Volume is not FAT32.")
            elif choice == 2:
                tree = vol.getDirectoryTree()
                print("Directory Tree:")
                tree.printTree()
            elif choice == 3:
                file_name = input("Enter file name to delete: ")
                vol.delete_object(file_name)
            elif choice == 4:
                print("Exiting program.")
                break
            else:
                print("Invalid choice!")
        except ValueError as e:
            print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()