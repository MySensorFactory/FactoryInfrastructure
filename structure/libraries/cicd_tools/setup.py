from setuptools import setup, find_packages

setup(
    name='cicd_tools',
    version='1.0.0',
    description='Cicd tools python package',
    author='Damian Wojcik',
    license='BSD 2-clause',
    packages=find_packages(),
    install_requires=['PyYAML',
                      'boto3',
                      'kubernetes',
                      'pydantic'
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)