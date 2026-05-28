from setuptools import setup, find_packages

setup(
    name="rubplus",
    version="1.5.1",
    author="RubPlus Team",
    description="Official Rubika Bot API wrapper with HTML support",
    packages=find_packages(),
    install_requires=["httpx>=0.27.0"],
    python_requires=">=3.8",
)