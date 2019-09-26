from distutils.core import setup

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

version_number = '0.0.0'

setup(
    name='carson-file',
    version=version_number,  # x.x.x.{dev, a, b, rc}
    packages=['Carson', r'Carson\Class'],
    license="Apache-2.0",

    author='Carson',
    author_email='jackparadise520a@gmail.com',

    scripts=[],

    install_requires=['pypiwin32', 'pywin32', 'psutil', ],

    url='https://github.com/CarsonSlovoka/carson-file',

    description='create a temp file, memory file, rename, move, copy, kill the process, get attribute, create a directory, etc.',
    long_description=long_description,
    long_description_content_type='text/x-rst',  # text/markdown
    keywords=['File'],

    download_url=f'https://github.com/CarsonSlovoka/carson-file/tarball/v{version_number}',
    python_requires='>=3.6.2,',

    zip_safe=False,
    classifiers=[  # https://pypi.org/classifiers/
        'Topic :: System :: Logging',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: Chinese (Traditional)',
        'Natural Language :: English',
        'Operating System :: Microsoft',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
