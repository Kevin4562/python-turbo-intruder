import os
from setuptools import setup

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "turbo_requests", "__version__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    url=about["__url__"],
    packages=["requests"],
    package_data={"": ["LICENSE", "NOTICE"]},
    package_dir={"": "turbo_requests"},
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[],
    license=about["__license__"],
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
    ],
    extras_require={
    },
    project_urls={
        "Source": about["__url__"],
    },
)