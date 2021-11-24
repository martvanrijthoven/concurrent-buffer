from setuptools import setup

# # read the contents of your README file
# from pathlib import Path
# this_directory = Path(__file__).parent
# long_description = (this_directory / "README.md").read_text()

setup(
    name='concurrentbuffer',
    version='0.0.5',
    author='Mart van Rijthoven',
    author_email='mart.vanrijthoven@gmail.com',
    packages=['concurrentbuffer'],
    license='LICENSE.txt',
    install_requires=['numpy>=1.18.1'],
    url='https://github.com/martvanrijthoven/concurrent-buffer'
)
