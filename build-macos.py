import os
import subprocess
import sys
# import shutil

# from distutils.core import setup

# def tree(src):
#     return [(root, map(lambda f: os.path.join(root, f), files))
#         for (root, dirs, files) in os.walk(os.path.normpath(src))]


# if os.path.exists('build'):
#     shutil.rmtree('build')

# if os.path.exists('dist/index.app'):
#     shutil.rmtree('dist/index.app')

# ENTRY_POINT = ['src/index.py']

# DATA_FILES = tree('dist')
# OPTIONS = {
#     'argv_emulation': False,
#     'strip': True,
#     'iconfile': 'src/assets/logo.icns',
#     'includes': ['WebKit', 'Foundation', 'webview', 'pkg_resources.py2_warn']
# }

# setup(
#     app=ENTRY_POINT,
#     data_files=DATA_FILES,
#     options={'py2app': OPTIONS},
#     setup_requires=['py2app'],
# )

def build_with_spec():
    spec_file = 'GeoshotApp.spec'

    if not os.path.exists(spec_file):
        print("Spec File Not Found")
        sys.exit(1)
    
    subprocess.run(['pyinstaller', spec_file], check=True)

if __name__ == '__main__':
    build_with_spec()