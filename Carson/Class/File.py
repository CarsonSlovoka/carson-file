import psutil
import typing
import win32api
import os
from os import path, remove
from os.path import abspath
import shutil


class FileHelper(object):
    @classmethod
    def get_file_properties(cls, file) -> dict:
        """
        Read all properties of the given file and return them as a dictionary.
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

            # \VarFileInfo\Translation returns list of available (language, codepage)
            # pairs that can be used to retreive string info. We are using only the first pair.
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
        except OSError as e:
            return False
        return True

    @classmethod
    def move_file(cls, src_file, dst_file):
        """
        warning: dst_file that will be replaced of src_file no matter dst_file exists or not.
        :param src_file:
        :param dst_file:
        :return:
        """
        # shutil.move(src_file, dst_file, copy_function=shutil.copy2)
        shutil.move(src_file, dst_file)

    @classmethod
    def file_path_add_prefix(cls, file, pre_fix_name) -> str:
        """
            FileHelper.file_path_add_prefix("C:\\Test\\fileA.txt", "My_")
            'C:\\Test\\My_fileA.txt'
        """
        dir_name = path.splitext(path.dirname(file))[0]
        new_file_name = pre_fix_name + path.basename(file)
        return abspath(path.join(dir_name, new_file_name))

    @classmethod
    def get_file_path(cls, file):
        """
        purpose: to get filename which name is too long
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
        Purpose
        =========

        if filename that contains illegal character then will replace those character by "list_replace_mapping" to rename the file.

        :return
            new_file_name, be_normalized

            if successful "be_normallizd: will be True, otherwise not.

        :param
            is_need_rename: rename whether or not
            option：
                only_base_name: handle basename only
                ignore_file_exist_error: file already exists after rename, then forced rename or not?

        USAGE:
            name_normalized = FileHelper.name_normalized
            new_path, be_normalized = name_normalized("C:\\[dir]\sub_dir\my_[test].txt")
            ('C:\\☶dir☲\\sub_dir\\my_☶test☲.txt', True)

            name_normalized("C:\\[dir]\sub_dir\my_[test].txt", only_base_name=True)
            'C:\[dir]\sub_dir\my_☶test☲.txt', Ture

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

    @staticmethod
    def kill_process(kill_name_list: typing.List[str]):
        for process in psutil.process_iter():
            for process_name in kill_name_list:
                if process.name() == process_name:
                    process.kill()


class TempFile:
    """
    Purpose
    ==========

    If you need temp file and that can be auto-deleted after you aren't using it.

    USAGE::
        with TempFile('temp.temp') as tmp_f:
            tmp_f.close()  # it's only using for other programs will do something by it (Option)
            other_process(tmp_file_path)
    """

    __slots__ = ['_file', '_file_path', '_encoding', ]

    def __init__(self, file_path, encoding='utf-8', ignore_error=False):
        self._file_path = abspath(file_path)
        if path.exists(self.file_path):
            if not ignore_error:
                raise FileExistsError(f'file:{self.file_path}')
            else:
                remove(self.file_path)

        self._encoding = encoding
        self._file = ''

    @property
    def encoding(self): return self._encoding

    @property
    def file_path(self): return self._file_path

    @property
    def file(self): return self._file

    def __enter__(self):
        self._file = open(self.file_path, 'w', encoding=self.encoding)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('__exit__')
        self.file.close()  # it's ok no matter whether that already closed or not.
        if path.exists(self.file_path):
            remove(self.file_path)
