# -*- coding: utf-8 -*-

import os
import sys
import struct
import operator
import argparse
import time
import hashlib
import gcnamehashes

import queue
import threading
from collections import namedtuple
from os import listdir, walk
from os.path import (
    isfile,
    join,
    relpath,
    basename,
    commonpath,
    abspath,
    realpath,
    normpath,
    dirname,
)

separator = ","
fileAtEnd = 0xC0000000

headerFile = "filelist.txt"

###########################################################################################################################################################


class RomSection:
    def __init__(self, name, hash, address, size, checksum):
        self.FileName = name.replace("\\", "/").lower()

        self.PathHash = int(hash)
        if self.PathHash == 0:
            self.PathHash = computeFileHash(self.FileName)

        self.DataOffset = int(address)
        self.OriginalDataOffset = self.DataOffset
        self.DataSize = int(size)
        self.CheckSum = int(checksum)
        if self.CheckSum > 0:
            self.CheckSum = 0x2000000

        self.IsNew = False
        # if self.CheckSum > 0 :
        #    print(self.FileName + " "+str(self.CheckSum)+"\n")

    @classmethod
    def fromList(cls, data):
        return cls(data[0], data[1], data[2], data[3], data[4])


###########################################################################################################################################################


CRCTable = [
    0x00000000,
    0x77073096,
    0xEE0E612C,
    0x990951BA,
    0x076DC419,
    0x706AF48F,
    0xE963A535,
    0x9E6495A3,
    0x0EDB8832,
    0x79DCB8A4,
    0xE0D5E91E,
    0x97D2D988,
    0x09B64C2B,
    0x7EB17CBD,
    0xE7B82D07,
    0x90BF1D91,
    0x1DB71064,
    0x6AB020F2,
    0xF3B97148,
    0x84BE41DE,
    0x1ADAD47D,
    0x6DDDE4EB,
    0xF4D4B551,
    0x83D385C7,
    0x136C9856,
    0x646BA8C0,
    0xFD62F97A,
    0x8A65C9EC,
    0x14015C4F,
    0x63066CD9,
    0xFA0F3D63,
    0x8D080DF5,
    0x3B6E20C8,
    0x4C69105E,
    0xD56041E4,
    0xA2677172,
    0x3C03E4D1,
    0x4B04D447,
    0xD20D85FD,
    0xA50AB56B,
    0x35B5A8FA,
    0x42B2986C,
    0xDBBBC9D6,
    0xACBCF940,
    0x32D86CE3,
    0x45DF5C75,
    0xDCD60DCF,
    0xABD13D59,
    0x26D930AC,
    0x51DE003A,
    0xC8D75180,
    0xBFD06116,
    0x21B4F4B5,
    0x56B3C423,
    0xCFBA9599,
    0xB8BDA50F,
    0x2802B89E,
    0x5F058808,
    0xC60CD9B2,
    0xB10BE924,
    0x2F6F7C87,
    0x58684C11,
    0xC1611DAB,
    0xB6662D3D,
    0x76DC4190,
    0x01DB7106,
    0x98D220BC,
    0xEFD5102A,
    0x71B18589,
    0x06B6B51F,
    0x9FBFE4A5,
    0xE8B8D433,
    0x7807C9A2,
    0x0F00F934,
    0x9609A88E,
    0xE10E9818,
    0x7F6A0DBB,
    0x086D3D2D,
    0x91646C97,
    0xE6635C01,
    0x6B6B51F4,
    0x1C6C6162,
    0x856530D8,
    0xF262004E,
    0x6C0695ED,
    0x1B01A57B,
    0x8208F4C1,
    0xF50FC457,
    0x65B0D9C6,
    0x12B7E950,
    0x8BBEB8EA,
    0xFCB9887C,
    0x62DD1DDF,
    0x15DA2D49,
    0x8CD37CF3,
    0xFBD44C65,
    0x4DB26158,
    0x3AB551CE,
    0xA3BC0074,
    0xD4BB30E2,
    0x4ADFA541,
    0x3DD895D7,
    0xA4D1C46D,
    0xD3D6F4FB,
    0x4369E96A,
    0x346ED9FC,
    0xAD678846,
    0xDA60B8D0,
    0x44042D73,
    0x33031DE5,
    0xAA0A4C5F,
    0xDD0D7CC9,
    0x5005713C,
    0x270241AA,
    0xBE0B1010,
    0xC90C2086,
    0x5768B525,
    0x206F85B3,
    0xB966D409,
    0xCE61E49F,
    0x5EDEF90E,
    0x29D9C998,
    0xB0D09822,
    0xC7D7A8B4,
    0x59B33D17,
    0x2EB40D81,
    0xB7BD5C3B,
    0xC0BA6CAD,
    0xEDB88320,
    0x9ABFB3B6,
    0x03B6E20C,
    0x74B1D29A,
    0xEAD54739,
    0x9DD277AF,
    0x04DB2615,
    0x73DC1683,
    0xE3630B12,
    0x94643B84,
    0x0D6D6A3E,
    0x7A6A5AA8,
    0xE40ECF0B,
    0x9309FF9D,
    0x0A00AE27,
    0x7D079EB1,
    0xF00F9344,
    0x8708A3D2,
    0x1E01F268,
    0x6906C2FE,
    0xF762575D,
    0x806567CB,
    0x196C3671,
    0x6E6B06E7,
    0xFED41B76,
    0x89D32BE0,
    0x10DA7A5A,
    0x67DD4ACC,
    0xF9B9DF6F,
    0x8EBEEFF9,
    0x17B7BE43,
    0x60B08ED5,
    0xD6D6A3E8,
    0xA1D1937E,
    0x38D8C2C4,
    0x4FDFF252,
    0xD1BB67F1,
    0xA6BC5767,
    0x3FB506DD,
    0x48B2364B,
    0xD80D2BDA,
    0xAF0A1B4C,
    0x36034AF6,
    0x41047A60,
    0xDF60EFC3,
    0xA867DF55,
    0x316E8EEF,
    0x4669BE79,
    0xCB61B38C,
    0xBC66831A,
    0x256FD2A0,
    0x5268E236,
    0xCC0C7795,
    0xBB0B4703,
    0x220216B9,
    0x5505262F,
    0xC5BA3BBE,
    0xB2BD0B28,
    0x2BB45A92,
    0x5CB36A04,
    0xC2D7FFA7,
    0xB5D0CF31,
    0x2CD99E8B,
    0x5BDEAE1D,
    0x9B64C2B0,
    0xEC63F226,
    0x756AA39C,
    0x026D930A,
    0x9C0906A9,
    0xEB0E363F,
    0x72076785,
    0x05005713,
    0x95BF4A82,
    0xE2B87A14,
    0x7BB12BAE,
    0x0CB61B38,
    0x92D28E9B,
    0xE5D5BE0D,
    0x7CDCEFB7,
    0x0BDBDF21,
    0x86D3D2D4,
    0xF1D4E242,
    0x68DDB3F8,
    0x1FDA836E,
    0x81BE16CD,
    0xF6B9265B,
    0x6FB077E1,
    0x18B74777,
    0x88085AE6,
    0xFF0F6A70,
    0x66063BCA,
    0x11010B5C,
    0x8F659EFF,
    0xF862AE69,
    0x616BFFD3,
    0x166CCF45,
    0xA00AE278,
    0xD70DD2EE,
    0x4E048354,
    0x3903B3C2,
    0xA7672661,
    0xD06016F7,
    0x4969474D,
    0x3E6E77DB,
    0xAED16A4A,
    0xD9D65ADC,
    0x40DF0B66,
    0x37D83BF0,
    0xA9BCAE53,
    0xDEBB9EC5,
    0x47B2CF7F,
    0x30B5FFE9,
    0xBDBDF21C,
    0xCABAC28A,
    0x53B39330,
    0x24B4A3A6,
    0xBAD03605,
    0xCDD70693,
    0x54DE5729,
    0x23D967BF,
    0xB3667A2E,
    0xC4614AB8,
    0x5D681B02,
    0x2A6F2B94,
    0xB40BBE37,
    0xC30C8EA1,
    0x5A05DF1B,
    0x2D02EF8D,
]


