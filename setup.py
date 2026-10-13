import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sheypoor-mcp",
    version="1.0.0",
    author="Antigravity Agent",
    description="Model Context Protocol (MCP) server for Sheypoor classifieds platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    include_package_data=True,
    package_data={
        "sheypoor_mcp": ["data/*.json"],
    },
    entry_points={
        "console_scripts": [
            "sheypoor-mcp=sheypoor_mcp.server:main",
            "sheypoor-cli=sheypoor_mcp.cli:main",
        ],
    },
)
