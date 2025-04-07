import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="saibautils",
    version="0.0.1",
    description="Utilities such as dataclasses, helpers and logging for Python",
    long_description=long_description,
    install_requires=[
        'requests',
        'elasticsearch',
        'python-openobserve'
    ],
    long_description_content_type="text/markdown",
    url="https://github.com/saibamo/saibautils",
    author="Saibamo",
    packages=["saibautils"])