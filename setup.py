from setuptools import setup, find_packages

setup(
    name='AIDataAugment',
    version='1.1.0',
    packages=find_packages(),
    install_requires=[
        'google-generativeai',
        'pandas',
        'openpyxl',
    ],
    author='Farouk Daboussi',
    author_email='faroukdaboussi2009@gmail.com',
    description='A Python package for efficient and customizable text augmentation for NLP tasks.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/FaroukDaboussi0/AIDataAugment',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
        package_data={
        '': ['usage_example.ipynb'],
    },
    include_package_data=True,
)
