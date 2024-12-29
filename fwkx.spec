a = Analysis(
    ['src/artisan.py'],
    pathex=['/path/to/your/project'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
exe = EXE(
    a, 
    # 其他配置...
    icon='fwkx.ico',  # 设置图标
)
