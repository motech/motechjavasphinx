
from setuptools import setup

setup(
    name = "motechjavasphinx",
    packages = ["motechjavasphinx"],
    version = "0.2",
    author = "Grameen Foundation",
    author_email = "rlarubbio@grameenfoundation.org",
    url = "http://github.com/motech/motechjavasphinx",
    description = "Sphinx extension for executing javasphinx to documenting Java projects",
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries"
        ],
    install_requires=["javalang>=0.9.5", "lxml", "beautifulsoup4", "javasphinx>=0.9.11"],
    long_description = """\
================
motechjavasphinx
================

motechjavasphinx is an extension to the Sphinx documentation system which adds support
for executing javasphinx during the sphinx build.  The extension searches project poms
for packages exported through OSGi and only executes javasphinx on those classes.
"""    
)
