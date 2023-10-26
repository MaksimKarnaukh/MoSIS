#
# scanner.py
#
# Based on code for COMP 304B Assignment 3
# Updated to Python 3 in 2021
# Adapted by Sam and Maksim

# trace FSA dynamics (True | False)
__trace__ = False
# __trace__ = True

class CharacterStream:
    """
    A stream of characters helper class.
    """
    def __init__(self, string):
        self.string = string
        self.last_ptr = -1
        self.cur_ptr = -1

    def __repr__(self):
        return self.string

    def __str__(self):
        return self.string

    def peek(self):
        if self.cur_ptr+1 < len(self.string):
            return self.string[self.cur_ptr+1]
        return None

    def consume(self):
        self.cur_ptr += 1

    def commit(self):
        self.last_ptr = self.cur_ptr

    def rollback(self):
        self.cur_ptr = self.last_ptr


class StringStream:
    """
    A stream of strings helper class
    """
    def __init__(self, string):
        self.strings = self.setstrings(string)
        self.last_ptr = -1
        self.cur_ptr = -1

    def setstrings(self, string):
        return string.split("\n")

    def __repr__(self):
        return "\n".join(self.strings)

    def __str__(self):
        return "\n".join(self.strings)

    def peek(self):
        if self.cur_ptr+1 < len(self.strings):
            return self.strings[self.cur_ptr+1]
        return None

    def consume(self):
        self.cur_ptr += 1

    def commit(self):
        self.last_ptr = self.cur_ptr

    def rollback(self):
        self.cur_ptr = self.last_ptr


class Scanner:
    """
    A simple Finite State Automaton simulator.
    Used for scanning an input stream.
    """
    def __init__(self, stream):
        self.set_stream(stream)
        self.current_state=None
        self.accepting_states=[]

    def set_stream(self, stream):
        self.stream = stream

    def scan(self):
        self.current_state = self.transition(self.current_state, None)

        if __trace__:
            print("\ndefault transition --> " + self.current_state)

        while True:
            # look ahead at the next character in the input stream
            next_char = self.stream.peek()

            # stop if this is the end of the input stream
            if next_char is None: break

            if __trace__:
                if self.current_state is not None:
                    print("transition", self.current_state, "-|", next_char, end=' ')

            # perform transition and its action to the appropriate new state
            next_state = self.transition(self.current_state, next_char)

            if __trace__:
                if next_state is None:
                    print("")
                else:
                    print("|->", next_state)


            # stop if a transition was not possible
            if next_state is None:
                break
            else:
                self.current_state = next_state
                # perform the new state's entry action (if any)
                self.entry(self.current_state, next_char)

            # now, actually consume the next character in the input stream
            next_char = self.stream.consume()

        if __trace__:
            print("")

        # now check whether to accept consumed characters
        success = self.current_state in self.accepting_states
        if success:
            self.stream.commit()
        else:
            self.stream.rollback()
        return success