def computeFileHash(name):
    length = len(name)
    hashVal = 0
    i = 0
    while length > 0:
        currentChar = ord(name[i])
        lookupKey = (hashVal ^ (currentChar)) & 0xFF
        hashVal = CRCTable[lookupKey] ^ (hashVal >> 8)
        length -= 1
        i += 1

    return hashVal


###########################################################################################################################################################


def scanFiles(dir):
    scannedRomMap = []
    for root, directories, files in os.walk(dir, topdown=False):
        for name in files:
            if name.lower() == headerFile:
                print("Skipping " + headerFile)
                continue

            # print(relpath(os.path.join(root,name),dir))
            fullName = relpath(os.path.join(root, name), dir)
            romSection = RomSection.fromList([fullName, "0", str(fileAtEnd), "0", "0"])
            scannedRomMap.append(romSection)

    return scannedRomMap


def readFileList(becmap):
    dir = os.path.dirname(becmap)
    scannedData = scanFiles(dir)

    fileListData = []

    with open(becmap) as fin:
        lineCount = 0
        for line in fin:
            if line[0] == "#":
                continue

            words = line.split(separator)

            # header
            if lineCount == 0:
                fileAlignment = int(words[0])
                nrOfFiles = int(words[1])
                headerMagic = int(words[2])
                print("FA : " + str(fileAlignment) + " : " + words[0])
            else:
                romSection = RomSection.fromList(words)
                fileListData.append(romSection)
                # print(romSection.FileName)
            lineCount += 1

    # print(romSections)
    diffList = diffFiles(fileListData, scannedData)

    # print("fileListData "+str(len(fileListData))+" scannedData "+str(len(scannedData))+"  diffList "+str(len(diffList)))
    print("Files : " + str(len(fileListData)))
    return [fileListData, fileAlignment, headerMagic, diffList]


