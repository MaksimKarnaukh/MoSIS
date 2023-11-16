import re
import pyCBD.naivelog as naivelog
import logging
from copy import deepcopy
from .util import enum, hash64
from collections import namedtuple

InputLink = namedtuple("InputLink", ["block", "output_port"])
Signal = namedtuple("Signal", ["time", "value"])

epsilon = 0.001

class Port:
    """
    Defines a port of a block.

    Args:
        name (str):                 The name of the port.
        direction (Port.Direction): The direction of the port; i.e., if it is
                                    an input or an output port.
        block (BaseBlock):          The block to which this port belongs.
    """
    Direction = enum(IN=0, OUT=1)
    """Possible port directions."""

    def __init__(self, name, direction, block):
        self.name = name
        self.direction = direction
        self.block = block
        self.__outgoing = []
        self.__incoming = None
        self.__history = []

    def __repr__(self):
        return "Port <%s> (%s)" % (self.name, repr(self.block))

    def set(self, value):
        """
        Sets the value of the port and transfers this to all outgoing connections.
        This will mainly update the current history.

        Args:
            value (float):  The new value of the port.
        """
        self.__history.append(value)
        for conn in self.__outgoing:
            conn.transfer()

    def get(self):
        """
        Obtains the current value of the port.
        """
        return self.__history[-1]

    def clear(self):
        """
        Clears all port signal history.
        """
        self.__history.clear()

    def reset(self):
        """Resets the port's connections."""
        self.clear()
        self.__outgoing = []
        self.__incoming = None

    def getOutgoing(self):
        """
        Obtains all outgoing connections from this port.
        """
        return self.__outgoing

    def getIncoming(self):
        """
        Obtains the incoming connection to this port.
        """
        return self.__incoming

    def getHistory(self):
        """
        Obtains all historic information about the signals of this port.
        """
        return self.__history

    def getPreviousPortClosure(self):
        """
        Find the previous port to which this port is connected that has no incoming connections.
        Hierarchical blocks and useless connections can/will be solved using this method.

        I.e., it obtains the port whose signal changes will eventually transfer to this port.
        """
        inc = self.getIncoming().source
        while inc.getIncoming() is not None:
            inc = inc.getIncoming().source
            if inc == self:
                raise ValueError("Loop Detected!")
        return inc

    def getNextPortClosure(self):
        """
        Find the next ports to which this port is connected that has no outgoing connections.
        Hierarchical blocks and useless connections can/will be solved using this method.

        I.e., it obtains the ports to whom this port transfers signals.
        """
        res = []
        loop_for = [self]
        visited = []
        while len(loop_for) > 0:
            elm = loop_for.pop(0)
            if elm in visited:
                raise ValueError("Loop Detected!")
            visited.append(elm)
            for out in elm.getOutgoing():
                port = out.target
                # End only in input ports
                if len(port.getOutgoing()) == 0:
                    res.append(port)
                else:
                    loop_for.append(port)
        return res

    def count(self):
        """
        Counts how often a signal was changed on this port.
        """
        return len(self.__history)

    def _rewind(self):
        """
        Rewinds the port to the previous iteration.
        """
        self.__history.pop()

    def getDependencies(self, _):
        if self.direction == Port.Direction.OUT:
            return [self.getPreviousPortClosure()]
        return []

    def getPath(self, sep):
        return self.block.getPath(sep) + sep + self.name

    @staticmethod
    def connect(source, target):
        """
        Connects two ports together.

        Args:
            source (Port):  The source port from which a connection starts.
            target (Port):  The target port where a connection ends.
        """
        conn = Connector(source, target)
        source.__outgoing.append(conn)
        assert target.__incoming is None, "Fan-IN is not allowed!"
        target.__incoming = conn

    @staticmethod
    def disconnect(source, target):
        """
        Disconnects two previously connected ports.

        Args:
            source (Port):  The source port from which a connection starts.
            target (Port):  The target port where a connection ends.
        """
        conn = target.__incoming
        assert conn.source == source
        source.__outgoing.remove(conn)
        target.__incoming = None


class Connector:
    """
    A connection that links two ports together.

    Args:
        source (Port):  The source port from which a connection starts.
        target (Port):  The target port where a connection ends.
    """
    def __init__(self, source, target):
        self.source = source
        self.target = target

    def __repr__(self):
        return "Connector <%s ==> %s>" % (repr(self.source), repr(self.target))

    def transfer(self):
        """
        Transfers the signal from the source port to the target port.
        """
        self.target.set(self.source.get())


