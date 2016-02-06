#!/usr/bin/env python
# -*- coding: utf-8 -*-


from distutils.core import setup
from glob import glob
import sys
import time


try:
      data_file = [("Microsoft.VC90.CRT", glob(
          r'C:\\Windows\\WinSxS\\x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.30729.9158_none_5091b51ebcb97cdc\\*.*'))]
      setup(
          data_files=data_file
      )
      sys.path.append("C:\\Windows\\WinSxS\\x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.30729.9158_none_5091b51ebcb97cdc")
      setup(name='Canela Core',
            version='2.0.0',
            author='Julio Alves',
            description='Programa de Caixa da Canela Santa',
            windows=[{
                         "script": "Base_s.py",
                         "icon_resources": [(1, "bronze.ico")],
                         "dest_base": "Canela Core"
                     }],
            console=[{
                         "script": "Base_s.py",
                         "icon_resources": [(1, "bronze.ico")],
                         "dest_base": "Base_c"
                     }])
except Exception, e:
    print
    print
    print 'Programa interrompido'
    print e
    time.sleep(999999)
