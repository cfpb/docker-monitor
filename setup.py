from setuptools import find_packages, setup


with open("README.md") as f:
    long_description = f.read()


setup(
    name="docker-monitor",
    url="https://github.com/cfpb/docker-monitor",
    author="CFPB",
    license="CC0",
    version="1.0.0",
    description="Utility that enforces Prisma Cloud Docker image policies`",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "requests",
        "docker",
    ],
    extras_require={
        "testing": [
            "mock",
            "coverage",
            "flake8",
        ],
    },
    test_suite="tests",
    entry_points={
        "console_scripts": [
            "docker_monitor = docker_monitor:main",
        ]
    },
)