class BaseBlock:
    """
    A base class for all types of basic blocks

    Args:
        name (str):             The name of the block. When empty, a :func:`pyCBD.util.hash64`
                                encoded name of the instance :func:`id` will be used, however
                                this is a bad practice and will result in a warning. When
                                using non-alphanumeric characters, a warning will also be shown.
        input_ports (iter):     List of input port names (strings).
        output_ports (iter):    List of output port names (strings).
    """
    def __init__(self, name, input_ports, output_ports):
        self.__block_name = hash64(id(self))
        if name != "":
            self.setBlockName(name)
        else:
            logger = logging.getLogger("CBD")
            logger.warning("No block name given, using hashed object id. This is a bad practice and should be avoided.",
                           extra={"block": self})
        if re.match(r"[^a-zA-Z0-9_]", self.__block_name):
            logger = logging.getLogger("CBD")
            logger.warning("Block names should only contain alphanumeric characters or underscores.", extra={"block": self})

        # The output signals produced by this block are encoded in a dictionary.
        # The key of this dictionary is the name of the output port.
        # Each element of the dictionary contains an ordered list of values.
        # self.__signals = dict()
        self.__outputs = {}
        for output_port in output_ports:
            self.addOutputPort(output_port)
            # self.__signals[output_port] = []


        # The input links produced by this block are encoded in a dictionary.
        # The key of this dictionary is the name of the input port.
        # Each element of the dictionary contains
        # a tuple of the block and the output name of the other block.
        # self._linksIn = dict()
        self.__inputs = {}
        for input_port in input_ports:
            self.addInputPort(input_port)

        # The list of possible input ports
        # self.__nameLinks = input_ports
        # In which CBD the BaseBlock is situated
        self._parent = None

    def addInputPort(self, name):
        """
        Adds an input port if there is no port with the given name.

        Args:
            name (str): The name of the port.
        """
        # if name not in self.__nameLinks:
        #     self.__nameLinks.append(name)
        if name not in self.__inputs:
            self.__inputs[name] = Port(name, Port.Direction.IN, self)

    def addOutputPort(self, name):
        """
        Adds an output port if there is no port with the given name.

        Args:
            name (str): The name of the port.
        """
        # if name not in self.__signals:
        #     self.__signals[name] = []
        if name not in self.__outputs:
            self.__outputs[name] = Port(name, Port.Direction.OUT, self)

    def removeInputPort(self, name):
        if name in self.__inputs:
            self.unlinkInput(name)
            del self.__inputs[name]

    def getInputPorts(self):
        return list(self.__inputs.values())

    def getInputPortNames(self):
        return list(self.__inputs.keys())

    def getInputPortByName(self, name):
        assert self.hasInputPortWithName(name), "No such input '%s' in %s" % (name, self.getPath())
        return self.__inputs[name]

    def hasInputPortWithName(self, name):
        return name in self.__inputs

    def getOutputPorts(self):
        return list(self.__outputs.values())

    def getOutputPortByName(self, name):
        assert self.hasOutputPortWithName(name), "No such output '%s' in %s" % (name, self.getPath())
        return self.__outputs[name]

    def getOutputPortNames(self):
        return list(self.__outputs.keys())

    def hasOutputPortWithName(self, name):
        return name in self.__outputs

    def reparentPorts(self):
        for port in self.getInputPorts() + self.getOutputPorts():
            port.block = self

    def clone(self):
        """
        (Deep) copies the current block, ignoring all connections or links
        that were set on this block.
        """
        other = deepcopy(self)
        other.reparentPorts()
        other.resetPorts()
        other._parent = None
        return other

    def getBlockName(self):
        """
        Gets the name of the block.
        """
        return self.__block_name

    def getFunctionName(self):
        """
        Obtains the block's function name, based on the block type.
        """
        nm = self.getBlockType().lower()
        if nm.endswith('block'):
            nm = nm[:-5]
        return nm

    def setBlockName(self, block_name):
        """
        Sets the name of the block.

        Args:
            block_name (str):   The name.
        """
        self.__block_name = block_name

    def setParent(self, parent):
        """
        Sets the block's parent.

        Args:
            parent (CBD):   The parent of the block.
        """
        self._parent = parent

    def getBlockType(self):
        """
        Gets the type of the block. This is the name of the class.
        """
        return self.__class__.__name__

    def getClock(self):
        """
        Gets the simulation clock. Only works if the block is part of a :class:`CBD` model.
        """
        return self._parent.getClock()

    def appendToSignal(self, value, name_output=None):
        """
        Appends the value to the set of obtained signals and links it to the current simulation
        time.

        Args:
            value (Any):        The value to append.
            name_output (str):  The name of the output port. If not set, or :code:`None`,
                                the value of :code:`OUT1` will be used.
        """
        name_output = "OUT1" if name_output is None else name_output
        port = self.getOutputPortByName(name_output)
        port.set(Signal(self.getClock().getTime(port.count()), value))

    def getSignalHistory(self, name_output=None):
        """
        Obtains the set of signals this block has sent over an output port.

        Args:
            name_output (str):  The name of the output port. If not set, or :code:`None`,
                                the value of :code:`OUT1` will be used.
        """
        name_output = "OUT1" if name_output is None else name_output
        return self.getOutputPortByName(name_output).getHistory()

    def clearPorts(self):
        """
        Clears all signal data from the ports.
        """
        for port in self.getInputPorts() + self.getOutputPorts():
            port.clear()

    def resetPorts(self):
        """
        Clears all signal data from the ports and resets all connections.
        """
        for port in self.getInputPorts() + self.getOutputPorts():
            port.reset()

    def getDependencies(self, curIteration):
        """
        Helper function to help the creation of the dependency graph.

        Args:
            curIteration (int): The current simulation's iteration, for which
                                the dependency graph must be constructed.

        Returns:
            A list of ports that must be computed in order to compute this block,
            at the time of the iteration.
        """
        # TODO: what with multiple sequential connectors
        return [p.getIncoming().source for p in self.getInputPorts() if p.getIncoming() is not None]

    def getPortConnectedToInput(self, input_port):
        """
        Get the block that is connected to a specific input.

        Args:
            input_port (str):   The name of the input port.
        """
        incoming = self.getInputPortByName(input_port).getIncoming()
        assert incoming is not None, "No block found that links to '%s' in '%s'." % (input_port, self.getPath())
        return incoming.source

    def getInputSignal(self, curIteration=-1, input_port="IN1"):
        """
        Returns the signal sent out by the input block.

        Args:
            curIteration (int):     The iteration at which the signal is obtained.
                                    When :code:`None` or :code:`-1`, the last value
                                    will be used.
            input_port (str):       The name of the input port. If omitted, or when
                                    :code:`None`, the value of :code:`IN1` will be used.
        """
        return self.getInputPortByName(input_port).getHistory()[curIteration]

    def getPath(self, sep='.', ignore_parent=False):
        """Gets the path of the current block.
        This includes the paths from its parents. When the block has no parents
        i.e. when it's the top-level block, the block's name is returned.

        Args:
            sep (str):              The separator to use. Defaults to :code:`.`
            ignore_parent (bool):   Whether or not to ignore the root block name.

        Returns:
            The full path as a string.

        Examples:

            A block called :code:`grandchild`, which is located in the :code:`child` CBD,
            that in its turn is located in this CBD has a path of :code:`child.grandchild`.
        """
        if self._parent is None:
            if ignore_parent:
                return ""
            return self.getBlockName()
        parpath = self._parent.getPath(sep, ignore_parent)
        if len(parpath) == 0:
            return self.getBlockName()
        return parpath + sep + self.getBlockName()

    def compute(self, curIteration):
        """
        Computes this block's operation, based on its inputs and store it as an output
        signal.

        Args:
            curIteration (int): The iteration at which we must compute this value.
        """
        raise NotImplementedError("BaseBlock has nothing to compute")

    def defaultInputPortNameIdentifier(self):
        """
        Algorithm that identifies which input port name to select if no input port name
        is provided for a link/connection.

        Be default, all ports with name :code:`INx` are analyzed, where :code:`x` identifies
        an integer of the auto-increment port.
        E.g. if the last connected port was :code:`IN1`, :code:`IN2` will be returned (if
        there is no incoming connection yet).

        Returns:
            The new input port.
        """
        i = 1
        while True:
            nextIn = "IN" + str(i)
            if self.hasInputPortWithName(nextIn):
                if self.getInputPortByName(nextIn).getIncoming() is None:
                    return nextIn
            else:
                raise ValueError("There are no open IN inputs left in block %s" % self.getPath())
            i += 1

    def linkToInput(self, in_block, *, name_input=None, name_output="OUT1"):
        """
        Links the output of the :code:`in_block` to the input of this block.

        Args:
            in_block (BaseBlock):   The block that must be linked before the current block.

        Keyword Args:
            name_input (str):       The name of the input port. When :code:`None` or omitted,
                                    :func:`defaultInputPortNameIdentifier` is used to find the
                                    next port name.
            name_output (str):      The name of the output port. Defaults to :code:`OUT1`.
        """
        if name_input is None:
            name_input = self.defaultInputPortNameIdentifier()
        if in_block.hasOutputPortWithName(name_output):
            source = in_block.getOutputPortByName(name_output)
        elif (self._parent == in_block or in_block == self) and in_block.hasInputPortWithName(name_output):
            # Connects input to input -- only in parent-child connection!
            source = in_block.getInputPortByName(name_output)
        else:
            raise ValueError("Could not connect ports!")
        if self.hasInputPortWithName(name_input):
            target = self.getInputPortByName(name_input)
        elif (self == in_block._parent or self == in_block) and self.hasOutputPortWithName(name_input):
            # Connects output to output -- only in parent-child connection!
            target = self.getOutputPortByName(name_input)
        else:
            raise ValueError("Could not connect ports %s and %s!" % (name_input, name_output))
        Port.connect(source, target)

    def unlinkInput(self, name_input):
        """
        Unlinks the input for this block.

        Args:
            name_input (str):   The name of the input.
        """
        target = self.getInputPortByName(name_input)
        if target.getIncoming() is not None:
            source = target.getIncoming().source
            Port.disconnect(source, target)

    def __repr__(self):
        return self.getPath() + ":" + self.getBlockType()

    def info(self, indent=0):
        """
        Returns a string with the block's details.

        Args:
            indent (int):   The amount of indentation that is required at the
                            start of each line. Defaults to 0.
        """
        idt = "\t" * indent
        repr = idt + self.getPath() + ":" + self.getBlockType() + "\n"
        if len(self.__inputs) == 0:
            repr += idt + "  No incoming connections to IN ports\n"
        else:
            for key, inport in self.__inputs:
                in_block = inport.getIncoming().block
                repr += "%s  Input %s connected from %s (%s)\n" % (idt, key, in_block.getPath(), in_block.getBlockType())
        return repr

    def _rewind(self):
        """
        Rewinds the CBD model to the previous iteration.

        Warning:
            Normally, this function should only be used by the internal mechanisms
            of the CBD simulator, **not** by a user. Using this function without a
            full understanding of the simulator may result in undefined behaviour.
        """
        for port in self.getInputPorts() + self.getOutputPorts():
            port._rewind()