## An example scanner, see http://msdl.cs.mcgill.ca/people/hv/teaching/SoftwareDesign/COMP304B2003/assignments/assignment3/solution/
class NumberScanner(Scanner):
    def __init__(self, stream):
        # superclass constructor
        super().__init__(stream)

        self.value = 0
        self.exp = 0
        self.scale = 1

        # define accepting states
        self.accepting_states=["S2","S4","S7"]

    def __str__(self):
        return str(self.value) + "E" + str(self.exp)

    def transition(self, state, input):
        """
        Encodes transitions and actions
        """
        if state is None:
            # action
            # initialize variables
            self.value = 0
            self.exp = 0
            # new state
            return "S1"

        elif state == "S1":
            if input  == '.':
                # action
                self.scale = 0.1
                # new state
                return "S3"
            elif '0' <= input <= '9':
                # action
                self.value = ord(input.lower()) - ord('0')
                # new state
                return "S2"
            else:
                return None

        elif state == "S2":
            if input  == '.':
                # action
                self.scale = 0.1
                # new state
                return "S4"
            elif '0' <= input <= '9':
                # action
                self.value = self.value * 10 + ord(input.lower()) - ord('0')
                # new state
                return "S2"
            elif input.lower()  == 'e':
                # action
                self.exp = 1
                # new state
                return "S5"
            else:
                return None

        elif state == "S3":
            if '0' <= input <= '9':
                # action
                self.value += self.scale * (ord(input.lower()) - ord('0'))
                self.scale /= 10
                # new state
                return "S4"
            else:
                return None

        elif state == "S4":
            if '0' <= input <= '9':
                # action
                self.value += self.scale * (ord(input.lower()) - ord('0'))
                self.scale /= 10
                # new state
                return "S4"
            elif input.lower()  == 'e':
                # action
                self.exp = 1
                # new state
                return "S5"
            else:
                return None

        elif state == "S5":
            if input == '+':
                # new state
                return "S6"
            elif input  == '-':
                # action
                self.exp = -1
                # new state
                return "S6"
            elif '0' <= input <= '9':
                # action
                self.exp *= ord(input.lower()) - ord('0')
                # new state
                return "S7"
            else:
                return None

        elif state == "S6":
            if '0' <= input <= '9':
                # action
                self.exp *= ord(input.lower()) - ord('0')
                # new state
                return "S7"
            else:
                return None

        elif state == "S7":
            if '0' <= input <= '9':
                # action
                self.exp = self.exp * 10 + ord(input.lower()) - ord('0')
                # new state
                return "S7"
            else:
                return None

        else:
            return None

    def entry(self, state, input):
        pass


# read file and put in one big string change trace file here
def readFile(fileName):
    strings = []
    with open(fileName, "r") as f:
        strings.append(f.read())
    return '\n'.join(strings)


class Requirement6_RE1_Scanner(Scanner):
    def __init__(self, stream):
        # superclass constructor
        super().__init__(stream)

        self.id = 0

        # define accepting states
        self.accepting_states=["S5"]

    def __str__(self):
        return str(self.id)

    def transition(self, state, input):
        """
        Encodes transitions and actions
        """
        if state is None:
            # action
            # initialize variables
            self.id = 0
            # new state
            return "S1"

        elif state == "S1":

            if input[0:6] == 'DS ON ':
                self.id = int(input[6:])
                return "S2"
            else:
                return "S1"

        elif state == "S2":
            if input[0:6] == 'DS OFF':
                id = int(input[7:])
                if id == self.id:
                    return "S3"
                self.id = id
                return "S2"
            elif input[0:6] == 'PS OFF':
                id = int(input[7:])
                if id == self.id:
                    return "S5"
                return "S2"
            elif input[0:6] == 'PS ON ':
                id = int(input[6:])
                if id == self.id:
                    self.id = id
                    return "S5"
                return "S2"
            else:
                return "S2"

        elif state == "S3":
            if input[0:6] == 'PS ON ':
                id = int(input[6:])
                if id == self.id:
                    return "S4"
                return "S3"
            elif input[0:6] == 'PS OFF':
                id = int(input[7:])
                if id == self.id:
                    return "S5"
                return "S3"
            else:
                return "S3"

        elif state == "S4":

            if input[0:6] == 'PS OFF':
                id = int(input[7:])
                if id == self.id:
                    return "S1"
                return "S4"
            else:
                return "S4"

        elif state == "S5":
            return "S5"

        else:
            return None

    def entry(self, state, input):
        pass


