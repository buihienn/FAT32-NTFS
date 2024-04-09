from NTFSAttribute import Attribute

class MFTEntry:
    # FILE_DELETED = 0x00
    # FILE_IN_USE = 0x01
    # Directory_DELETED = 0x02
    # Directory_IN_USE = 0x03

    def __init__(self, data): #data: bytes
        # MFT Entry Header
        self.signature = data[0x00:0x04] # Dùng 4 byte đầu tiên làm chữ ký
        self.update_seq_offset = int.from_bytes(data[0x04:0x06], byteorder='little')  
        self.update_seq_size = int.from_bytes(data[0x06:0x08], byteorder='little')  
        self.log_file_seq_num = int.from_bytes(data[0x08:0x10], byteorder='little')  
        self.seq_num = int.from_bytes(data[0x10:0x12], byteorder='little') 
        self.hard_link_count = int.from_bytes(data[0x12:0x14], byteorder='little')  
        self.offset_first_attr = int.from_bytes(data[0x14:0x16], byteorder='little')  
        self.flag = int.from_bytes(data[0x16:0x18], byteorder='little')  

        self.used_entry_size = int.from_bytes(data[0x18:0x1C], byteorder='little')  
        self.allocated_entry_size = int.from_bytes(data[0x1C:0x20], byteorder='little') 
        self.base_entry_ref = int.from_bytes(data[0x20:0x28], byteorder='little') 
        self.next_attr_id = int.from_bytes(data[0x28:0x2A], byteorder='little')  
        self.EntryID = int.from_bytes(data[0x2C:0x30], byteorder='little') 

        if self.signature != b"FILE":
            return
        
        attrData = data[self.offset_first_attr:]
    
        offset = 0
        self.AttrList = []
        #
        while offset < len(attrData):
            attribute = Attribute(attrData, offset)
            if (attribute.attrType == 0xFFFFFFFF):
                break
            self.AttrList.append(attribute)
            offset += attribute.sizeAttr

    def getFlag(self):
        return self.flag

    def getFileName(self):
        for a in self.AttrList:
            if a.attrType == 0x30:
                return a.fileName
        return None
    
    def getParentId(self):
        for a in self.AttrList:
            if a.attrType == 0x30:
                return a.IdParentFolder
        return None

    def getCreatedTime(self):
        for a in self.AttrList:
            if a.attrType == 0x10:
                return a.dateCreated
        return None
    
    def getModified(self):
        for a in self.AttrList:
            if a.attrType == 0x10:
                return a.dateModified
        return None

    def getFileSize(self):
        for a in self.AttrList:
            if a.attrType == 0x80:
                return a.realSize
        return 0

    def isFile(self):
        return self.flag == 0x01
    
    def isDirectory(self):
        return self.flag == 0x03
    
    def getAttribute(self):
        for a in self.AttrList:
            if a.attrType == 0x30:
                return a.objectAttributeList
        return None
    

    def isSystemOrHidden(self):
        objectAttributeList = self.getAttribute()
        print (objectAttributeList[0])
        for attr in objectAttributeList:
            if attr == "System" or attr == "Hidden":
                return True
        return False 

    def getDataTxt(self, nameVolume):
        fileNameTemp = self.getFileName()
        fileSize = self.getFileSize()
        for a in self.AttrList:
            if (a.attrType == 0x80 and fileNameTemp.endswith('.txt') and a.flagResident == 0):
                dataOfTxt = a.dataOfFile.decode('utf-8')
                return dataOfTxt
            # bugggggg
            if (a.attrType == 0x80 and fileNameTemp.endswith('.txt') and a.flagResident == 1):
                with open(r'\\.\%s' % nameVolume, 'rb') as file: 
                    print (a.firstCluster)
                    print (a.clusterCount)
                    print (fileSize)
                    physicalAddress = a.firstCluster * 4096
                    print (physicalAddress)
                    file.seek(physicalAddress)
                    dataOfTxt = file.read(fileSize).decode('utf-8')
                    file.close()
                return dataOfTxt
        return None
    