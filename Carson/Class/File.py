import psutil
import typing
import win32api
import os
from os import path, remove
from os.path import abspath
import shutil
from io import StringIO, BytesIO
from enum import Enum
import configparser


class FileHelper(object):
    @classmethod
    def get_file_properties(cls, file) -> dict:
        """
        Read all properties of the given file and return them as a dictionary.

        EXAMPLE::

            prop = FileHelper.get_file_properties(r"C:\\Windows\\System32\\cmd.exe")
            for key, value in prop['StringFileInfo'].items():
                print(f'{key:<15} {value if value else "":<30}')
        """

        prop_names = ('Comments', 'InternalName', 'ProductName',
                      'CompanyName', 'LegalCopyright', 'ProductVersion',
                      'FileDescription', 'LegalTrademarks', 'PrivateBuild',
                      'FileVersion', 'OriginalFilename', 'SpecialBuild')

        return_dict = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}
        try:
            # backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc
            fixed_info = win32api.GetFileVersionInfo(file, '\\')
            return_dict['FixedFileInfo'] = fixed_info
            return_dict['FileVersion'] = "%d.%d.%d.%d" % (fixed_info['FileVersionMS'] / 65536,
                                                          fixed_info['FileVersionMS'] % 65536,
                                                          fixed_info['FileVersionLS'] / 65536,
                                                          fixed_info['FileVersionLS'] % 65536)

            # \VarFileInfo\Translation returns list of available (language, code-page)
            # pairs that can be used to retrieve string info. We are using only the first pair.
            lang, codepage = win32api.GetFileVersionInfo(file, '\\VarFileInfo\\Translation')[0]

            # any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle
            # two are language/codepage pair returned from above
            dict_info = {}
            for cur_prop_name in prop_names:
                prop_name = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, cur_prop_name)
                dict_info[cur_prop_name] = win32api.GetFileVersionInfo(file, prop_name)
            return_dict['StringFileInfo'] = dict_info
        except:
            pass
        return return_dict

    @classmethod
    def delete_dir(cls, dir_path):
        """
        recursive delete all files include directory.

        :param dir_path:
        :return:
        """
        if path.exists(dir_path):
            shutil.rmtree(dir_path)

    @classmethod
    def if_dir_not_exist_then_create(cls, chk_path, is_dir_name_have_dot=False) -> bool:
        """

        :param chk_path:
        :param is_dir_name_have_dot:
        :return: True: create successful, otherwise not.
        """
        try:
            if not path.exists(chk_path):
                if is_dir_name_have_dot:
                    os.makedirs(chk_path)  # directory name contain "."
                else:
                    if chk_path.rfind('.') > 0:  # it directory name contains "." then create the directory which doesn't include extension name.
                        os.makedirs(path.dirname(chk_path)) if not path.exists(path.dirname(chk_path)) else None
                    else:
                        os.makedirs(chk_path)
        except OSError:
            return False
        return True

    @classmethod
    def move_file(cls, src_file, dst_file):
        """
        .. warning:: dst_file that will be replaced of src_file no matter dst_file exists or not.

        :param src_file:
        :param dst_file:
        :return:
        """
        # shutil.move(src_file, dst_file, copy_function=shutil.copy2)
        shutil.move(src_file, dst_file)

    @classmethod
    def file_path_add_prefix(cls, file, pre_fix_name) -> str:
        """
            >>> FileHelper.file_path_add_prefix("C:\\Test\\fileA.txt", "My_")
            'C:\\Test\\My_fileA.txt'
        """
        dir_name = path.splitext(path.dirname(file))[0]
        new_file_name = pre_fix_name + path.basename(file)
        return abspath(path.join(dir_name, new_file_name))

    @classmethod
    def get_file_path(cls, file):
        """
        to get filename which name is too long

        :param file: abspath
        :return:
        """
        if path.exists(abspath(file)):
            return win32api.GetShortPathName(file)
        else:
            # sometimes GetShortPathName are not working but "\\\\?\\" that can
            return "\\\\?\\" + file

    @classmethod
    def get_file_info(cls, file):
        return os.stat(FileHelper.get_file_path(file))

    @classmethod
    def get_file_attrib(cls, file):
        return win32api.GetFileAttributes(FileHelper.get_file_path(file))

    @classmethod
    def is_illegal_file_name(cls, file_path):
        for illegal_chr in ['<', '>', '?', '[', ']', ':', '|', '*']:
            if file_path.find(illegal_chr) > 0:
                return True
        return False

    @classmethod
    def rename(cls, src_file, dst_file, ignore_file_exist_error):
        if ignore_file_exist_error and path.exists(dst_file):
            os.remove(dst_file)
        os.rename(src_file, dst_file)

    @classmethod
    def name_normalized(cls, file_path,
                        is_need_rename=False,
                        list_replace_mapping=(('[', '☶'), (']', '☲'),),
                        **option) -> tuple:
        """
        if filename that contains illegal character then will replace those character by "list_replace_mapping" to rename the file.

        :return
            new_file_name, be_normalized

            if successful "be_normallizd: will be True, otherwise not.

        :param
            is_need_rename: rename whether or not

            option:
                - only_base_name: handle basename only
                - ignore_file_exist_error: file already exists after rename, then forced rename or not?

        USAGE::

            name_normalized = FileHelper.name_normalized
            new_path, be_normalized = name_normalized("C:\\[dir]\\sub_dir\\my_[test].txt")
            ('C:\\☶dir☲\\sub_dir\\my_☶test☲.txt', True)

            name_normalized("C:\\[dir]\\sub_dir\\my_[test].txt", only_base_name=True)
            ('C:\\[dir]\\sub_dir\\my_☶test☲.txt', Ture)

            name_normalized("my_[test].txt", only_base_name=True)
            my_☶test☲.txt, True

            name_normalized("my_[test].txt")
            'my_☶test☲.txt', True

            name_normalized("my_test.txt")
            'my_test.txt', False
        """
        check_name = path.splitext(path.basename(file_path))[0] \
            if option.get('only_base_name') \
            else file_path  # handle basename only

        if not FileHelper.is_illegal_file_name(check_name):
            return file_path, False  # means: the file is legal so we don't do anything.

        for cur_chr, replace_chr in list_replace_mapping:
            check_name = check_name.replace(cur_chr, replace_chr)

        new_file_name = path.join(path.dirname(file_path), check_name) \
            if option.get('only_base_name') \
            else check_name
        if file_path.find('.') and option.get('only_base_name'):
            ext_name = path.splitext(file_path)[1]
            new_file_name += ext_name

        if is_need_rename:
            if option.get('ignore_file_exist_error'):
                if path.exists(new_file_name):
                    os.remove(new_file_name)
            os.rename(file_path, new_file_name)

        return new_file_name, True

    @classmethod
    def copy_config(cls, org_config) -> configparser.ConfigParser:
        """
        .. note:: you can assign the string to `org_config`, but its data must be able to read by ConfigParser

        USAGE::

            org_config = configparser.ConfigParser()
            org_config.read([file1, file2], encoding='utf-8')
            new_config = FileHelper.copy_config(org_config)

        :param org_config: type: configparser.ConfigParser, str
        :return:
        """
        if not isinstance(org_config, (configparser.ConfigParser, str)):
            raise TypeError(f'org_config must be `configparser.ConfigParser` or `str`')

        with StringIO() as memory_file:
            if isinstance(org_config, str):
                memory_file.write(org_config)
            else:
                org_config.write(memory_file)
            memory_file.seek(0)
            new_config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
            new_config.read_file(memory_file)
        return new_config

    @staticmethod
    def kill_process(kill_name_list: typing.List[str]):
        for process in psutil.process_iter():
            for process_name in kill_name_list:
                if process.name() == process_name:
                    process.kill()


