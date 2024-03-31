from enum import Flag, auto
from datetime import datetime
from itertools import chain
import re
class FAT32_Attribute(Flag):
    READ_ONLY = auto()
    HIDDEN = auto()
    SYSTEM = auto()
    VOLLABLE = auto()
    DIRECTORY = auto()
    ARCHIVE = auto()
class FAT:#doc du lieu tu FAT
    def read_bytes(FAT,data):
        FAT.data=data
        FAT.bytes=[]
        for bit in range(0,len(FAT.data),4):
            FAT.bytes.insert(len(FAT.clusters),int.from_bytes(FAT.data[bit:bit + 4], byteorder='little'))#little endian

    def get_cluster(FAT,bytes_idx):
        list_cluster = []
        while True:
            list_cluster.append(bytes_idx)
            bytes_idx =FAT.bytes[bytes_idx]
            if bytes_idx == 0x0FFFFFFF or bytes_idx == 0x0FFFFFF7:
                break
        return list_cluster
class RDET_ENTRY:
    def convert_create_time(entry,time_value):
        hours = (time_value & 0b111110000000000000000000) >> 19
        minutes = (time_value & 0b000001111110000000000000) >> 13
        seconds = (time_value & 0b000000000001111110000000) >> 7
        milliseconds = (time_value & 0b000000000000000001111111)
        return  hours,minutes,seconds,milliseconds
    def convert_create_date(entry,date_value):
        year = 1980 + ((date_value & 0b1111111000000000) >> 9)
        month = (date_value & 0b0000000111100000) >> 5
        day = date_value & 0b0000000000011111
        return year,month,day
    def LRN(entry):
        name = b""
        for i in chain(range(0x1, 0xB), range(0xE, 0x1A), range(0x1C, 0x20)):
            name += int.to_bytes(entry.data[i], 1, byteorder='little')
            if name.endswith(b"\xff\xff"):
                name = name[:-2]
                break
        return name.decode('utf-16le').strip('\x00')
    def get_attribute(entry,data_bytes):
        entry.data=data_bytes
        entry.entry_name=""
        entry.attr_byte=entry.data[11:12]#offset 0xB de lay thuoc tinh
        entry.is_sub_entry = False
        if entry.attr_byte==b"\x0F":
            entry.is_sub_entry = True
        entry.is_deleted = entry.data[0] == 0xe5
        entry.is_empty = entry.data[0] == 0x00
        entry.is_label = FAT32_Attribute.VOLLABLE in FAT32_Attribute(int.from_bytes(entry.attr_byte, byteorder='little'))
        entry.is_system= FAT32_Attribute.SYSTEM in FAT32_Attribute(int.from_bytes(entry.attr_byte, byteorder='little'))
        entry.is_directory=FAT32_Attribute.DIRECTORY in FAT32_Attribute(int.from_bytes(entry.attr_byte, byteorder='little'))
        entry.is_archive=FAT32_Attribute.ARCHIVE in FAT32_Attribute(int.from_bytes(entry.attr_byte, byteorder='little'))
        entry.attr=FAT32_Attribute(int.from_bytes(entry.attr_byte,byteorder='little'))
        entry.size=0
        entry.create_date=0
        entry.last_accessed=0
        entry.last_updated=0
        entry.extend_name=b""#cai nay phai byte string
        entry.LRN=""
        if not entry.is_sub_entry:#not LRN
            entry.name=entry.data[0:8]
            entry.extend_name=entry.data[8:11]
            if entry.is_deleted or entry.is_empty:
                entry.name=""
            if entry.is_label:
                return
            #create time
            entry.temp_create_time=int.from_bytes(entry.data[13:16],byteorder='little')
            hours , minutes ,seconds ,milliseconds =entry.convert_create_time(entry.temp_create_time)

            entry.temp_create_date=int.from_bytes(entry.data[16:18],byteorder='little')
            year,month,day=entry.convert_create_date(entry.temp_create_date)
            entry.create_date= datetime(year,month,day,hours,minutes,seconds,milliseconds)
            #last accessed time
            entry.temp_last_accessed=int.from_bytes(entry.data[18:20],byteorder='little')
            year,month,day=entry.convert_create_date(entry.temp_last_accessed)
            entry.last_accessed=datetime(year,month,day)
            #last update time
            entry.temp_last_update_time=int.from_bytes(entry.data[22:24],byteorder='little')
            hours , minutes ,seconds ,milliseconds=entry.convert_create_time(entry.temp_last_update_time)

            entry.temp_last_update_date=int.from_bytes(entry.data[24:26],byteorder='little')
            year,month,day=entry.convert_create_date(entry.temp_last_update_date)
            entry.last_updated=datetime(year,month,day,hours,minutes,seconds,milliseconds)

            entry.start_cluster=int.from_bytes(entry.data[26:28]+entry.data[20:22],byteorder='little')
        else:
            entry.index=entry.data[0]
            entry.name=entry.LRN()
    def is_active_entry(entry):
        return not(entry.is_empty or entry.is_deleted or entry.is_sub_entry or entry.is_label or entry.is_system)
    def is_direct(entry):
        return entry.is_directory
    def is_arch(entry):
        return entry.is_archive
