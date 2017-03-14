#!/usr/bin/env /usr/local/bin/python3
# encoding: utf-8

"""
用于将搜狗拼音词库scel文件转换为txt文件
@version: 0.1
@author: Gamelfie
@contact: fudenglong1417@gmail.com
@time: 2017/3/13 13:02
"""

from io import BufferedReader
import glob
import struct
import os
import sys


def __read_utf16_str(open_file, offset=-1, read_len=2):
    assert isinstance(open_file, BufferedReader)
    if offset >= 0:
        open_file.seek(offset)
    return open_file.read(read_len).decode('UTF-16LE')


def __read_unit16(open_file):
    assert isinstance(open_file, BufferedReader)
    try:
        return struct.unpack('<H', open_file.read(2))[0]
    except struct.error:
        pass
        # return struct.unpack('<H', open_file.read(2))[0]
        # struct.error: unpack requires a bytes object of length 2


def transform(source_file_or_dir):
    """
    用于将搜狗拼音词库转换为txt文件
    :param source_file_or_dir: scel文件或者包含scel文件的目录
    :return: 返回包含word的生成器 generator
    """

    files = []

    if os.path.isdir(source_file_or_dir):
        if not source_file_or_dir.endswith("/"):
            source_file_or_dir += "/"
        files += glob.glob(source_file_or_dir + "*.scel")
    elif os.path.isfile(source_file_or_dir):
        files.append(source_file_or_dir)
    else:
        raise FileNotFoundError("文件路径不存在")

    for file in files:
        file_size = os.path.getsize(file)
        with open(file, "rb") as f:
            try:
                hz_offset = 0
                mask = struct.unpack('128B', f.read(128))[4]
                if mask == 0x44:
                    hz_offset = 0x2628
                elif mask == 0x45:
                    hz_offset = 0x26c4

                title = __read_utf16_str(f, 0x130, 0x338 - 0x130)
                type_ = __read_utf16_str(f, 0x338, 0x540 - 0x338)
                desc = __read_utf16_str(f, 0x540, 0xd40 - 0x540)
                samples = __read_utf16_str(f, 0xd40, 0x1540 - 0xd40)
                # print("Title：%s" % title, "Type：%s" % type_, "Desc：%s" % desc, "Samples：%s" % samples, sep="\n")
                py_map = {}
                f.seek(0x1540 + 4)
                while True:
                    py_code = __read_unit16(f)
                    py_len = __read_unit16(f)
                    py_str = __read_utf16_str(f, -1, py_len)

                    if py_code not in py_map:
                        py_map[py_code] = py_str

                    if py_str == 'zuo':
                        break

                f.seek(hz_offset)
                while f.tell() != file_size:
                    word_count = struct.unpack('<H', f.read(2))[0]
                    pinyin_count = int(struct.unpack('<H', f.read(2))[0] / 2)

                    py_set = []
                    for i in range(pinyin_count):
                        py_id = __read_unit16(f)
                        py_set.append(py_map[py_id])
                    py_str = "'".join(py_set)

                    for i in range(word_count):
                        word_len = __read_unit16(f)
                        word_str = __read_utf16_str(f, -1, word_len)
                        f.read(12)
                        yield word_str
            except KeyError:
                pass
            except struct.error:
                # 求大神指针错误
                # mask = struct.unpack('128B', f.read(128))[4]
                # struct.error: unpack requires a bytes object of length 128
                pass


def transform_and_save(source_file_or_dir, target_file):
    """
    转换并且保存为文件
    :param source_file_or_dir: scel文件或者包含scel文件的目录
    :param target_file: 保存的目标文件
    :return:
    """
    words = []
    for word_ in transform(source_file_or_dir=source_file_or_dir):
        words.append(word_)
    with open(target_file, "w+", encoding="utf8") as f:
        f.write("\n".join(words))


def main():

    if len(sys.argv) < 2:
        raise Exception("缺少必要的参数")
    source_file_or_dir = sys.argv[1]

    target_file = "./dict.txt"
    if len(sys.argv) == 3:
        target_file = sys.argv[2]

    transform_and_save(source_file_or_dir, target_file)

if __name__ == "__main__":
    main()
