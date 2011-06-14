from setuptools import setup

setup(
    name='django-esi',
    version='0.0.1',
    description='Django ESI Generating application',
    author='Mike',
    author_email='mrfunyon@gmail.com',
    url='http://github.com/mrfunyon/django-esi/',
    packages=[
        'esi',
        'esi.templatetags',
    ],

    install_requires=[
        'setuptools',
        'django',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)