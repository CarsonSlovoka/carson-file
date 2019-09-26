===================
File
===================

.. sectnum::



Install
===============

    * ``pip install carson-file``

import packages
===============

.. code-block:: python

    from Carson.Class.File import FileHelper, TempFile, MemoryFile


SOURCE DOCUMENT
===============

FileHelper
--------------

class FileHelper
  Class methods defined here:
  
  delete_dir(dir_path)
      recursive delete all files include directory.
  
  file_path_add_prefix(file, pre_fix_name) -> str
      >>> FileHelper.file_path_add_prefix("C:\Test\fileA.txt", "My")
      'C:\Test\MyfileA.txt'
  
  get_file_attrib(file)
  
  get_file_info(file)
  
  get_file_path(file)
      to get filename which name is too long
  
  get_file_properties(file) -> dict
      Read all properties of the given file and return them as a dictionary.
      
      EXAMPLE::
      
          prop = FileHelper.get_file_properties(r"C:\Windows\System32\cmd.exe")
          for key, value in prop['StringFileInfo'].items():
              print(f'{key:<15} {value if value else "":<30}')

      OUTPUT::

          Comments
          InternalName    cmd
          ProductName     Microsoft® Windows® Operating System
          CompanyName     Microsoft Corporation
          LegalCopyright  © Microsoft Corporation. All rights reserved.
          ProductVersion  10.0.18362.356
          FileDescription Windows 命令處理程式
          LegalTrademarks
          PrivateBuild
          FileVersion     10.0.18362.356 (WinBuild.160101.0800)
          OriginalFilename Cmd.Exe.MUI
          SpecialBuild
  
  if_dir_not_exist_then_create(chk_path, is_dir_name_have_dot=False) -> bool
      :return: True: create successful, otherwise not.
  
  is_illegal_file_name(file_path)
  
  move_file(src_file, dst_file)
      .. warning:: dst_file that will be replaced of src_file no matter dst_file exists or not.

  
  name_normalized(file_path, is_need_rename=False, list_replace_mapping=(('[', '☶'), (']', '☲')), option: dict) -> tuple
      if filename that contains illegal character then will replace those character by "list_replace_mapping" to rename the file.
      
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
  
  rename(src_file, dst_file, ignore_file_exist_error)

  copy_config(org_config) -> configparser.ConfigParser
      .. note:: you can assign the string to `org_config`, but its data must be able to read by ConfigParser

      USAGE::

          org_config = configparser.ConfigParser()
          org_config.read([file1, file2], encoding='utf-8')
          new_config = FileHelper.copy_config(org_config)

  Static methods defined here:
  
  kill_process(kill_name_list: List[str])
 

class MemoryFile
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

class TempFile
  If you need temp file and that can be auto-deleted after you aren't using it.
  
  USAGE::

      with TempFile('temp.temp') as tmp_f:
          tmp_f.close()  # it's only using for other programs will do something by it (Option)
          other_process(tmp_file_path)


more detail please see the source file.

all function and class have illustrate in source file