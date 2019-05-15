
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import os
from io import open

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

terraform_files = package_files('shipit/terraform')
print(terraform_files)


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
    package_data={'': ['shipit.yml', 'Dockerfile', 'config/*', *terraform_files]},
    include_package_data=True,
    python_requires='!=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
    install_requires=[
        'docker>=3',
        'numpy>=1',
        'awscli',
        'pyyaml>=3.13,<3.15',
        'delegator.py>=0.1.1',
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
