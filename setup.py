from setuptools import setup
import re

package_name = 'wiggle'

with open('README.md', 'r') as f:
    long_description = f.read()

with open(f'{package_name}/__init__.py', 'r') as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(),
        re.MULTILINE).group(1)

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()

setup(
    name=package_name,
    version=version,
    url=f'https://github.com/JohnVinyard/{package_name}',
    author='John Vinyard',
    author_email='john.vinyard@gmail.com',
    long_description=long_description,
    packages=[package_name],
    download_url=f'https://github.com/jvinyard/{package_name}/tarball/{version}',
    requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    setup_requires=[
        'lmdb',
        'requests',
        'numpy',
        'librosa',
        'scipy',
        'soundfile',
        'jsonschema'
    ],
    install_requires=[
        'lmdb',
        'requests',
        'numpy',
        'librosa',
        'scipy',
        'soundfile',
        'jsonschema'
    ],
    include_package_data=True,
    package_data={
        '': ['sampler.json', 'sequencer.json']
    },
)