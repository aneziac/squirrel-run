from setuptools import setup, find_packages


setup(
    name="Squirrel Run",
    version="0.1.0",
    description="2D side scroller",
    author="aneziac and PlayinWithFire123",
    url="https://github.com/aneziac/squirrel-run",
    packages=find_packages(),
    install_requires=[
        "pygame",
    ],
    python_requires='>=3.0'
)
