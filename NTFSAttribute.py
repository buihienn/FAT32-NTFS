from datetime import timezone, datetime
        
class Attribute:
    def __init__(self, data, offset): #data: 
        # Header attribute
        self.attrType = int.from_bytes(data[offset + 0x00:offset + 0x04], byteorder='little')
        self.sizeAttr = int.from_bytes(data[offset +0x04:offset +0x08 ], byteorder='little')  # kich thuoc của Attrbute gồm Header
        self.flagResident = int.from_bytes(data[offset +0x08:offset +0x09], byteorder='little')
        # self.attrSize = int.from_bytes(data[0x16:0x20], byteorder='little')  # kich thuoc của Attribute không gồm Header
        self.attrData = int.from_bytes(data[offset +20:offset +22], byteorder='little') # Offset start attribute
        self.realSize1 = self.realSize2 = 0 # Init realSize1 and realSize2 

        # Attribute data
        jumpAttrData = offset + self.attrData
        # Standard
        if (self.attrType == 0x10): # Data Standard 
            self.dateCreatedRaw = int.from_bytes(data[jumpAttrData + 0x00:jumpAttrData + 0x08],byteorder='little')
            self.dateCreated = self.convertDatetime(self.dateCreatedRaw)

            self.dateModifiedRaw = int.from_bytes(data[jumpAttrData + 0x08:jumpAttrData + 0x10], byteorder='little')
            self.dateModified = self.convertDatetime(self.dateModifiedRaw)

        # File name 
        if (self.attrType ==0x30):  
            self.IdParentFolder = int.from_bytes(data[jumpAttrData + 0x00:jumpAttrData + 0x06], byteorder='little')
            # Attribute File
            self.objectAttributeRaw = int.from_bytes(data[jumpAttrData + 0x38:jumpAttrData + 0x3C], byteorder='little')
            self.objectAttributeList = []
            self.extractFileAttributes()
            #File Name
            self.fileNameLength = int.from_bytes(data[jumpAttrData + 0x40:jumpAttrData + 0x41], byteorder='little')
            self.fileName = data[jumpAttrData + 0x42 : jumpAttrData + 0x42 + self.fileNameLength * 2].decode('utf-16-le')

        # Data
        if (self.attrType == 0x80):
            if self.flagResident == 0:
                self.realSize1 = int.from_bytes(data[offset + 0x10:offset +0x14], byteorder='little')
            else:
                self.realSize2 = int.from_bytes(data[offset + 0x30:offset +0x38], byteorder='little')
        if(self.realSize1 > self.realSize2):
            self.realSize = self.realSize1
        else:
            self.realSize = self.realSize2

        if (self.attrType == 0x80):
            if self.flagResident == 0:
                self.dataOfFile = data[jumpAttrData + 0x00: jumpAttrData + self.realSize]
            else: 
                self.dataRunOffset = int.from_bytes(data[offset + 32:offset + 34], "little")
                self.clusterCount = int.from_bytes(data[offset + self.dataRunOffset + 1 :offset + self.dataRunOffset + 2], "little")
                self.firstCluster = int.from_bytes(data[offset + self.dataRunOffset + 2:offset + self.dataRunOffset + 4], "little")
                self.clusterSize = int.from_bytes(data[offset + self.dataRunOffset + 0 :offset + self.dataRunOffset + 1], "little")
    
    def convertDatetime(self, date: int) -> str:
        # Chuyển đổi timestamp từ 1601-01-01 00:00:00 UTC sang giây tính từ epoch 1970-01-01 00:00:00 UTC
        timestamp = date / 10_000_000 - 11_644_473_600
        # Tạo đối tượng datetime từ timestamp_seconds
        object = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        # Định dạng theo chuỗi yyyy-mm-dd h:minute
        formattedDatetime = object.strftime('%Y-%m-%d %H:%M')
        return formattedDatetime
    
    def extractFileAttributes(self):
        if self.objectAttributeRaw & 0x01:
            self.objectAttributeList.append("Read-only")
        if self.objectAttributeRaw & 0x02:
            self.objectAttributeList.append("Hidden")
        if self.objectAttributeRaw & 0x04:
            self.objectAttributeList.append("System")
        if self.objectAttributeRaw & 0x20:
            self.objectAttributeList.append("Archive")
        if self.objectAttributeRaw & 0x10000000:
            self.objectAttributeList.append("Directory")
