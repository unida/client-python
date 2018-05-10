from setuptools import setup

setup(name='unida',
	version='0.1',
	description='Unida Client',
	url='https://github.com/unida/client-python.git',
	author='Unida',
	author_email='info@unida.io',
	license='MIT',
	packages=['unida'],
	zip_safe=False,
	install_requires=[
		"six==1.11.0",
		"requests==2.18.4",
		"websocket-client==0.47.0"
	]
)