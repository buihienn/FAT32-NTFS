import os
from MFTEntry import MFTEntry
from TreeDirectory import TreeNode, TreeDirectory

class NTFS:
    info =  [
        "JUMP instruction",
        "OEM ID",
        "Bytes per sector",
        "Sectors per Cluster",
        #"Reserved sectors",
        #"Media descriptor",
        "Sectors per track",
        "Number of heads",
        #"Hidden sectors",
        "Total sectors",
        "$MFT cluster number",
        "$MFTMirr cluster number",
        "Clusters per File Record Segment",
        "Clusters per Index Block",
        "Volume serial number",
        "MFT Entry size",
    ]

    def detectFormat (self, volumePath):
        fileIn = open(r'\\.\%s' % volumePath, 'rb')
        oemID = fileIn.read(512)[0x03:0x0B]
        fileIn.close()
        if oemID == b"NTFS    ":
            return True
        return False
    
    def __init__(self, nameOfVolume):
        self.name = nameOfVolume
        self.curDirectory = [self.name]
        # Doc o dia
        self.fileIn = open(r'\\.\%s' % self.name, 'rb')
        self.bootSectorRaw = self.fileIn.read(0x200)
        
        self.VBR = {}
        self.extractVBR()
        self.MFTSize = self.VBR["MFT Entry size"]

        #Jump to the First MFT Entry
        self.fileIn.seek(self.VBR["$MFT cluster number"] * self.VBR["Sectors per Cluster"] * self.VBR["Bytes per sector"])
        
        #List MFT Entries
        self.MFTList = []
        
        # self.MFTListTest = []
        self.extractMFT()
        self.fileIn.close()
        # self.MFTList[37].header.printTest()

        # print (self.MFTList[38].getFileName())
        # print (self.MFTList[38].getParentId())
        # print (self.MFTList[38].getFileSize())
        # print (self.MFTList[38].getDataTxt(self.name))
        self.getDirectoryTree()

      

    def extractVBR(self):
        self.VBR["JUMP instruction"] = hex(int.from_bytes(self.bootSectorRaw[:3], byteorder= 'little'))
        self.VBR["OEM ID"] = self.bootSectorRaw[3:0xB].decode()
        self.VBR["Bytes per sector"] = int.from_bytes(self.bootSectorRaw[0xB:0xD], byteorder= 'little')
        self.VBR["Sectors per Cluster"] = int.from_bytes(self.bootSectorRaw[0xD:0xE], byteorder= 'little')
        self.VBR["Sectors per track"] = int.from_bytes(self.bootSectorRaw[0x18:0x1A], byteorder='little')
        self.VBR["Number of heads"] = int.from_bytes(self.bootSectorRaw[0x1A:0x1C], byteorder= 'little')
        self.VBR["Total sectors"] = int.from_bytes(self.bootSectorRaw[0x28:0x30], byteorder= 'little')
        self.VBR["$MFT cluster number"] = int.from_bytes(self.bootSectorRaw[0x30:0x38], byteorder= 'little')
        self.VBR["$MFTMirr cluster number"] = int.from_bytes(self.bootSectorRaw[0x38:0x40], byteorder= 'little')
        self.VBR["Clusters per File Record Segment"] = int.from_bytes(self.bootSectorRaw[0x40:0x41], byteorder= 'little', signed = True)
        self.VBR["Clusters per Index Block"] = int.from_bytes(self.bootSectorRaw[0x44:0x48], byteorder= 'little')
        self.VBR["Volume serial number"] = hex(int.from_bytes(self.bootSectorRaw[0x48:0x50], byteorder='little'))
        self.VBR["MFT Entry size"] = 2 ** abs(self.VBR["Clusters per File Record Segment"])

    
    def extractMFT(self):
        count = 0
        while True:
            data = self.fileIn.read(self.MFTSize)  # Đọc một phần dữ liệu từ ổ đĩa
            if len(data) < self.MFTSize:
                break   
            # Kiểm tra xem dữ liệu đọc được có phải là MFT Entry hay không
            if data[:0x04] == b'FILE':
                count += 1
                self.mftData = MFTEntry(data)
                self.MFTList.append(self.mftData)  # lưu MFT
            
    def __str__(self) -> str:
        description = ""
        description += "Volume name: " + self.name
        description += "\nVolume information:\n"
        for attributeName in NTFS.info:
            description += f"{attributeName}: {self.VBR[attributeName]}\n"
        return description
    

    def getChildren(self, currentNode, level):
        if level == 0:
            self.array = {mftEntry.EntryID: 0 for mftEntry in self.MFTList}
        for mftEntry in self.MFTList:
            if  self.array[mftEntry.EntryID] == 0 and mftEntry.EntryID != 5 and mftEntry.EntryID > self.getIDLastSystemEntry() and mftEntry.getParentId() == currentNode.id:
                self.array[mftEntry.EntryID] = 1
                if mftEntry.isDirectory() and mftEntry.getFileName() != "$RECYCLE.BIN":
                    node = TreeNode(mftEntry.getFileName(), mftEntry.EntryID, mftEntry.getFileSize(), mftEntry.getCreatedTime(), mftEntry.getModified())
                    currentNode.children[mftEntry.getFileName()] = node
                    self.getChildren(node, level + 1)
                if mftEntry.isFile():
                    currentNode.children[mftEntry.getFileName()] = TreeNode(mftEntry.getFileName(), mftEntry.EntryID, mftEntry.getFileSize(), mftEntry.getCreatedTime(), mftEntry.getModified())

    def getIDLastSystemEntry (self):
        for mftEntry in self.MFTList:
            if mftEntry.getFileName() == "Recovery":
                return mftEntry.EntryID
        return 31
    
    def getDirectoryTree(self):
        self.tree = TreeDirectory()
        self.getChildren(self.tree.root, 0)
        self.tree.printTree()
        return self.tree



def getBasename(path):
    # Sử dụng os.path.basename để lấy tên file hoặc thư mục cuối cùng trong đường dẫn
    return os.path.basename(path)
    


# def listAvailableVolumes():
#     # Danh sách các ổ đĩa có sẵn trên hệ thống
#     volumes = [chr(x) + ":" for x in range(65, 91) if os.path.exists(chr(x) + ":")]
#     # In ra danh sách các ổ đĩa
#     if volumes:
#         print("Available volumes:")
#         for i, volume in enumerate(volumes, start=1):
#             print(f"{i}. {volume}")
#     else:
#         print("")



# def main():
#     listAvailableVolumes()
#     ntfs = NTFS("Z:")
#     # if ntfs:
#     #     print (ntfs)
#     """
#     try:
#         # Chọn một ổ đĩa từ danh sách
#         choice = int(input("Choose a volume: ")) - 1
#         selected_volume = volumes[choice]
#     except (ValueError, IndexError):
#         print("Invalid choice!")
#         return
# #     """
# if __name__ == "__main__":
#     main()