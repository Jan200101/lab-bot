# -*- coding: utf-8 -*-
import setuptools
import re

requirements = []
with open('requirements.txt') as f:
  requirements = f.read().splitlines()

version = None
with open('labbot/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

long_description = ""
with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="lab-bot",
    version=version,
    author="Jan Drögehoff",
    author_email="jandroegehoff@gmail.com",
    description="a modular gitlab bot oriented towards automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=[
        "labbot",
        "labbot.addons"
    ],
    license="MIT",
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",

        "Programming Language :: Python :: 3",

        "License :: OSI Approved :: MIT License",

        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",

        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",

    entry_points={
        'console_scripts': [
            'lab-bot=labbot.__main__:main',
        ],
    },

)
