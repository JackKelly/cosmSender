from setuptools import setup, find_packages

setup(
    name = "cosmSender",
    version = "0.1",
    packages = find_packages(),
    install_requires = ['pyserial>=2.4', 'simplejson'],
    author = "JackKelly",
    author_email = "",
    description = "Sender with caching for cosm",
    license = "",
    keywords = "cosm python",
    url = "http://github.com/JackKelly/cosmSender",
    download_url = "https://github.com/JackKelly/cosmSender/tarball/master",
    long_description="Use python to send stuff to cosm",
)
