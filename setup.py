from setuptools import setup, Extension

known_subblocks = Extension('known', sources=['cascade-study/study/known_subblocks.c'])

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
    ext_modules=[known_subblocks],
    entry_points={
        'console_scripts': [
            'cascade-study=cmdline:execute',
        ]
    }
)
