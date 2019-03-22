
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='shipit',  # Required
    version='0.6.0',  # Required
    description='Package machine learning models for the web',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='http://github.com/qCaudron/shipit/',  # Optional
    author='Quentin Caudron',  # Optional
    author_email='quentincaudron@gmail.com',  # Optional
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='machine learning scikit keras docker',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'example']),  # Required
    package_data={'': ['shipit.yml', 'Dockerfile', 'config/*']},
    include_package_data=True,
    python_requires='!=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
    install_requires=[
        'docker==3.7.1',
        'numpy>=1',
        'pyyaml==5.1'
    ],
    entry_points={
        'console_scripts': [
            'shipit=shipit.cli:main',
        ],
    },
    project_urls={
        'Source': 'http://github.com/qCaudron/shipit/',
    },
)
