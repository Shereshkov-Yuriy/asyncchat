from setuptools import setup, find_packages

setup(name="sher_client_chat",
      version="0.0.1",
      description="sher_client_chat",
      author="Yuriy Shereshkov",
      author_email="yuriy.shereshkoff@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy']
      )
