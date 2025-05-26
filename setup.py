"""Setup script for Backlog Backup tool."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="backlog-backup",
    version="0.1.0",
    author="Tomoya Yamamoto",
    author_email="tmyymmt@gmail.com",
    description="Tool for backing up Backlog project data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tmyymmt/backlog-backup",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "scraping": [
            "selenium>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "backlog-backup=backlog_backup.cli:main",
        ],
    },
)