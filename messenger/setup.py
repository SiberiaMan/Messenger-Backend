import os
# try: # for pip >= 10
from pip._internal.req import parse_requirements
# except ImportError: # for pip <= 9.0.3
#   from pip.req import parse_requirements
from setuptools import setup, find_packages

current_path = os.path.dirname(os.path.abspath(__file__))
cureent_path = current_path + '/requirements.txt'

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session=False)

reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='messenger',
    platforms="all",
    packages=find_packages(exclude=["tests"]),
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'messenger-api = messenger.__main__:main',
            'analyzer-db = messenger.alembic.__main__:main'
        ]
    },
    include_package_data=True
)
