from setuptools import setup, find_packages
import os

def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'src', 'README.md')
    return open(readme_path, encoding='utf-8').read() if os.path.exists(readme_path) else ''


setup(
    name='penetration-testing-toolkit',
    version='1.0.0',
    author='Deepayan Dey',
    author_email='your.pandaaahacker007@gmail.com',
    description='Modular penetration testing toolkit for ethical hacking and security auditing',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/error404-004/penetration-testing-toolkit',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'requests',
        'paramiko',
        'scapy',
        'colorama',
        'python-nmap',
        'rich'  # Optional CLI/UX enhancements
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'pentoolkit=main:main',
        ]
    }
)