def diffFiles(fileListData, scannedData):
    fileListDataDictionary = {}
    scannedDataDictionary = {}
    for romData in fileListData:
        fileListDataDictionary[romData.FileName] = romData
    for romData in scannedData:
        scannedDataDictionary[romData.FileName] = romData

    scannedSet = set(scannedDataDictionary.keys())
    fileListSet = set(fileListDataDictionary.keys())

    scannedList = list(scannedDataDictionary)
    fileListList = list(fileListDataDictionary)

    scannedList.sort()
    fileListList.sort()

    # writeListToFile("scanned.txt",scannedList)
    # writeListToFile("fileListSet.txt",fileListList)

    newFiles = scannedSet - fileListSet

    returnList = []
    for file in newFiles:
        romSection = RomSection.fromList([file, "0", str(fileAtEnd), "0", "0"])
        romSection.IsNew = True
        returnList.append(romSection)

    # for file in newFiles :
    # print(file)
    return returnList


def writeListToFile(name, data):
    outFile = open(name, "w")
    for item in data:
        outFile.write(str(item))
        outFile.write("\n")

    outFile.flush()
    outFile.close()


# PACK BEC-ARCHIVE
###########################################################################################################################################################

MAX_NR_OF_THREADS = 1
file_queue = queue.Queue()


def ReadSection(file, addr, size, debug=False):
    file.seek(addr)
    return file.read(size)


def WriteSectionInFile(fByteArray, dirname, filename, addr, size, debug=False):
    filename2 = dirname + filename
    if not os.path.exists(os.path.dirname(filename2)):
        os.makedirs(os.path.dirname(filename2))
    outFile = open(filename2, "wb")
    outFile.write(fByteArray)
    outFile.flush()
    outFile.close()

    # print("Write out file " + filename2)


def file_worker():
    while True:
        item = file_queue.get()
        if item is None:
            break
        fByteArray, dirname, filename, addr, size = item
        WriteSectionInFile(fByteArray, dirname, filename, addr, size)
        file_queue.task_done()


def ReadWord(file, Offset):
    file.seek(Offset)
    data = file.read(4)
    (word,) = struct.unpack(">I", data)
    return word


def ReadHWord(file, Offset):
    file.seek(Offset)
    data = file.read(2)
    (word,) = struct.unpack(">H", data)
    return word


def ReadByte(file, Offset):
    file.seek(Offset)
    data = file.read(1)
    (word,) = struct.unpack("<B", data)
    return word


###########################################################################################################################################################


def getFilename(hashcode, count):
    if hashcode in gcnamehashes.filenameHashes:
        return gcnamehashes.filenameHashes[hashcode]
    else:
        return str(count) + ".bin"


def unpackBecArchive(filename, filedir, demobec, debug=False):

    print("Filename : " + filename)
    print("Filedir : " + filedir)
    file = open(filename, "rb+")
    header_output = unpackBecArchive2(file, filedir, demobec, debug)

    headerfilename = filedir + headerFile
    if not os.path.exists(os.path.dirname(headerfilename)) and os.path.dirname(
        headerfilename
    ):
        os.makedirs(os.path.dirname(headerfilename))
    fheader = open(headerfilename, "w")
    fheader.write(header_output)


