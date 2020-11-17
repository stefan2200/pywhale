import setuptools

setuptools.setup(
    name="pywhale",
    version="0.0.1",
    author="stefan2200",
    author_email="stefan@stefanvlems.nl",
    description="Tool for detecting malicious emails and SMTP misconfiguration",
    url="https://github.com/stefan2200/pywhale",
    entry_points={
        'console_scripts': ['pywhale=pywhale.main:main'],
    },
    packages=setuptools.find_packages(),
    package_data={'': [
        'app/static/js/*',
        'app/static/css/*',
        'app/templates/*',
        'attachments/*',
        'indicators/*'
    ]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "flask",
        "beautifulsoup4",
        "validators",
        "tldextract"
    ],
    python_requires='>=3.6',
)