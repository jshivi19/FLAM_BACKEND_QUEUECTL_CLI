from setuptools import setup, find_packages

setup(
    name="queuectl",
    version="1.0.0",
    description="A CLI-based background job queue system",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "psutil>=5.9.0",
    ],
    entry_points={
        'console_scripts': [
            'queuectl=queuectl.__main__:main',
        ],
    },
    python_requires='>=3.7',
)