class Requirement6_RE2_Scanner(Scanner):
    def __init__(self, stream):
        # superclass constructor
        super().__init__(stream)

        self.id = 0

        # define accepting states
        self.accepting_states=["S3"]

    def __str__(self):
        return str(self.id)

    def transition(self, state, input):
        """
        Encodes transitions and actions
        """
        if state is None:
            # action
            # initialize variables
            self.id = 0
            # new state
            return "S1"

        elif state == "S1":
            # if input starts with PS ON, get the number x in string 'PS ON x'
            if input[0:6] == 'PS ON ':
                self.id = int(input[6:])
                return "S2"
            else:
                return "S1"

        elif state == "S2":
            if input[0:6] == 'PS OFF':
                id = int(input[7:])
                return "S1"
            elif input[0:6] == 'PS ON ':
                id = int(input[6:])
                if id != self.id:
                    self.id = id
                    return "S3"
                return "S2"
            else:
                return "S2"

        elif state == "S3":
            return "S3"

        else:
            return None

    def entry(self, state, input):
        pass

class Requirement5_RE1_Scanner(Scanner):
    def __init__(self, stream):
        # superclass constructor
        super().__init__(stream)

        self.id = 0

        # define accepting states
        self.accepting_states=["S8"]

    def __str__(self):
        return str(self.id)

    def transition(self, state, input):
        """
        Encodes transitions and actions
        """
        if state is None:
            # action
            # initialize variables
            self.id = 0
            # new state
            return "S1"

        elif state == "S1":
            if input[0:6] == 'FS ON':
                return "S2"
            else:
                return "S1"

        elif state == "S2":
            if input[0:6] == 'QS ON':
                return "S3"
            else: return "S2"

        elif state == "S3":
            if input[0:6] == 'DS ON ':
                self.id = int(input[6:])
                return "S4"
            elif input == 'QS OFF':
                return "S2"
            else:
                return "S3"

        elif state == "S4":

            if input == 'TL GREEN':
                return "S5"
            else:
                return "S4"
        elif state == "S5":
            if input == 'TL RED':
                return "S8"
            elif input[0:6] == 'DS OFF':
                id = int(input[7:])
                if id == self.id:
                    return "S3"
                self.id = id
                return "S6"
            else:
                return "S5"
        elif state == "S6":
            if input == 'TL RED':
                return "S3"
            else:
                return "S6"
        elif state == "S8":
            return "S8"


        else:
            return None

    def entry(self, state, input):
        pass

class Requirement5_RE3_Scanner(Scanner):
    def __init__(self, stream):
        # superclass constructor
        super().__init__(stream)

        self.id = 0

        # define accepting states
        self.accepting_states=["S8"]

    def __str__(self):
        return str(self.id)

    def transition(self, state, input):
        """
        Encodes transitions and actions
        """
        if state is None:
            # action
            # initialize variables
            self.id = 0
            # new state
            return "S8"

        elif state == "S1":

            if input == 'FS ON ':
                return "S2"
            else:
                return "S1"

        elif state == "S2":
            if input == 'FS OFF':
                return "S1"
            elif input[0:6] == 'QS ON':
                return "S3"
            else:
                return "S2"

        elif state == "S3":
            if input == 'QS OFF':
                return "S2"
            elif input == 'TL GREEN':
                return "S4"
            else:
                return "S3"

        elif state == "S4":
            if input[0:6] == 'DS OFF':
                self.id = int(input[7:])
                return "S5"
            else:
                return "S4"

        elif state == "S5":
            if input[0:6] == 'DS ON ' or input[0:6]=='DS OFF':
                id = int(input[6:])
                self.id = id
                return "S6"
            return "S5"
        elif state == "S6":
            if input == 'TL RED':
                return "S8"
            elif input[0:6] == 'DS ON ' or input[0:6]=='DS OFF':
                return "S7"

        else:
            return None

    def entry(self, state, input):
        pass


