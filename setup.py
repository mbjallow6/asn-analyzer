from setuptools import setup, find_packages

setup(
    name="asn-analyzer",
    version="1.0.0",
    description="ASN Analysis Tool for BGP and Company Information",
    author="Your Team",
    author_email="your-email@domain.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "pydantic>=2.5.0",
        "aiohttp>=3.9.1",
        "tenacity>=8.2.3",
        "lxml>=4.9.3",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "pandas>=2.1.4",
        "click>=8.1.7",
        "colorama>=0.4.6",
        "tqdm>=4.66.1",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "asn-analyzer=main:cli",
        ],
    },
)
