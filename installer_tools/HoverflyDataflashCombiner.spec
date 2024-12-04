# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew
block_cipher = None


a = Analysis(['Y:\\git\\DFLogTool/gui.py'],
             pathex=['Y:\\git\\DFLogTools_Installer'],
             # binaries=[('C:\\Users\\Stranjyr\\Anaconda3\\pkgs\\mkl-2021.3.0-haa95532_524\\Library\\bin\\mkl_intel_thread.1.dll', '.')],
             datas=[('Y:\\git\\DFLogTool\\log_parser\\editor.kv', 'log_parser')],
             hiddenimports=['win32timezone'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz, Tree('Y:\\git\\DFLogTool\\log_parser\\'),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          name='HoverflyDataflashCombiner',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