class Requirement5_RE2_Scanner(Scanner):
    def __init__(self, stream):
        # superclass constructor
        super().__init__(stream)

        self.id = 0

        # define accepting states
        self.accepting_states=["S8"]

    def __str__(self):
        return str(self.id)

    def transition(self, state, input):
        """
        Encodes transitions and actions
        """
        if state is None:
            # action
            # initialize variables
            self.id = 0
            # new state
            return "S1"

        elif state == "S1":

            if input == 'FS ON':
                return "S2"
            else:
                return "S1"

        elif state == "S2":
            if input == 'QS ON':
                return "S3"
            else:
                return "S2"

        elif state == "S3":
            if input == 'QS OFF':
                return "S2"
            elif input == 'TL GREEN':
                return "S4"
            else:
                return "S3"

        elif state == "S4":
            if input[0:6] == 'DS OFF':
                self.id = int(input[7:])
                return "S5"
            else:
                return "S4"

        elif state == "S5":
            if input[0:6] == 'DS OFF':
                self.id = int(input[7:])
                return "S6"
            else:
                return "S5"

        elif state == "S6":
            if input[0:6] == 'DS OFF':
                self.id = int(input[7:])
                return "S7"
            else:
                return "S6"

        elif state == "S7":
            if input == 'TL RED':
                return "S3"
            else:
                return "S7"

        elif state == "S7":
            if input == 'TL RED':
                return "S3"
        elif state == "S8":
            return "S8"
        else:
            return None

    def entry(self, state, input):
        pass


def runThroughAllFSAs(FSM_inputs: list):
    """
    Runs through all the FSMs and prints out the results
    """
    for i, FSM_input in enumerate(FSM_inputs):

        print(f"Running trace {i+1} through Requirement6_RE1_Scanner")
        stream = StringStream(FSM_input)
        scanner = Requirement6_RE1_Scanner(stream)
        success = scanner.scan()
        if success:
            print("Stream not accepted, violation against requirement 6. ID: %s" % (str(scanner.id)))
        else:
            print("Stream has been accepted. Correct")

        print(f"Running trace {i+1} through Requirement6_RE2_Scanner")
        stream = StringStream(FSM_input)
        scanner = Requirement6_RE2_Scanner(stream)
        success = scanner.scan()
        if success:
            print("Stream not accepted, violation against requirement 6. ID: %s" % (str(scanner.id)))
        else:
            print("Stream has been accepted. Correct")
        print("-")

        print(f"Running trace {i + 1} through Requirement5_RE1_Scanner")
        stream = StringStream(FSM_input)
        scanner = Requirement5_RE1_Scanner(stream)
        success = scanner.scan()
        if success:
            print("Stream not accepted, violation against requirement 5. ID: %s" % (str(scanner.id)))
        else:
            print("Stream has been accepted. Correct")

        print(f"Running trace {i + 1} through Requirement5_RE2_Scanner")
        stream = StringStream(FSM_input)
        scanner = Requirement5_RE2_Scanner(stream)
        success = scanner.scan()
        if success:
            print("Stream not accepted, violation against requirement 5. ID: %s" % (str(scanner.id)))
        else:
            print("Stream has been accepted. Correct")

        print(f"Running trace {i + 1} through Requirement5_RE3_Scanner")
        stream = StringStream(FSM_input)
        scanner = Requirement5_RE3_Scanner(stream)
        success = scanner.scan()
        if success:
            print("Stream not accepted, violation against requirement 5. ID: %s" % (str(scanner.id)))
        else:
            print("Stream has been accepted. Correct")
        print("----------------------------------------------------------------------------------------")


if __name__ == "__main__":

    # run test

    traces_file_path = "../output_traces/"

    trace1 = readFile(traces_file_path + "trace1.txt")
    trace2 = readFile(traces_file_path + "trace2.txt")
    trace3 = readFile(traces_file_path + "trace3.txt")
    trace4 = readFile(traces_file_path + "trace4.txt")
    trace5 = readFile(traces_file_path + "trace5.txt")
    trace6 = readFile(traces_file_path + "trace6.txt")
    traces = [trace1, trace2, trace3, trace4, trace5, trace6]

    runThroughAllFSAs(traces)

