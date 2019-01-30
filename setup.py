from distutils.core import setup
from tmDiff import __version__ as version

long_description = open('README.md').read()

setup(
    name="tm-diff",
    version=version,
    url="https://github.com/cms-l1-globaltrigger/tm-diff",
    author="Bernhard Arnold",
    author_email="bernhard.arnold@cern.ch",
    description="Compare the content of two XML trigger menus.",
    long_description=long_description,
    packages=["tmDiff"],
    scripts=["scripts/tm-diff"],
    license="GPLv3",
    keywords="",
    platforms="any",
    classifiers=[
        "Topic :: Software Development",
        "Topic :: Utilities",
    ]
)