class CBD(BaseBlock):
    """
    The CBD class, contains an entire Causal Block Diagram
    Call the run function to simulate the model.
    """
    def __init__(self, block_name, input_ports=None, output_ports=None):
        input_ports = input_ports if input_ports is not None else []
        output_ports = output_ports if output_ports is not None else []
        BaseBlock.__init__(self, block_name, input_ports, output_ports)
        # The blocks in the CBD will be stored both
        # -as an ordered list __blocks and
        # -as a dictionary __blocksDict with the blocknames as keys
        # for fast name-based retrieval and to ensure block names are unique within a single CBD
        self.__blocks = []
        self.__blocksDict = {}
        self.__clock = None

    def clone(self):
        # Clone all fields
        other: CBD = BaseBlock.clone(self)
        # other.setClock(deepcopy(self.getClock()))

        # Re-add all blocks to ensure deep cloning
        other.clearBlocks()
        for block in self.getBlocks():
            other.addBlock(block.clone())

        # Reconnect all blocks in the clone
        for block in self.getBlocks():
            for inp in block.getInputPorts():
                prev = inp.getIncoming().source
                if prev.block == self: continue
                other.addConnection(prev.block.getBlockName(), inp.block.getBlockName(), output_port_name=prev.name, input_port_name=inp.name)
        for inp in self.getInputPorts():
            for target in inp.getOutgoing():
                nxt = target.target
                if other.getBlockName() == nxt.block.getBlockName():
                    other.addConnection(inp.name, nxt.name)
                else:
                    other.addConnection(other, nxt.block.getBlockName(), output_port_name=inp.name, input_port_name=nxt.name)
        for out in self.getOutputPorts():
            prev = out.getIncoming().source
            if other.getBlockName() == prev.block.getBlockName(): continue
            other.addConnection(prev.block.getBlockName(), other, output_port_name=prev.name, input_port_name=out.name)
        return other

    def getTopCBD(self):
        """
        Finds the highest-level :class:`CBD` instance.
        """
        return self if self._parent is None else self._parent.getTopCBD()

    def flatten(self, ignore=None, psep="."):
        """
        Flatten the CBD inline and call recursively for all sub-CBDs.

        Args:
            ignore (iter):  Block class names to ignore in the flattening. When :code:`None`,
                            no blocks are ignored. Defaults to :code:`None`.
            psep (str):     The path separator to use. Defaults to :code:`"."`.

        .. versionchanged:: 1.5
            When an empty CBD block is encountered during flattening, this block will be removed from
            the resulting flattened model. Add it to the :attr:`ignore` iterable to prevent such a
            removal.
        """
        if ignore is None: ignore = []

        blocks = self.__blocks[:]
        for block in blocks:
            if isinstance(block, CBD) and not block.getBlockType() in ignore:
                block.flatten(ignore, psep)
                for child in block.getBlocks():
                    child.setBlockName(block.getBlockName() + psep + child.getBlockName())
                    self.addBlock(child)
                for port in block.getInputPorts() + block.getOutputPorts():
                    if port.getIncoming() is not None:
                        source = port.getIncoming().source
                        Port.disconnect(source, port)
                        outgoing = port.getOutgoing()[:]
                        for conn in outgoing:
                            target = conn.target
                            Port.disconnect(port, target)
                            self.addConnection(source.block, target.block, input_port_name=target.name,
                                               output_port_name=source.name)
                self.removeBlock(block)

    def flattened(self, ignore=None, psep="."):
        """
        Return a flattened version of the provided CBD.

        Args:
            ignore (iter):  Block class names to ignore in the flattening. When :code:`None`,
                            no blocks are ignored. Defaults to :code:`None`.
            psep (str):     The path separator to use. Defaults to :code:`"."`.
        """
        clone = self.clone()
        clone.flatten(ignore, psep)
        return clone

    def getBlocks(self):
        """
        Gets the list of blocks.
        """
        return self.__blocks

    def getBlockByName(self, name):
        """
        Gets a block by its name.

        Args:
            name (str): The block's name
        """
        return self.__blocksDict[name]

    def hasBlock(self, name):
        """
        Checks if the CBD has a block with the given name.

        Args:
            name (str): The name of the block to check.
        """
        return name in self.__blocksDict

    def clearBlocks(self):
        """
        Clears the block information. Calling this function will
        "empty" the current block.
        """
        self.__blocks.clear()
        self.__blocksDict.clear()

    def getClock(self):
        """
        Gets the current simulation clock.
        This will always be the block of the highest-level :class:`CBD`.
        """
        return self.__clock if self._parent is None else self._parent.getClock()

    def addFixedRateClock(self, prefix="clock", delta_t=1.0, start_time=0.0):
        """
        Adds a clock with a fixed rate.

        Two blocks are added to the simulation: a :class:`Clock` and a
        :class:`ConstantBlock` for the rate. Their names will be :code:`<prefix>-<what>`,
        where :code:`<what>` identifies the purpose of the block (which is one of
        :code:`clock` or :code:`delta`).

        Args:
            prefix (str):       The prefix for the names of the blocks.
                                Defaults to :code:`"clock"`.
            delta_t (float):    The interval when the clock must tick.
                                Defaults to 1.
            start_time (float): The time at which the simulation starts.
                                Defaults to 0.

        Note:
            Whenever this function is not called, upon simulation start a clock
            is added with the default values.

        Warning:
            **Clock Usage Assumption:** When adding a (custom) clock to your model(s),
            its outputs will always represent the (relative) simulated time and time-delta,
            independent of the simulation algorithm used. I.e., changing the delay of a
            fixed-rate clock should only influence the accuracy of the signals, **not**
            the correctness of the signals. It is forbidden to misuse these outputs for
            specific simulations (e.g., using the :code:`time` as a counter, using
            :code:`delta` as a constant value...).

            In other words, the clock is guaranteed to output a correct value and should
            only be used in the context of "time". When exporting the CBD model to other
            formalisms/simulators, the Clock's outputs should be replaced with the
            corresponding simulator's clock without loss of generality.
        """
        self.addBlock(Clock("%s-clock" % prefix, delta_t, start_time))
        self.addBlock(ConstantBlock("%s-delta" % prefix, delta_t))
        self.addConnection("%s-delta" % prefix, "%s-clock" % prefix, input_port_name='h')

    def addBlock(self, block):
        """
        Add a block to the CBD model

        Args:
            block (BaseBlock):  The block to add.

        Returns:
            The block that was passed as an argument.
        """
        assert isinstance(block, BaseBlock), "Can only add BaseBlock (subclass) instances to a CBD"
        block.setParent(self)

        if block.getBlockName() not in self.__blocksDict and \
                block.getBlockName() not in self.getOutputPortNames() + self.getInputPortNames():
            self.__blocks.append(block)
            self.__blocksDict[block.getBlockName()] = block
            if isinstance(block, Clock):
                self.__clock = block
        else:
            logger = logging.getLogger("CBD")
            logger.warning("Did not add this block as it has the same name '%s' as an already existing block/port." % block.getBlockName(), extra={ "block":self})

        return block

    def removeBlock(self, block):
        """
        Removes a block from the :class:`CBD`.

        Args:
            block (BaseBlock):  The block to remove.
        """
        assert isinstance(block, BaseBlock), "Can only delete BaseBlock (subclass) instances to a CBD"

        if block.getBlockName() in self.__blocksDict:
            self.__blocks.remove(self.__blocksDict[block.getBlockName()])
            del self.__blocksDict[block.getBlockName()]
        else:
            exit("Warning: did not remove this block %s as it was not found" % block.getBlockName())

    def addConnection(self, from_block, to_block, *, input_port_name=None, output_port_name="OUT1"):
        """
        Adds a connection between :code:`from_block` with :code:`input_port_name` to
        :code:`to_block` with :code:`outport_port_name`.

        Args:
            from_block (str):       The block to start the connection from.
            to_block (str):         The target block of the connection.

        Keyword Args:
            input_port_name (str):  The name of the input port. When :code:`None` or unset,
                                    :func:`defaultInputPortNameIdentifier` will be used to
                                    identify the port name.
            output_port_name (str): The name of the output port. Defaults to :code:`OUT1`.

        Note:
            Connecting from and to ports is possible by setting the :attr:`from_block` and/or
            :attr:`to_block` arguments to the port names.

        See Also:
            :func:`BaseBlock.linkToInput`
        """
        if isinstance(from_block, str):
            if self.hasInputPortWithName(from_block):
                output_port_name = from_block
                from_block = self
            else:
                from_block = self.getBlockByName(from_block)
        if isinstance(to_block, str):
            if self.hasOutputPortWithName(to_block):
                input_port_name = to_block
                to_block = self
            else:
                to_block = self.getBlockByName(to_block)
        to_block.linkToInput(from_block, name_input=input_port_name, name_output=output_port_name)

    def getDependencies(self, curIteration):
        deps = []
        for block in self.getBlocks():
            deps += [x for x in block.getDependencies(curIteration) if x.block == self]
        return deps

    def removeConnection(self, block, input_port_name):
        """
        Removes an input connection of block :code:`block` and port :code:`input_port_name`.

        Args:
            block (BaseBlock):      A block to remove an input connection for.
            input_port_name (str):  The (input) port name.
        """
        if isinstance(block, str):
            block = self.getBlockByName(block)
        block.unlinkInput(input_port_name)

    def find(self, path, sep='.'):
        """Obtain a block/port in a submodel of this CBD.

        Args:
            path (str): The path of the block to find. Empty string for the current block,
                        :code:`child.grandchild` for the block called code:`grandchild`,
                        which is located in the :code:`child` CBD that is located in this CBD.
            sep (str):  The path separator to use. Defaults to :code:`.`

        Returns:
            The block that corresponds to the given path and the path to the block itself.

            .. note::   The block/port that will be returned has a different path than the path provided
                        in this function call. This is because this function assumes you already have
                        a path to the CBD you call it on. For instance, if this CBD contains a child
                        called :code:`child`, which has a :code:`grandchild` block in its turn, calling
                        find on the :class:`child` to locate the :code:`grandchild` only needs
                        :code:`grandchild` to be passed as a path. If the function is called on the
                        current CBD block instead, :code:`child.grandchild` is required to obtain the
                        same block.
        """
        if path == '':
            return self, self.getPath()
        cur = self
        for p in path.split(sep):
            if p in cur.__blocksDict:
                cur = cur.getBlockByName(p)
            elif p in cur.getInputPortNames():
                cur = cur.getInputPortByName(p)
                path = cur.block.getPath()
            elif p in cur.getOutputPortNames():
                cur = cur.getOutputPortByName(p)
                path = cur.block.getPath()
            else:
                raise ValueError("Cannot find block '{}' in '{}'.".format(p, cur.getPath()))
        return cur, path

    def __repr__(self):
        return "CBD <%s>" % self.getBlockName()

    def info(self, indent=0):
        """
        Obtains the model structure recursively.

        Args:
            indent (int):   The level of indents to start at.
        """
        det = ("\t" * indent) + BaseBlock.info(self, indent) + "\n"
        for block in self.getBlocks():
            det += block.info(indent + 1)
        return det

    def dump(self):
        """
        Dumps the model information to the console.
        """
        print("=========== Start of Model Dump ===========")
        print(self)
        print(self.info())
        print("=========== End of Model Dump =============\n")

    def dumpSignals(self):
        """
        Dumps the signal information to the console.
        """
        print("=========== Start of Signals Dump ===========")
        for block in self.getBlocks():
            print("%s:%s" % (block.getBlockName(), block.getBlockType()))
            print(str(block.getSignalHistory()) + "\n")
        print("=========== End of Signals Dump =============\n")

    def getSignalHistory(self, name_output=None):
        name_output = "OUT1" if name_output is None else name_output
        port = self.getOutputPortByName(name_output)
        return port.getHistory()

    def getSignals(self):
        """
        Obtains all signal histories.
        """
        res = {}
        for port in self.getOutputPortNames():
            res[port] = self.getSignalHistory(port)
        return res

    def clearSignals(self):
        """
        Clears the output signals of all blocks and ports.
        """
        for block in self.getBlocks():
            if isinstance(block, CBD):
                block.clearSignals()
            block.clearPorts()
        self.clearPorts()

    def getAllSignalNames(self, sep="."):
        res = []
        for block in self.getBlocks():
            if isinstance(block, CBD):
                res.extend(block.getAllSignalNames(sep))
            for out in block.getOutputPorts():
                path = block.getPath(sep, True)
                if len(path) == 0:
                    path = out.name
                else:
                    path += sep + out.name
                res.append(path)
        for out in self.getOutputPorts():
            path = self.getPath(sep, True)
            if len(path) == 0:
                path = out.name
            else:
                path += sep + out.name
            res.append(path)
        return res

    def compute(self, curIteration):
        pass

    def _rewind(self):
        super()._rewind()
        for block in self.getBlocks():
            block._rewind()

    def getUniqueBlockName(self, prefix="", hash=False):
        """
        Fetches a name that is unique within the given model.
        This name is in the form :code:`<prefix><suffix>`. The suffix is the
        string representation of a unique identifier. This identifier is
        continuously increased and tested.

        Args:
            prefix (str):   The prefix of the name to fetch. When a valid
                            name by itself, this will be returned, ignoring
                            any suffix. Defaults to the empty string.
            hash (bool):    When :code:`True`, the current object id will be
                            used as a starting point for the identifier.
                            Additionally, the :func:`pyCBD.util.hash64` function
                            will be used for the suffix representation. When
                            :code:`False`, the identifier will start at 1 and
                            no hashing will be done. Defaults to :code:`False`.
        """
        names = set([x.getBlockName() for x in self.getBlocks()] + self.getInputPortNames() + self.getOutputPortNames())
        uid = 1
        if hash:
            uid = id(self)
        name = prefix
        while name in names:
            suffix = str(uid)
            if hash:
                suffix = hash64(uid)
            name = prefix + suffix
            uid += 1
        return name


from pyCBD.lib.std import Clock, ConstantBlock
