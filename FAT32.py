from enum import Flag, auto
from datetime import datetime
from itertools import chain
import re
import os

class FAT32_Attribute(Flag):
    READ_ONLY = auto()
    HIDDEN = auto()
    SYSTEM = auto()
    VOLLATILE = auto()
    DIRECTORY = auto()
    ARCHIVE = auto()
class FAT:#doc du lieu tu FAT
    def __init__(FAT,data):
        FAT.data=data
        FAT.bytes=[]
        for bit in range(0,len(FAT.data),4):
            FAT.bytes.insert(len(FAT.bytes),int.from_bytes(FAT.data[bit:bit + 4], byteorder='little'))#little endian

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
    def __init__(entry,data_bytes):
        entry.data=data_bytes
        entry.entry_name=''
        entry.attr_byte=entry.data[0xB:0xC]#offset 0xB de lay thuoc tinh
        entry.is_sub_entry = False
        if entry.attr_byte==b'\x0f':
            entry.is_sub_entry = True
        entry.is_deleted = entry.data[0] == 0xe5
        entry.is_empty = entry.data[0] == 0x00
       
       
        
        entry.is_label = FAT32_Attribute.VOLLATILE in FAT32_Attribute(int.from_bytes(entry.attr_byte,byteorder='little'))
        entry.size=int.from_bytes(entry.data[0x1C:0x20], byteorder='little')
        
        entry.create_date=0
        entry.last_accessed=0
        entry.last_updated=0
        entry.extend_name=b""#cai nay phai byte string
        
        if not entry.is_sub_entry:#not LRN
            entry.name=entry.data[:8]
            
            entry.extend_name=entry.data[8:11]
            if entry.is_deleted or entry.is_empty:
                entry.name=""
                return
            entry.attr=FAT32_Attribute(int.from_bytes(entry.attr_byte,byteorder='little'))
        
            if FAT32_Attribute.VOLLATILE in entry.attr:
                entry.is_label=True
                return
            #create time
            entry.temp_create_time=int.from_bytes(entry.data[0xD:0x10],byteorder='little')
            
            hours , minutes ,seconds ,milliseconds =entry.convert_create_time(entry.temp_create_time)
          
            entry.temp_create_date=int.from_bytes(entry.data[0x10:0x12],byteorder='little')
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
        return not(entry.is_empty or entry.is_deleted or entry.is_sub_entry or entry.is_label or FAT32_Attribute.SYSTEM in entry.attr)
    def is_direct(entry):
        return FAT32_Attribute.DIRECTORY in entry.attr
    def is_arch(entry):
        return FAT32_Attribute.ARCHIVE in entry.attr