class RDET:
    def get_full_entry_name(rdet) -> list[RDET_ENTRY]:
        entry_name = ''
        entries: list[RDET_ENTRY] = []

        for i in range(0, len(rdet.data), 32):
            entries.append(RDET_ENTRY(rdet.data[i: i + 32]))
            if entries[-1].is_empty or entries[-1].is_deleted:
                entry_name = ''
                continue
            elif entries[-1].is_subentry:
                entry_name = entries[-1].name + entry_name
                continue

            if entry_name != '':
                entries[-1].entry_name = entry_name
            else:
                extension = entries[-1].extend_name.strip().decode()
                if extension != '':
                    entries[-1].entry_name = entries[-1].name.strip().decode() + '.' + extension
                else:
                    entries[-1].entry_name = entries[-1].name.strip().decode()
            entry_name = ''
        return entries
    def __init__(rdet,data):
        rdet.data=data
        rdet.entries:list[RDET_ENTRY]=[]
        rdet.entries=rdet.get_full_entry_name()
    def get_active_entries(rdet) -> 'list[RDET_ENTRY]':
        entry_list = []
        for i in range(len(rdet.entries)):
            if rdet.entries[i].is_active_entry():
                entry_list.append(rdet.entries[i])
        return entry_list
    def find_entry(rdet, name):
        for i in range(len(rdet.entries)):
            if rdet.entries[i].is_active_entry() and rdet.entries[i].entry_name.lower() == name.lower():
                return rdet.entries[i]
        return None
