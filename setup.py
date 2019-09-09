from setuptools import setup

long_description = open('README.md').read()

setup(
    name="tm-diff",
    version='0.6.0',
    url="https://github.com/cms-l1-globaltrigger/tm-diff",
    author="Bernhard Arnold",
    author_email="bernhard.arnold@cern.ch",
    description="Compare the content of two XML trigger menus.",
    long_description=long_description,
    packages=['tmDiff'],
    install_requires=[
        #'tmTable>=0.7.3',
    ],
    entry_points={
        'console_scripts': [
            'tm-diff = tmDiff.main:main',
        ],
    },
    test_suite='tests',
    license="GPLv3",
    keywords="",
    platforms="any",
    classifiers=[
        "Topic :: Software Development",
        "Topic :: Utilities",
    ]
)
