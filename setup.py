from setuptools import setup, find_packages

# 使用 UTF-8 编码读取 README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wframe",
    version="0.1.9",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "werkzeug>=2.0.0",
        "jinja2>=3.0.0",
        "apispec>=5.0.0",
        "marshmallow>=3.0.0",
        "apispec-webframeworks>=0.5.2",
        "bcrypt>=3.2.0",
        "PyJWT>=2.0.0",
        "python-dotenv>=0.19.0",
        "SQLAlchemy==1.4.50",
        "alembic>=1.7.0",
        "click>=8.1.7"
    ],
    entry_points={
        "console_scripts": [
            "wframe=wframe.cli:main"
        ]
    },
    author="xuehaoweng",
    author_email="13721113750@163.com",
    description="一个轻量级的 Python Web 框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xuehaoweng/wframe",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
) 