class FAT32:
    def get_all_cluster_data(fat32, cluster_index):
        cluster_list = fat32.list_FAT32[0].get_cluster(cluster_index)
        data = b""

        for i in cluster_list:
            if i<2:
                continue
            sector_index = fat32.reserved_sec + fat32.sec_per_fat*fat32.num_fat + i*fat32.sec_per_clus
            fat32.bin_data.seek(sector_index * fat32.bytes_per_sec)
            data += fat32.bin_data.read(fat32.bytes_per_sec * fat32.sec_per_clus)
        return data
    def extract_boot_sector(fat32):
        fat32.boot_sector['Bytes/Sector'] = int.from_bytes(fat32.boot_sector_data[0xB:0xD], 'little')
        fat32.boot_sector['Sectors/Cluster'] = int.from_bytes(fat32.boot_sector_data[0xD:0xE], 'little')
        fat32.boot_sector['Reserved Sectors'] = int.from_bytes(fat32.boot_sector_data[0xE:0x10], 'little')
        fat32.boot_sector['Numbers of FAT'] = int.from_bytes(fat32.boot_sector_data[0x10:0x11], 'little')
        fat32.boot_sector['Sectors In Volume'] = int.from_bytes(fat32.boot_sector_data[0x20:0x24], 'little')
        fat32.boot_sector['Sectors/FAT'] = int.from_bytes(fat32.boot_sector_data[0x24:0x28], 'little')
        fat32.boot_sector['Start Cluster of RDET'] = int.from_bytes(fat32.boot_sector_data[0x2C:0x30], 'little')
        fat32.boot_sector['FAT Name'] = fat32.boot_sector_data[0x52:0x5A]
        fat32.boot_sector['Start Sector'] = fat32.boot_sector['Reserved Sectors'] + fat32.boot_sector['Numbers of FAT'] * fat32.boot_sector['Sectors/FAT']#do FAT32 co phan reserved nen no thuoc ve start sector
    def __init__(fat32,volume_name):
        fat32.name=  volume_name
        fat32.cwd=[fat32.name]   
        try:
            fat32.bin_data=open(rf"\\.\{fat32.name}", 'rb')
            fat32.boot_sector={}

            fat32.bsector_data=fat32.bin_data.read(512)
            fat32.extract_boot_sector()
            if fat32.boot_sector['FAT Name'] != b'FAT32':
                raise Exception('NOT FAT32')
            
            fat32.boot_sector['FAT Name']=fat32.boot_sector['FAT Name'].decode()
            fat32.bytes_per_sec=fat32.boot_sector['Bytes/Sector']
            fat32.sec_per_clus= fat32.boot_sector['Sectors/Cluster']
            fat32.reserved_sec=fat32.boot_sector['Reserved Sectors']
            fat32.num_fat=fat32.boot_sector['Numbers of FAT']
            fat32.sec_in_vol=fat32.boot_sector['Sectors In Volume']
            fat32.sec_per_fat=fat32.boot_sector['Sectors/FAT']
            fat32.start_clus_rdet=fat32.boot_sector['Start Cluster of RDET']
            fat32.data_start_sec=fat32.boot_sector['Start Sector']
            FAT32_size=fat32.bytes_per_sec*fat32.sec_per_fat
            fat32.boot_sector_reserved_temp=fat32.bin_data.read(fat32.bytes_per_sec*(fat32.reserved_sec-1))

            fat32.list_FAT32=[]
            for f in range(fat32.num_fat):
                fat32.list_FAT32.append(FAT(fat32.bin_data.read(FAT32_size)))

            #RDET
            fat32.RDET=RDET(fat32.get_all_cluster_data(fat32.start_clus_rdet))
            fat32.DET={}
            fat32.DET[fat32.start_clus_rdet]=fat32.RDET
        except Exception as error:
            print(f"Error:{error}")
            exit()
    def __info__(fat32):
        data = "VOLUME INFORMATION\n"
        data += "Name: " + fat32.name + '\n'
        info = fat32.boot_sector.items()

        for i in info:
            data += str(i[0]) + ': ' + str(i[1]) + '\n'
        return data
    def __close__(self):
        if getattr(self, "bin_data", None):
            print("Closing")
            self.bin_data.close()
    @staticmethod
    def is_FAT32(name):
        try:
            boot_sector = open(rf'\\.\{name}', 'rb')
            boot_sector.read(1)  #MAYBE
            boot_sector.seek(0x52)
            FAT_type = boot_sector.read(8)

            if FAT_type == b'FAT32':
                return True
            return False
        except Exception as error:
            print(f'Error: {error}')
            exit()
    
    def split_path(fat32,path):
        dirs = path.replace('/', '\\').strip('\\').split('\\')
        return dirs
    def retrieve_path(fat32,path):
        if path=="":
            raise Exception("Path is empty!")
        path=fat32.split_path(path)
        if path[0]== fat32.name:#duong dan co chua volume
            cur_det=fat32.DET[fat32.start_clus_rdet]
            path.pop(0)
        else:#duong dan ko co bat dau tu volume name
            cur_det=fat32.RDET
        
        for i in path:
            entry=cur_det.find_entry(i)
            if entry is None:
                raise Exception("Directory not found!")
            if entry.is_direct():
                if entry.start_cluster==0:
                    cur_det=
