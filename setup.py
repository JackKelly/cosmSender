from setuptools import setup, find_packages

setup(
    name = "cosmSender",
    version = "0.12",
    packages = find_packages(),
    install_requires = ['pyserial>=2.4', 'simplejson'],
    author = "Jack Kelly",
    author_email = "",
    description = "Sender with caching for Cosm",
    license = "MIT",
    keywords = "cosm python",
    url = "http://github.com/JackKelly/cosmSender",
    download_url = "https://github.com/JackKelly/cosmSender/tarball/master",
    long_description="Use Python to send stuff to Cosm",
)