def unpackBecArchive2(file, filedir, demobec, debug=False):
    output = ""

    RomSections = []

    BecHeader = namedtuple("BecHeader", ["FileAlignment", "NrOfFiles", "HeaderMagic"])

    print("DemoBec == " + str(demobec))

    if demobec == 1:
        file.seek(0x4)  # bec
        data = file.read(4)
        numFiles = struct.unpack("<I", data)[0]
        makeData = [0, numFiles, 0]
        header = BecHeader._make(makeData)
    else:
        file.seek(0x6)
        data = file.read(10)
        header = BecHeader._make(struct.unpack("<HII", data))

    print("Nr of Files in the bec-file: " + str(header.NrOfFiles))
    print("File Alignment: " + str(header.FileAlignment))
    output += (
        str(header.FileAlignment)
        + separator
        + str(header.NrOfFiles)
        + separator
        + str(header.HeaderMagic)
        + "\n"
    )

    print(output)

    count = 0

    FileEntry = namedtuple(
        "FileEntry", ["PathHash", "DataOffset", "CompDataSize", "DataSize"]
    )
    for i in range(header.NrOfFiles):
        data = file.read(0x10)  # file.seek(0x10+0x10*i)
        fileEntry = FileEntry._make(struct.unpack("<IIII", data))
        filename = getFilename(fileEntry.PathHash, count)
        romSection = RomSection(
            filename,
            str(fileEntry.PathHash),
            str(fileEntry.DataOffset),
            str(fileEntry.DataSize),
            str(fileEntry.CompDataSize),
        )
        RomSections.append(romSection)
        count += 1

    for romSection in RomSections:
        romSection.FileByteArray = ReadSection(
            file, romSection.DataOffset, romSection.DataSize
        )
        WriteSectionInFile(
            romSection.FileByteArray,
            filedir,
            romSection.FileName,
            romSection.DataOffset,
            romSection.DataSize,
        )

        # if romSection.CheckSum != 0:
        #    dataLine = "#"
        #    dataLine += "  Compressed Size : "+(romSection.CheckSum & 0xFFFFFF00)
        #    dataLine += "  Cached : "+ +(romSection.CheckSum & 0x000000F0)
        #    dataLine += "  Instanced : "+ +(romSection.CheckSum & 0x00000080)
        #    dataLine += "\n"
        #    output += dataLine

        dataLine = romSection.FileName + separator
        dataLine += str(romSection.PathHash) + separator
        dataLine += str(romSection.DataOffset) + separator
        dataLine += str(romSection.DataSize) + separator
        dataLine += str(romSection.CheckSum) + "\n"
        output += dataLine

    for i in range(MAX_NR_OF_THREADS):
        file_queue.put(None)

    return output


# UNPACK BEC-ARCHIVE
###########################################################################################################################################################

RomMap = []


def alignFileSizeWithZeros(file, pos, alignment):
    target = (pos + alignment - 1) & (0x100000000 - alignment)
    amount = target - pos
    file.write(b"\0" * amount)


###########################################################################################################################################################


