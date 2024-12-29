from setuptools import setup, find_packages

setup(
    name="my_project",  # 项目名称
    version="0.1.0",    # 项目版本
    author="myname",  # 作者信息
    author_email="your.email@example.com",  # 作者邮箱
    description="A brief description of your project",  # 项目描述
    long_description=open("README.md").read(),  # 从 README.md 加载长描述
    long_description_content_type="text/markdown",  # README 的类型（通常是 markdown）
    url="https://github.com/yourusername/my_project",  # 项目 URL（可以是 GitHub 地址）
    packages=find_packages(),  # 自动查找所有包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # 支持的 Python 版本
    install_requires=[
        "requests",  # 填入项目依赖的第三方库
    ],
)
