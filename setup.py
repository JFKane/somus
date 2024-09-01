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
    name='audio_testing_app',
    version='0.1.0',
    description='Audio Testing Application with plugin support',
    author='Your Name',
    author_email='your.email@example.com',
    ext_modules=cythonize(get_extensions()),
    packages=find_packages(),
    package_data={
        'core.plugins': ['*.py'],  # Include all Python files in the plugins directory
    },
    include_package_data=True,
    install_requires=[
        'fastapi',
        'uvicorn',
        'python-socketio',
        'numpy',
        'scipy',
        'librosa',
        'sounddevice',
        # Add any other dependencies your application needs
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.10',
)