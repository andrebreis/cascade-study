from setuptools import setup, Extension

block_parity_inference = Extension('inference', sources=['cascade-study/study/block_parity_inference.c'])

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
    ext_modules=[block_parity_inference],
    entry_points={
        'console_scripts': [
            'cascade-study=cmdline:execute',
        ]
    }
)
