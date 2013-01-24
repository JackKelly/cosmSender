from setuptools import setup, find_packages

setup(
    name = "cosmSender",
    version = "0.1",
    packages = find_packages(),
    install_requires = ['simplejson'],
    author = "Jack Kelly",
    author_email = "jack-list@xlk.org.uk",
    description = "Sender with caching for Cosm",
    license = "MIT",
    keywords = "cosm python",
    url = "http://github.com/JackKelly/cosmSender",
    download_url = "https://github.com/JackKelly/cosmSender/tarball/master",
    long_description = open('README').read()
)