class RDET:
    def get_full_entry_name(rdet) -> list[RDET_ENTRY]:
        entry_name = ''
        entries: list[RDET_ENTRY] = []

        for i in range(0, len(rdet.data), 32):
            entries.append(RDET_ENTRY(rdet.data[i: i + 32]))
            if entries[-1].is_empty or entries[-1].is_deleted:
                entry_name = ''
                continue
            elif entries[-1].is_sub_entry:
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
    def count_sector_offset_in_cluster(fat32,index):
        return fat32.reserved_sec + fat32.sec_per_fat * fat32.num_fat + (index-2) * fat32.sec_per_clus
    def get_all_cluster_data(fat32, cluster_index):
        cluster_list = fat32.list_FAT32[0].get_cluster(cluster_index)
        data = b""

        for i in cluster_list:

            sector_index = fat32.reserved_sec + fat32.sec_per_fat*fat32.num_fat + (i-2)*fat32.sec_per_clus
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

            fat32.boot_sector_data=fat32.bin_data.read(512)
            fat32.extract_boot_sector()
            if fat32.boot_sector['FAT Name'] != b'FAT32   ':
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
            s_index=fat32.boot_sector['Start Cluster of RDET']
            fat32.RDET=RDET(fat32.get_all_cluster_data( s_index))
            fat32.DET={}
            fat32.DET[ s_index]=fat32.RDET
        except Exception as error:
            print(f"Error:{error}")
            exit()

    @staticmethod
    def is_FAT32(name):
        try:
            boot_sector = open(rf'\\.\{name}', 'rb')
            boot_sector.read(1)  #MAYBE
            boot_sector.seek(0x52)
            FAT_type = boot_sector.read(8)
            
            if FAT_type == b'FAT32   ':
                return True
            return False
        except Exception as error:
          
            print(f'Error: {error}')
            exit()
    
    def split_path(fat32,path):
        dirs = path.replace('/', '\\').strip('\\').split('\\')
        return dirs
    def retrieve_path(fat32,path):#duong dan trong thao tac cd va data
        if path=="":
            raise Exception("Path is empty!")
        path=fat32.split_path(path)#tach duong dan thanh cac phan tu
        if path[0]== fat32.name:#duong dan co chua volume
            cur_det=fat32.DET[fat32.start_clus_rdet]#dat cur_det vao direct entry bat dau
            path.pop(0)
        else:#duong dan ko co bat dau tu volume name
            cur_det=fat32.RDET#dat cur_det vao RDET de kiem tra tu o dia
        
        for i in path:
            entry=cur_det.find_entry(i)
            if entry is None:
                raise Exception("Directory not found!")
            if entry.is_direct():
                if entry.start_cluster==0:
                    cur_det=fat32.DET[fat32.start_clus_rdet]
                    continue
                if entry.start_cluster in fat32.DET:
                    cur_det=fat32.DET[entry.start_cluster]
                    continue
                fat32.DET[entry.start_cluster]=RDET(fat32.get_all_cluster_data( entry.start_cluster))
                cur_det=fat32.DET[entry.start_cluster]
            else:
                raise Exception("Not a directory")
        return cur_det
    def getCWD(fat32):
        if len(fat32.cwd)==1:
            return fat32.cwd[0]+"\\"
        return"\\".join(fat32.cwd)
    def get_directory_info(fat32,path=None):
        try:
            if path is not None:
                cur_det=fat32.retrieve_path(path)
                print(cur_det)
                entry_list=cur_det.get_active_entries()
            else:
                entry_list=fat32.RDET.get_active_entries()
            info=[{
                "Flags":i.attr.value,
                "Date Modified":i.last_updated,
                "Size":i.size,
                "Name":i.entry_name,
                "Date Created":i.create_date,
                "Last Accessed":i.last_accessed,
                "Sector":(i.start_cluster+2)*fat32.sec_per_clus if i.start_cluster==0 else i.start_cluster*fat32.sec_per_clus

            }for i in entry_list]
            return info
        except Exception as error:
            raise(error)
    def move_to_directory(fat32,path):#cd vao thu muc
        if path is None:
            raise Exception("Path is None!")
        try:
            cur_det=fat32.retrieve_path(path)
            fat32.RDET=cur_det
            dirs=fat32.split_path(path)
            if dirs[0]==fat32.name:
                fat32.cwd.clear()
                fat32.cwd.insert(0,fat32.name)
                dirs.pop(0)
            for i in dirs:
                if i =="..":
                    fat32.cwd.pop()
                elif i!=".":
                    fat32.cwd.append(i)
        except Exception as e:
            raise e
    def get_File_content(fat32,path):
        split_path=fat32.split_path(path)
        if len (split_path)>1:
            volume_name=split_path[-1]
            dir_path="\\".join(split_path[:-1])
            cur_det=fat32.retrieve_path(dir_path)
            entry=cur_det.find_entry(volume_name)
        else:
            entry=fat32.RDET.find_entry(split_path[0])
        if entry is None:
            raise Exception("File not exists")
        if entry.is_direct():
            raise Exception("Is a directory")
        cluster_list=fat32.list_FAT32[0].get_cluster(entry.start_cluster)
        data=""
        size=entry.size
        for cluster in cluster_list:
            if size<=0:
                break
            sector_offset=fat32.count_sector_offset_in_cluster(cluster)#tim vi tri sector bat dau cua entry 
            fat32.bin_data.seek(sector_offset*fat32.bytes_per_sec)#seek toi vi tri sector bat dau do
            raw_data=fat32.bin_data.read(min(fat32.sec_per_clus*fat32.bytes_per_sec,size))#doc du lieu entry nay
            size-=fat32.sec_per_clus*fat32.bytes_per_sec# doc tung cluster nen lay entry size - size cluster de dung vong lap
            try:
                data+= raw_data.decode()
            except UnicodeDecodeError as e:
                raise Exception("not text file")
            except Exception as e:
                raise e
        return data
    
