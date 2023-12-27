# Copyright 2014 Modelling, Simulation and Design Lab (MSDL) at
# McGill University and the University of Antwerp (http://msdl.cs.mcgill.ca/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class BaseTracer:
	"""
	The baseclass for the tracers, allows for inheritance.
	"""
	def __init__(self, uid, server):
		"""
		Constructor

		:param uid: the UID of this tracer
		:param server: the server to make remote calls on
		"""
		self.uid = uid
		self.server = server

	def startTracer(self, recover):
		"""
		Starts up the tracer

		:param recover: whether or not this is a recovery call (so whether or not the file should be appended to)
		"""
		pass

	def stopTracer(self):
		"""
		Stop the tracer
		"""
		pass

	def trace(self, time, text):
		"""
		Actual tracing function

		:param time: time at which this trace happened
		:param text: the text that was traced
		"""
		pass


	def traceInternal(self, aDEVS):
		"""
		Tracing done for the internal transition function

		:param aDEVS: the model that transitioned
		"""
		pass

	def traceConfluent(self, aDEVS):
		"""
		Tracing done for the confluent transition function

		:param aDEVS: the model that transitioned
		"""
		pass

	def traceExternal(self, aDEVS):
		"""
		Tracing done for the external transition function

		:param aDEVS: the model that transitioned
		"""
		pass

	def traceInit(self, aDEVS, t):
		"""
		Tracing done for the initialisation

		:param aDEVS: the model that was initialised
		:param t: time at which it should be traced
		"""
		pass

	def traceUser(self, time, aDEVS, variable, value):
		"""
        Tracing done for a user change

        :param aDEVS: the model that was initialised
        :param time: time at which it should be traced
        :param variable: the variable that was changed
        :param value: the new value for the variable
        """
		pass