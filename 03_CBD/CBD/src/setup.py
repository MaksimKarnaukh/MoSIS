from setuptools import setup, find_packages

setup(name="pyCBD",
      version="1.6",
      description="Python CBD simulator",
      author=", ".join([
	      "Marc Provost <Marc.Provost@mail.mcgill.ca>",
	      "Hans Vangheluwe <Hans.Vangheluwe@uantwerpen.be>",
	      "Joachim Denil <Joachim.Denil@uantwerpen.be>",
	      "Claudio Gomes",
	      "Randy Paredis <Randy.Paredis@uantwerpen.be>"
      ]),
      url="http://msdl.cs.mcgill.ca/people/rparedis",
      packages=find_packages(include=('*', 'pyCBD.*')),
      package_data={
	      '': ['*.c', '*.h', '*.lark']
      },
)
