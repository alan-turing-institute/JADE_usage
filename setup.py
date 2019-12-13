from setuptools import setup, find_packages

setup(
    name="jade-usage",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "tabulate"
        ],
    entry_points={
        'console_scripts': [
            'jade-usage = jade_usage.__main__:main'
            ]
        }
    )
