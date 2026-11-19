from setuptools import setup

setup(
    name="rubplus",
    version="1.5.2",
    author="RubPlus Team",
    description="Asynchronous Rubika Bot API wrapper",
    packages=["rubplus"],
    package_dir={"rubplus": "."},
    include_package_data=True,
    install_requires=["httpx>=0.27.0"],
    extras_require={
        "webhook": ["fastapi>=0.100.0", "uvicorn[standard]>=0.23.0"],
        "html": ["markdownify>=0.11.0"],
        "dev": ["pytest>=7.0", "pytest-asyncio>=0.21", "build>=1.0"],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
)
