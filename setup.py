from setuptools import setup

setup(
    name='cascade-study',
    version='',
    packages=['', 'study', 'utils', 'datasets', 'implementations'],
    package_dir={'': 'cascade-study'},
    url='',
    license='',
    author='andrebreis',
    author_email='',
    description='',
    install_requires=['bitstring', 'joblib', 'plotly'],
    entry_points={
        'console_scripts': [
            'cascade-study=cmdline:execute',
        ]
    }
)
