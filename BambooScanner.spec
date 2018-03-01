# -*- mode: python -*-

block_cipher = None

assets = [ ( '.\\assets', 'assets' ) ]
dlls = [ ( 'C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\ucrt\\DLLs\\x64', '.' ),
         ( '.\\venv\\Lib\\site-packages\\scipy\\extra-dll', '.' ) ]

a = Analysis(['main.py'],
             pathex=['C:\\Users\\arosa\\PycharmProjects\\bamboo-scanner'],
             binaries=dlls,
             datas=assets,
             hiddenimports=['scipy.spatial', 'scipy._lib.messagestream'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='BambooScanner',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='BambooScanner')
