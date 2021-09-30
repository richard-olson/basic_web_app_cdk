import setuptools

setuptools.setup(
    name="three_tier_webapp",
    version="0.0.1",

    description="A three tier web application built with CDK",
    long_description='A three tier web application that provides an overview of instances and databases. This CDK repo pairs with the application at https://github.com/malbertus/basic_web_app',
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "three_tier_webapp"},
    packages=setuptools.find_packages(where="three_tier_webapp"),

    install_requires=[
        "aws-cdk-lib>=2.0.0-rc.21",
        "constructs>=10.0.0,<11.0.0",
    ],

    python_requires=">=3.7",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: AWS Builders",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