class MemoryFile:
    """
    easier to write or read data from memory

    USAGE::

        import pandas as pd
        tmp_file = MemoryFile()
        tmp_file.write('name|age')
        tmp_file.write('Carson|26')
        tmp_file.writelines(['Person_1|18', 'Person_2|12'])
        print(tmp_file.read())
        tmp_file.io.seek(0)
        print(tmp_file.readline())  # make sure cursor waiting position is what you want before readline
        tmp_file.io.seek(0)
        df = pd.read_csv(tmp_file.io, sep='|')  # must seek(0) before read_csv.
        tmp_file.close()

        with MemoryFile(MemoryFile.IoType.BYTE) as tmp_file_2:
            tmp_file_2.write('name|age')
            tmp_file_2.write('中文|26')
            tmp_file_2.writelines(['Person_1|18', 'Person_2|12'])
            print(tmp_file_2.read())
            tmp_file_2.seek(0)
            print(tmp_file_2.readline())
            tmp_file_2.seek(0)
            df = pd.read_csv(tmp_file_2.io, sep='|')

            with open('temp.temp', 'wb') as f:
                f.write(tmp_file_2.read())
            with open('temp.temp', 'r', encoding='utf-8') as f:
                print(f.read())
    """

    class IoType(Enum):
        STR = 'STR'
        BYTE = 'BYTE'

    __slots__ = ['_io', '_encoding', '_mode']

    def __init__(self, mode: IoType = IoType.STR, encoding='utf-8'):
        self._encoding = encoding
        self._io = StringIO() if mode == MemoryFile.IoType.STR else BytesIO()
        self._mode = mode

    @property
    def io(self): return self._io

    @property
    def mode(self): return self._mode

    @property
    def encoding(self): return self._encoding

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.io.close()

    def write(self, msg) -> None:
        msg = msg + '\n'
        if self.mode == MemoryFile.IoType.BYTE:
            msg = msg.encode(self.encoding)
        self.io.write(msg)

    def writelines(self, list_msg: list) -> None:
        list_msg = [line + '\n' for line in list_msg] if self.mode == MemoryFile.IoType.STR else \
            [(line + '\n').encode(self.encoding) for line in list_msg]
        self.io.writelines(list_msg)

    def seek(self, n: int = 0):
        return self.io.seek(n)

    def readline(self):
        return self.io.readline()[:-1]  # remove '\n'

    def read(self):
        return self.io.getvalue()

    def close(self):  # release memory
        self.io.close()


class TempFile:
    """
    If you need temp file and that can be auto-deleted after you aren't using it.

    USAGE::

        with TempFile('temp.temp') as tmp_f:
            tmp_f.close()  # it's only using for other programs will do something by it (Option)
            other_process(tmp_file_path)
    """

    __slots__ = ['_file', '_file_path', '_encoding', ]

    def __init__(self, file_path, encoding='utf-8', ignore_file_exists_error=False):
        self._file_path = abspath(file_path)
        if path.exists(self.file_path):
            if not ignore_file_exists_error:
                raise FileExistsError(f'file:{self.file_path}')
            else:
                remove(self.file_path)

        self._encoding = encoding
        self._file = None

    @property
    def encoding(self):
        return self._encoding

    @property
    def file_path(self):
        return self._file_path

    @property
    def file(self):
        return self._file

    def __enter__(self):
        self._file = open(self.file_path, 'w', encoding=self.encoding)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('__exit__')
        self.file.close()  # it's ok no matter whether that already closed or not.
        if path.exists(self.file_path):
            remove(self.file_path)
