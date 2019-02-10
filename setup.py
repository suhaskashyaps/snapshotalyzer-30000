from setuptools import setup

setup(
    name='snapshotalyzer-30000',
    version='0.1',
    author="Suhas Kashyap",
    author_email="suhas.s.kashyap@gmail.com",
    description="Snapshotalyzer 30000 is a tool to manage EC2 snapshots",
    license="GPLv3+",
    packages=['shotty'],
    url="https://github.com/suhaskashyaps/snapshotalyzer-30000",
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        shotty=shotty.shotty:cli
    ''',
    
)
