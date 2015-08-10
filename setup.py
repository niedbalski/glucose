from setuptools import setup, find_packages 

dependencies = [] 

setup(
    name="glucose",
    version="0.1a",
    packages=find_packages(),
    install_requires=dependencies,
    author="Jorge Niedbalski R.",
    author_email="jnr@metaklass.org",
    include_package_data=True,
    license="BSD",
    entry_points={
	'console_scripts' : [
		'glucose = glucose.app:main'
	]
    },
    classifiers=['Development Status :: 3 - Alpha',
                'Intended Audience :: Developers',
                'Operating System :: Unix '] )
