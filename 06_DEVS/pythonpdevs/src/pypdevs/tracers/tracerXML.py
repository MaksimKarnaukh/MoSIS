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

from pypdevs.tracers.tracerBase import BaseTracer
from pypdevs.util import runTraceAtController, toStr
import sys, re

class TracerXML(BaseTracer):
    """
    A tracer for XML tracing output
    """
    def __init__(self, uid, server, filename):
        """
        Constructor

        :param uid: the UID of this tracer
        :param server: the server to make remote calls on
        :param filename: file to save the trace to
        """
        super(TracerXML, self).__init__(uid, server)
        if server.getName() == 0:
            self.filename = filename
        else:
            self.filename = None

    def write_py23(self, string):
        try:
            self.xml_file.write(string)
        except TypeError:
            self.xml_file.write(string.encode())

    def startTracer(self, recover):
        """
        Starts up the tracer

        :param recover: whether or not this is a recovery call (so whether or not the file should be appended to)
        """
        if self.filename is None:
            # Nothing to do here as we aren't the controller
            return
        elif recover:
            self.xml_file = open(self.filename, 'a+')
        else:
            self.xml_file = open(self.filename, 'w')
        self.write_py23("<?xml version=\"1.0\"?>\n" + "<trace>\n")

    def stopTracer(self):
        """
        Stop the tracer
        """
        self.write_py23("</trace>")
        self.xml_file.flush()

    def trace(self, model_name, timestamp, event_kind, port_info, xml_state, str_state):
        """
        Save an XML entry for the provided parameters, basically wraps it in the necessary tags

        :param model_name: name of the model
        :param timestamp: timestamp of the transition
        :param event_kind: kind of event that happened, e.g. internal, external, ...
        :param port_info: actual information about the port
        :param xml_state: XML representation of the state
        :param str_state: normal string representation of the state
        """
        self.write_py23("<event>\n"
                          + "<model>" + model_name + "</model>\n"
                          + "<time>" + str(timestamp[0]) + "</time>\n"
                          + "<kind>" + event_kind + "</kind>\n"
                          + port_info
                          + "<state>\n"+ xml_state + "<![CDATA[" + str_state + "]]>\n</state>\n"
                          + "</event>\n")

    def traceInternal(self, aDEVS):
        """
        The trace functionality for XML output at an internal transition

        :param aDEVS: the model that transitioned
        """
        port_info = ""
        for I in range(len(aDEVS.OPorts)):
            if (aDEVS.OPorts[I] in aDEVS.my_output and 
                    aDEVS.my_output[aDEVS.OPorts[I]] is not None):
                port_info += '<port name="' + aDEVS.OPorts[I].getPortName() + '" category="O">\n'
                for j in aDEVS.my_output.get(aDEVS.OPorts[I], []):
                    port_info += "<message>" + str(j) + "</message>\n"
                port_info += "</port>\n"
        runTraceAtController(self.server, 
                             self.uid, 
                             aDEVS, 
                             [toStr(aDEVS.getModelFullName()), 
                                aDEVS.time_last, 
                                "'IN'", 
                                toStr(port_info), 
                                toStr(TracerXML.toXML(aDEVS.state)),
                                toStr(aDEVS.state)])

    def traceExternal(self, aDEVS):
        """
        The trace functionality for XML output at an external transition

        :param aDEVS: the model that transitioned
        """
        port_info = ""
        for I in range(len(aDEVS.IPorts)):
            port_info += '<port name="' + aDEVS.IPorts[I].getPortName() + '" category="I">\n'
            for j in aDEVS.my_input.get(aDEVS.IPorts[I], []):
                port_info += "<message>" + str(j) + "</message>\n"
            port_info += "</port>\n"
        runTraceAtController(self.server, 
                             self.uid, 
                             aDEVS, 
                             [toStr(aDEVS.getModelFullName()), 
                                aDEVS.time_last, 
                                "'EX'", 
                                toStr(port_info), 
                                toStr(TracerXML.toXML(aDEVS.state)),
                                toStr(aDEVS.state)])

    def traceConfluent(self, aDEVS):
        """
        The trace functionality for XML output at a confluent transition

        :param aDEVS: the model that transitioned
        """
        port_info = ""
        for I in range(len(aDEVS.IPorts)):
            port_info += '<port name="' + aDEVS.IPorts[I].getPortName() + '" category="I">\n'
            for j in aDEVS.my_input.get(aDEVS.IPorts[I], []):
                port_info += "<message>" + str(j) + "</message>\n"
            port_info += "</port>\n"
        runTraceAtController(self.server, 
                             self.uid, 
                             aDEVS, 
                             [toStr(aDEVS.getModelFullName()), 
                                aDEVS.time_last, 
                                "'EX'", 
                                toStr(port_info), 
                                toStr(TracerXML.toXML(aDEVS.state)),
                                toStr(aDEVS.state)])
        port_info = ""
        for I in range(len(aDEVS.OPorts)):
            if aDEVS.OPorts[I] in aDEVS.my_output:
                port_info += '<port name="' + aDEVS.OPorts[I].getPortName() + '" category="O">\n'
                for j in aDEVS.my_output.get(aDEVS.OPorts[I], []):
                    port_info += "<message>" + str(j) + "</message>\n"
                port_info += "</port>\n"
        runTraceAtController(self.server, 
                             self.uid, 
                             aDEVS, 
                             [toStr(aDEVS.getModelFullName()), 
                                aDEVS.time_last, 
                                "'IN'", 
                                toStr(port_info), 
                                toStr(TracerXML.toXML(aDEVS.state)),
                                toStr(aDEVS.state)])

    def traceInit(self, aDEVS, t):
        """
        The trace functionality for XML output at initialization

        :param aDEVS: the model that transitioned
        :param t: time at which it should be traced
        """
        runTraceAtController(self.server, 
                             self.uid, 
                             aDEVS, 
                             [toStr(aDEVS.getModelFullName()), 
                                t, 
                                "'EX'", 
                                "''", 
                                toStr(TracerXML.toXML(aDEVS.state)),
                                toStr(aDEVS.state)])

    @staticmethod
    def toXML(state):
        primitives = {
            int: "Integer",
            float: "Float",
            str: "String"
        }

        def create_multi_attrib(name, elem):
            cat = "C"
            if type(elem) in primitives:
                cat = "P"
                type_ = primitives[type(elem)]
                return "<attribute category=\"%s\"><name>%s</name><type>%s</type><value>%s</value></attribute>" % (
                cat, name, type_, str(elem))
            else:
                type_ = "Unknown"
                value = TracerXML.toXML(elem)
                return "<attribute category=\"%s\"><name>%s</name><type>%s</type><value>%s</value></attribute>" % (
                cat, name, type_, str(value))

        if isinstance(state, (str, int, float)):
            return "<attribute category=\"P\"><name>state</name><type>%s</type><value>%s</value></attribute>" % (primitives[type(state)], str(state))
        elif isinstance(state, dict):
            res = ""
            for k, v in state.items():
                name = re.sub("[^a-zA-Z0-9_]", "", k)
                res += create_multi_attrib(name, v)
            return "<attribute category=\"C\"><name>state</name><type>Map</type><value>%s</value></attribute>" % res
        elif isinstance(state, (list, tuple)):
            res = ""
            for ix, item in enumerate(state):
                name = "item-%d" % ix
                res += create_multi_attrib(name, item)
            return "<attribute category=\"C\"><name>state</name><type>List</type><value>%s</value></attribute>" % res
        elif hasattr(state, "toXML"):
            return state.toXML()
        elif hasattr(state, "__str__"):
            return TracerXML.toXML(str(state))
        return TracerXML.toXML({k: getattr(state, k) for k in dir(state) if not k.startswith("_") and not callable(getattr(state, k))})

