from setuptools import find_packages, setup

long_description = open("README.md").read()

setup(
    name='lbnotes',
    version='0.1.2',
    packages=find_packages(),
    author="lightblue",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/weilancys/lbnotes",
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-simplemde',
        'flask-wtf',
    ],
)