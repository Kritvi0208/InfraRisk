from setuptools import setup, find_packages

setup(
    name='infrarisk-ai',
    version='0.1.0',
    author='Zetheta Algorithms',
    description='Infrastructure project finance AI platform',
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[
        'fastapi>=0.104.0',
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'scikit-learn>=1.3.0',
        'xgboost>=2.0.0',
        'torch>=2.1.0',
    ],
)