def createBecArchive(dir, filename, becmap, gc, demobec, ignorechecksum, debug=False):
    print("createBecArchive")
    FileAlignment = 0x0
    NrOfFiles = 0x0
    HeaderMagic = 0x0

    readfileListResults = readFileList(becmap)
    FileAlignment = readfileListResults[1]
    HeaderMagic = readfileListResults[2]

    RomMap.extend(readfileListResults[0])

    print("*** : " + str(readfileListResults[3]))
    # include any new files
    RomMap.extend(readfileListResults[3])

    if os.path.dirname(filename) != "":
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
    output_rom = open(filename, "wb")

    # write header

    ignoreChecksumVersion = 0x1
    useChecksumVersion = 0x3
    version = useChecksumVersion
    if ignorechecksum:
        version = ignoreChecksumVersion

    NrOfFiles = len(RomMap)

    print("Creating file with : " + str(NrOfFiles) + " entries")

    output_rom.write(
        struct.pack(
            "<4sHHII",
            b" ceb",
            int(version),
            int(FileAlignment),
            int(NrOfFiles),
            int(HeaderMagic),
        )
    )

    addr = 0x10 + NrOfFiles * 0x10 + (FileAlignment - 1)
    addr &= 0x100000000 - FileAlignment

    print("After header position : " + str(output_rom.tell()))
    print("Start address : " + str(addr))

    baseAddr = addr
    currentAddr = baseAddr

    RomMap.sort(key=operator.attrgetter("DataOffset"))  # address

    print("Sorted Offset")

    count = 0
    lastItem = None

    for item in RomMap:
        duplicate = False

        oldSize = item.DataSize
        item.OldSize = oldSize
        item.DataSize = os.path.getsize(dir + "/" + item.FileName)
        if oldSize != item.DataSize:
            print(
                item.FileName
                + " size changed : "
                + str(oldSize)
                + " / "
                + str(item.DataSize)
            )

        if lastItem is not None:
            if (
                lastItem.OriginalDataOffset == item.OriginalDataOffset
                and item.IsNew == False
            ):
                duplicate = True

        if duplicate:
            lastItem.Checksum = 0x2000000
            item.Checksum = 0x2000000
            item.DataOffset = lastItem.DataOffset
        else:
            if item.IsNew:
                print(
                    "Adding new item "
                    + item.FileName
                    + " at position "
                    + str(currentAddr)
                )

            item.DataOffset = currentAddr
            currentAddr += item.DataSize
            currentAddr += FileAlignment - 1
            # checksum
            currentAddr += 8
            currentAddr &= 0x100000000 - FileAlignment

        lastItem = item

    RomMap.sort(key=operator.attrgetter("PathHash"))  # address
    # RomMap.sort(key=operator.attrgetter('DataOffset')) # address
    for item in RomMap:
        output_rom.write(struct.pack("<I", item.PathHash))
        output_rom.write(struct.pack("<I", item.DataOffset))
        output_rom.write(struct.pack("<I", item.CheckSum))
        output_rom.write(struct.pack("<I", item.DataSize))

    alignFileSizeWithZeros(output_rom, output_rom.tell(), FileAlignment)

    print("After header write and align : " + str(output_rom.tell()))

    print("Sorted DataOffset")

    print("RomMap Size : " + str(len(RomMap)))

    RomMap.sort(key=operator.attrgetter("DataOffset"))  # address
    i = 0
    for item in RomMap:
        # handle items that had the same offset in the file
        if item.DataOffset < output_rom.tell():
            # print("Skipping duplicate "+item.FileName)
            continue

        filepath = dir + "/" + item.FileName
        filepath = normpath(filepath)
        file = open(filepath, "rb")
        filedata = bytearray(file.read())
        file.close()
        output_rom.write(filedata)
        if item.DataSize > 0:
            output_rom.write(struct.pack("<II", item.CheckSum, 0))

        if item.OldSize != item.DataSize:
            print(
                "Adding new file "
                + item.FileName
                + " hash "
                + str(item.PathHash)
                + " with dataoffset + "
                + str(item.DataOffset)
                + " size "
                + str(item.DataSize)
            )

        alignFileSizeWithZeros(output_rom, output_rom.tell(), FileAlignment)
        # print("After data write and align : "+str(output_rom.tell()))

        output_rom.flush()

        i += 1
        if (i % 2500) == 0:
            print("write progress... " + str(i) + "/" + str(len(RomMap)))


###########################################################################################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-pack",
        action="store",
        nargs=3,
        type=str,
        metavar=("inputDir", "outputFile", "becFilelist"),
        help="pack files into a bec-archive",
    )
    group.add_argument(
        "-unpack",
        action="store",
        nargs=2,
        type=str,
        metavar=("inputFile", "outputDir"),
        help="unpack files from a bec-archive",
    )
    # group.add_argument('-scan', action='store', nargs=1, type=str, metavar=("inputDir", ), help="scan files in archive")
    group.add_argument(
        "-readfilelist",
        action="store",
        nargs=1,
        type=str,
        metavar=("inputFile",),
        help="read file list and package extra files",
    )

    parser.add_argument(
        "--demobec", action="store_true", help="demo file mode for bec"
    )  # switch between demo and non demo formats as they differ
    parser.add_argument(
        "--ignorechecksum", action="store_true", help="test ignore checksum for repack"
    )  #

    args = parser.parse_args()

    start = time.time()
    debug = True
    demobec = 0
    ignorechecksum = 0

    if args.demobec:
        demobec = 1

    if args.ignorechecksum:
        ignorechecksum = 1

    print("Main demobec " + str(demobec))

    if args.pack:
        createBecArchive(
            args.pack[0], args.pack[1], args.pack[2], demobec, ignorechecksum, debug
        )
    if args.unpack:
        unpackBecArchive(args.unpack[0], args.unpack[1], demobec, debug)
    # if args.scan:
    #    scanFiles(args.scan[0])
    if args.readfilelist:
        readFileList(args.readfilelist[0])

    if debug:
        elapsed_time_fl = time.time() - start
        print("passed time: " + str(elapsed_time_fl))
