from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import os

# Exclude plugin files from compilation
def get_extensions():
    extensions = []
    for root, _, files in os.walk("core"):
        for file in files:
            if file.endswith(".py") and not root.endswith("plugins"):
                module_path = os.path.join(root, file)
                module_name = os.path.splitext(module_path.replace(os.path.sep, "."))[0]
                extensions.append(Extension(module_name, [module_path]))
    return extensions

setup(
    name='somus',
    version='0.1.0',
    packages=find_packages(),
    ext_modules=cythonize(get_extensions()),
    package_data={
        'core.plugins': ['*.py'],
    },
    include_package_data=True,
    install_requires=[
        # List your requirements here
        'fastapi',
        'uvicorn',
        'python-socketio',
        'numpy',
        'scipy',
        'librosa',
        'sounddevice',
        # Add any other dependencies
    ],
)