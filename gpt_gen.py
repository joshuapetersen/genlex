import struct
import uuid
import zlib

SECTOR = 512
DISK_SIZE = 128 * 1024 * 1024
TOTAL_SECTORS = DISK_SIZE // SECTOR

PRIMARY_HDR_LBA = 1
PART_ENTRIES_LBA = 2
PART_ENTRY_SIZE = 128
PART_ENTRY_COUNT = 128
PART_ARRAY_SIZE = PART_ENTRY_SIZE * PART_ENTRY_COUNT
PART_ARRAY_SECTORS = PART_ARRAY_SIZE // SECTOR

BACKUP_ENTRIES_LBA = TOTAL_SECTORS - 1 - PART_ARRAY_SECTORS
BACKUP_HDR_LBA = TOTAL_SECTORS - 1

FIRST_USABLE = PART_ENTRIES_LBA + PART_ARRAY_SECTORS
LAST_USABLE = BACKUP_ENTRIES_LBA - 1

OUT_PATH = r"C:\Genlex_Linear\sarah_os_gpt.img"


def crc32(data):
    return zlib.crc32(data) & 0xFFFFFFFF


def build_pmbr():
    mbr = bytearray(SECTOR)
    # Protective MBR partition entry
    mbr[446:462] = struct.pack(
        "<BBBBBBBBII",
        0x00, 0x00, 0x02, 0x00,   # status + CHS first
        0xEE, 0xFF, 0xFF, 0xFF,   # type 0xEE + CHS last
        1,                        # LBA start
        TOTAL_SECTORS - 1         # size in sectors
    )
    mbr[510:512] = b"\x55\xAA"
    return mbr


def build_partition_array(start_lba, end_lba):
    arr = bytearray(PART_ARRAY_SIZE)

    # Partition entry 0
    part_type = uuid.UUID("C12A7328-F81F-11D2-BA4B-00A0C93EC93B").bytes_le
    unique = uuid.uuid4().bytes_le
    name_utf16 = "EFI System".encode("utf-16-le")

    entry = bytearray(PART_ENTRY_SIZE)
    entry[0:16] = part_type
    entry[16:32] = unique
    entry[32:40] = struct.pack("<Q", start_lba)
    entry[40:48] = struct.pack("<Q", end_lba)
    entry[56:56+len(name_utf16)] = name_utf16

    arr[0:PART_ENTRY_SIZE] = entry
    return arr


def build_gpt_header(current_lba, backup_lba, entries_lba, entries_crc):
    hdr = bytearray(92)
    hdr[0:8] = b"EFI PART"
    hdr[8:12] = struct.pack("<I", 0x00010000)   # Revision 1.0
    hdr[12:16] = struct.pack("<I", 92)          # Header size
    hdr[20:24] = b"\x00\x00\x00\x00"            # Reserved

    hdr[24:32] = struct.pack("<Q", current_lba)
    hdr[32:40] = struct.pack("<Q", backup_lba)
    hdr[40:48] = struct.pack("<Q", FIRST_USABLE)
    hdr[48:56] = struct.pack("<Q", LAST_USABLE)

    hdr[56:72] = uuid.uuid4().bytes_le          # Disk GUID

    hdr[72:80] = struct.pack("<Q", entries_lba)
    hdr[80:84] = struct.pack("<I", PART_ENTRY_COUNT)
    hdr[84:88] = struct.pack("<I", PART_ENTRY_SIZE)
    hdr[88:92] = struct.pack("<I", entries_crc)

    # Compute header CRC
    temp = bytearray(hdr)
    temp[16:20] = b"\x00\x00\x00\x00"
    crc = crc32(temp)
    hdr[16:20] = struct.pack("<I", crc)

    return hdr

def create_gpt():
    disk = bytearray(DISK_SIZE)

    # PMBR
    disk[0:SECTOR] = build_pmbr()

    # Primary partition entries
    part_array = build_partition_array(2048, LAST_USABLE)
    part_crc = crc32(part_array)
    disk[PART_ENTRIES_LBA*SECTOR : PART_ENTRIES_LBA*SECTOR + PART_ARRAY_SIZE] = part_array

    # Primary header
    primary_hdr = build_gpt_header(
        PRIMARY_HDR_LBA,
        BACKUP_HDR_LBA,
        PART_ENTRIES_LBA,
        part_crc
    )
    disk[PRIMARY_HDR_LBA*SECTOR : PRIMARY_HDR_LBA*SECTOR + 92] = primary_hdr

    # Backup partition entries
    disk[BACKUP_ENTRIES_LBA*SECTOR : BACKUP_ENTRIES_LBA*SECTOR + PART_ARRAY_SIZE] = part_array

    # Backup header
    backup_hdr = build_gpt_header(
        BACKUP_HDR_LBA,
        PRIMARY_HDR_LBA,
        BACKUP_ENTRIES_LBA,
        part_crc
    )
    disk[BACKUP_HDR_LBA*SECTOR : BACKUP_HDR_LBA*SECTOR + 92] = backup_hdr

    with open(OUT_PATH, "wb") as f:
        f.write(disk)

    print("SUCCESS: Valid GPT image created at", OUT_PATH)

if __name__ == "__main__":
    create_gpt()
