from setuptools import setup, find_packages

setup(
    name="movie-genre-predictor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "metaflow>=2.10.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
        "nltk>=3.8.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.20.0",
        "pydantic>=2.0.0",
        "requests>=2.30.0",
        "boto3>=1.28.0",
        "python-dotenv>=1.0.0",
        "joblib>=1.3.0",
    ],
    python_requires=">=3.10",
    author="Your Name",
    author_email="your.email@example.com",
    description="ML project that predicts movie genres based on plot summaries",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
