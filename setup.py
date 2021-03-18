import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hidebehind",
    version="0.0.1",
    author="multifrench",
    author_email="multifrench@protonmail.com",
    description="A steganography library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/multifrench/hidebehind",
    project_urls={
        "Bug Tracker": "https://github.com/multifrench/hidebehind/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Intended Audience :: Education",
        "Topic :: Security",
        "Natural Language :: English",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    packages=setuptools.find_packages(exclude=['docs', 'tests']),
    install_requires=['numpy', 'Pillow'],
    python_requires=">=3.9",
)
