from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name="caprae_leadgen_tool",
    version="0.1.0",
    author="Caprae",
    author_email="info@caprae.com",
    description="A comprehensive lead generation and contact information enrichment tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mathamphetamine/caprae_leadgen_tool",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        'caprae_leadgen_tool': [
            'templates/*',
            'static/css/*',
            'static/js/*',
            'static/sample_data.csv',
        ],
    },
    entry_points={
        'console_scripts': [
            'caprae-leadgen=main:app.run',
        ],
    },
) 