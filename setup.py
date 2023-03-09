from setuptools import setup, find_packages

setup(
    name="prototype",
    version="1.0.0",
    packages=find_packages(),
    package_dir={
        "server": "./server",
        "registrar": "./registrar",
        "client": "./client",
    },
)
