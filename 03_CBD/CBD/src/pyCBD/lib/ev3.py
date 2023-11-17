"""Set of simple Blocks to use in combination with LEGO Mindstorms EV3.

Requires Pybricks to be installed. See also the documentation at
	https://pybricks.com/ev3-micropython

Warning:
	Brick sounds are not permitted, as they delay the simulation. It is
	also unclear if multithreading is possible to allow for this.

Note:
	Because drawing features are quite complicated and use-case specific,
	no block for drawing to the screen is included. If required, this needs
	to be created.

Note:
	It does not make sense to use these blocks in combination with precise state events, as the
	event has already happened and rewinding is not useful.
"""
from pyCBD.Core import BaseBlock
from pybricks.ev3devices import TouchSensor, ColorSensor, InfraredSensor, GyroSensor, UltrasonicSensor
from pybricks._common import Motor, Control
from pybricks.robotics import DriveBase
from pybricks.parameters import Port, Direction
from pybricks.hubs import EV3Brick

_Brick = EV3Brick()

_PI = 3.14159265359
def _rad2deg(radians):
	return radians * 180 / _PI


#################
#     BRICK     #
#################

class BrickLightBlock(BaseBlock):
	"""
	Block to change the light of the EV3 Brick.

	Arguments:
		block_name (str):       The name of the block.

	:Input Ports:
		**IN1** -- The value of the light. Must be a Color or :code:`None` to turn off.
	"""
	def __init__(self, block_name):
		super().__init__(block_name, input_ports=["IN1"], output_ports=[])

	def compute(self, curIteration):
		color = self.getInputSignal(curIteration, "IN1").value
		_Brick.light.on(color)


class BatteryVoltageBlock(BaseBlock):
	"""
	Block that outputs the current EV3 Brick's voltage.

	Arguments:
		block_name (str):   The name of the block.
		starting (numeric): The starting voltage of the Brick. When :code:`None`,
							the Voltage is outputted in an absolute value. Otherwise,
							a percentage is used. When set, must be larger than 0.

	:Output Ports:
		**OUT1** -- The voltage of the EV3 Brick. Can be absolute or relative (percentage).
	"""
	def __init__(self, block_name, starting=None):
		assert starting is None or starting > 0
		super().__init__(block_name, input_ports=[], output_ports=["OUT1"])
		self.starting = starting

	def compute(self, curIteration):
		voltage = float(_Brick.battery.voltage()) / 1000.0
		if self.starting is None:
			self.appendToSignal(voltage, "OUT1")
		else:
			self.appendToSignal(voltage / self.starting, "OUT1")


#################
#    SENSORS    #
#################
class TouchSensorBlock(BaseBlock):
	"""
	Block to check if a touch sensor is pressed.

	Arguments:
		block_name (str):   The name of the block.
		port_name (str):    The name of the sensor port. This is a number
							between 1 and 4.

	:Output Ports:
		**OUT1** -- Boolean value indicating if the button is pressed (:code:`True`)
					or not (:code:`False`).
	"""
	def __init__(self, block_name, port_name):
		super().__init__(block_name, input_ports=[], output_ports=["OUT1"])
		self.port = getattr(Port, "S{}".format(port_name))
		self.sensor = TouchSensor(self.port)

	def compute(self, curIteration):
		value = self.sensor.pressed()
		self.appendToSignal(value, "OUT1")


class ColorSensorBlock(BaseBlock):
	"""
	Block to compute the color reflection of a surface.

	Arguments:
		block_name (str):   The name of the block.
		port_name (str):    The name of the sensor port. This is a number
							between 1 and 4.

	:Output Ports:
		- **OUT1** -- The amount of red reflected light.
		- **OUT2** -- The amount of green reflected light.
		- **OUT3** -- The amount of blue reflected light.

	Note:
		Can cause inconsistent and invalid results when the :class:`AmbientLightSensorBlock`
		is also used on the same port.
	"""
	def __init__(self, block_name, port_name):
		super().__init__(block_name, input_ports=[], output_ports=["OUT1", "OUT2", "OUT3"])
		self.port = getattr(Port, "S{}".format(port_name))
		self.sensor = ColorSensor(self.port)

	def compute(self, curIteration):
		r, g, b = self.sensor.rgb()
		self.appendToSignal(r, "OUT1")
		self.appendToSignal(g, "OUT2")
		self.appendToSignal(b, "OUT3")


class AmbientLightSensorBlock(BaseBlock):
	"""
	Block to compute the amount of ambient light.

	Arguments:
		block_name (str):   The name of the block.
		port_name (str):    The name of the sensor port. This is a number
							between 1 and 4.

	:Output Ports:
		**OUT1** -- The amount of ambient light.

	Note:
		Can cause inconsistent and invalid results when the :class:`ColorSensorBlock`
		is also used on the same port.
	"""
	def __init__(self, block_name, port_name):
		super().__init__(block_name, input_ports=[], output_ports=["OUT1"])
		self.port = getattr(Port, "S{}".format(port_name))
		self.sensor = ColorSensor(self.port)

	def compute(self, curIteration):
		ambient = self.sensor.ambient()
		self.appendToSignal(ambient, "OUT1")


class InfraredDistanceSensorBlock(BaseBlock):
	"""
	Block to compute the distance to an object, using an infrared sensor.

	Arguments:
		block_name (str):   The name of the block.
		port_name (str):    The name of the sensor port. This is a number
							between 1 and 4.

	:Output Ports:
		**OUT1** -- The distance to an object.
	"""
	def __init__(self, block_name, port_name):
		super().__init__(block_name, input_ports=[], output_ports=["OUT1"])
		self.port = getattr(Port, "S{}".format(port_name))
		self.sensor = InfraredSensor(self.port)

	def compute(self, curIteration):
		value = self.sensor.distance()
		self.appendToSignal(value, "OUT1")


class InfraredButtonSensorBlock(BaseBlock):
	"""
	Block to compute the input of a remote.

	Arguments:
		block_name (str):   The name of the block.
		port_name (str):    The name of the sensor port. This is a number
							between 1 and 4.
		channel (int):      The channel on the remote.

	:Output Ports:
		**OUT1** -- The button list. Should not be used for mathematical computations.
	"""
	def __init__(self, block_name, port_name, channel):
		super().__init__(block_name, input_ports=[], output_ports=["OUT1"])
		self.port = getattr(Port, "S{}".format(port_name))
		self.sensor = InfraredSensor(self.port)
		self.channel = channel

	def compute(self, curIteration):
		value = self.sensor.buttons(self.channel)
		self.appendToSignal(value, "OUT1")


class UltrasonicSensorBlock(BaseBlock):
	"""
	Block to compute the distance to an object, using an ultrasonic sensor.

	Arguments:
		block_name (str):   The name of the block.
		port_name (str):    The name of the sensor port. This is a number
							between 1 and 4.

	:Output Ports:
		**OUT1** -- The distance to an object.

	Note:
		The sensor does not turn off after measuring a distance. Because of
		a presumed high-rate CBD simulation, continuously turning it off is
		bad for performance and may cause the sensor to freeze.

		This results in the sensor causing more inference with other ultrasonic
		sensors.
	"""
	def __init__(self, block_name, port_name):
		super().__init__(block_name, input_ports=[], output_ports=["OUT1"])
		self.port = getattr(Port, "S{}".format(port_name))
		self.sensor = UltrasonicSensor(self.port)

	def compute(self, curIteration):
		value = self.sensor.distance(silent=False)
		self.appendToSignal(value, "OUT1")


class GyroscopicSpeedSensorBlock(BaseBlock):
	"""
	Block to compute the rotational velocity, using a gyroscopic sensor.

	Arguments:
		block_name (str):       The name of the block.
		port_name (str):        The name of the sensor port. This is a number
								between 1 and 4.
		direction (Direction):  Whether the sensor should be rotating
								clockwise or counter-clockwise. Defaults to
								:code:`CLOCKWISE`.

	:Output Ports:
		**OUT1** -- The rotational velocity in deg/s.
	"""
	def __init__(self, block_name, port_name, direction=Direction.CLOCKWISE):
		super().__init__(block_name, input_ports=[], output_ports=["OUT1"])
		self.port = getattr(Port, "S{}".format(port_name))
		self.sensor = GyroSensor(self.port, direction)

	def compute(self, curIteration):
		value = self.sensor.speed()
		self.appendToSignal(value, "OUT1")


class GyroscopicAngleSensorBlock(BaseBlock):
	"""
	Block to compute an angle, using a gyroscopic sensor.

	Arguments:
		block_name (str):       The name of the block.
		port_name (str):        The name of the sensor port. This is a number
								between 1 and 4.
		direction (Direction):  Whether the positive rotation should be
								clockwise or counter-clockwise. Defaults to
								:code:`CLOCKWISE`.
		resettable (bool):      When :code:`True`, an input is added on which the
								angle can be changed. Defaults to :code:`False`.

	:Input Ports:
		**IN1** -- New value for the angle in deg. Optional port if the angle can be reset.

	:Output Ports:
		**OUT1** -- The angle in deg.
	"""
	def __init__(self, block_name, port_name, direction=Direction.CLOCKWISE, resettable=False):
		super().__init__(block_name, input_ports=[], output_ports=["OUT1"])
		self.port = getattr(Port, "S{}".format(port_name))
		self.sensor = GyroSensor(self.port, direction)
		self.resettable = resettable
		if self.resettable:
			self.addInputPort("IN1")

	def compute(self, curIteration):
		if self.resettable:
			self.sensor.reset_angle(self.getInputSignal(curIteration, "IN1"))
		value = self.sensor.angle()
		self.appendToSignal(value, "OUT1")


#################
#    MOTORS     #
#################

class MotorBlock(BaseBlock):
	"""
	Block that drives a single Motor.

	Arguments:
		block_name (str):       The name of the block.
		port_name (str):        The name of the actuator port. This is a letter
								between A and D.
		direction (Direction):  Whether the positive rotation should be
								clockwise or counter-clockwise. Defaults to
								:code:`CLOCKWISE`.
		gears (list):           Additional list of gears that are linked to the
								motor, to allow for better control. Defaults to
								:code:`None` (i.e., the empty list).
		control (Control):      The Motors themselves use a PID controller. To fully
								manipulate their behaviour, use the :class:`Control` class.

	:Input Ports:
		**IN1** -- The motor velocity in deg/s. Use 0 to brake the rotation.
	"""
	def __init__(self, block_name, port_name, direction=Direction.CLOCKWISE, gears=None, control=None):
		super().__init__(block_name, input_ports=["IN1"], output_ports=[])
		self.port = getattr(Port, port_name)
		self.motor = Motor(self.port, direction, gears)
		if control is not None:
			self.motor.control = control

	def compute(self, curIteration):
		phi = self.getInputSignal(curIteration, "IN1").value
		if abs(phi) <= 1e-6:
			self.motor.hold()
		else:
			self.motor.run(phi)

	def __del__(self):
		# Ensures that the motor actually stops
		self.motor.stop()


class MotorSpeedSensorBlock(BaseBlock):
	"""
	Block to compute the rotational velocity of a motor.

	Arguments:
		block_name (str):       The name of the block.
		port_name (str):        The name of the motor port. This is a letter
								between A and D.
		direction (Direction):  Whether the sensor should be rotating
								clockwise or counter-clockwise. Defaults to
								:code:`CLOCKWISE`.
		gears (list):           Additional list of gears that are linked to the
								motor, to allow for better control. Defaults to
								:code:`None` (i.e., the empty list).
		control (Control):      The Motors themselves use a PID controller. To fully
								manipulate their behaviour, use the :class:`Control` class.

	:Output Ports:
		**OUT1** -- The rotational velocity in deg/s.
	"""
	def __init__(self, block_name, port_name, direction=Direction.CLOCKWISE, gears=None, control=None):
		super().__init__(block_name, input_ports=[], output_ports=["OUT1"])
		self.port = getattr(Port, port_name)
		self.motor = Motor(self.port, direction, gears)
		if control is not None:
			self.motor.control = control

	def compute(self, curIteration):
		value = self.motor.speed()
		self.appendToSignal(value, "OUT1")


class MotorAngleSensorBlock(BaseBlock):
	"""
	Block to compute an angle of a Motor.

	Arguments:
		block_name (str):       The name of the block.
		port_name (str):        The name of the motor port. This is a letter
								between A and D.
		direction (Direction):  Whether the positive rotation should be
								clockwise or counter-clockwise. Defaults to
								:code:`CLOCKWISE`.
		resettable (bool):      When :code:`True`, an input is added on which the
								angle can be changed. Defaults to :code:`False`.
		gears (list):           Additional list of gears that are linked to the
								motor, to allow for better control. Defaults to
								:code:`None` (i.e., the empty list).
		control (Control):      The Motors themselves use a PID controller. To fully
								manipulate their behaviour, use the :class:`Control` class.

	:Input Ports:
		**IN1** -- New value for the angle in deg. Optional port if the angle can be reset.

	:Output Ports:
		**OUT1** -- The angle in deg.
	"""
	def __init__(self, block_name, port_name, direction=Direction.CLOCKWISE, resettable=False, gears=None, control=None):
		super().__init__(block_name, input_ports=[], output_ports=["OUT1"])
		self.port = getattr(Port, port_name)
		self.motor = Motor(self.port, direction, gears)
		if control is not None:
			self.motor.control = control
		self.resettable = resettable
		if self.resettable:
			self.addInputPort("IN1")

	def compute(self, curIteration):
		if self.resettable:
			self.motor.reset_angle(self.getInputSignal(curIteration, "IN1"))
		value = self.motor.angle()
		self.appendToSignal(value, "OUT1")


class DifferentialDrive(BaseBlock):
	"""
	Implements the builtin Differential Drive Odometry from Pybricks.

	This assumes your robot has two nonholonomic wheels (and an optional ball caster),
	both wheels are connected to their own motor, but virtually located among the same
	axis. The robot center is the center of both wheels.

	This block ignores slipping and skidding and mainly should only be used as "estimation"
	information, as LEGO is not precise enough for exact, accurate data.

	Arguments:
		block_name (str):       The name of the block.
		left_port_name (str):   The name of the left motor port. This is a letter
								between A and D.
		right_port_name (str):  The name of the right motor port. This is a letter
								between A and D.
		wheel_diameter (float): The diameter of the wheel.
		axle_length (float):    The distance between both wheels.
		ldirection (Direction): Whether the left motor's positive rotation should be
								clockwise or counter-clockwise. Defaults to
								:code:`CLOCKWISE`.
		rdirection (Direction): Whether the right motor's positive rotation should be
								clockwise or counter-clockwise. Defaults to
								:code:`CLOCKWISE`.
		left_gears (list):      Additional list of gears that are linked to the left
								motor, to allow for better control. Defaults to
								:code:`None` (i.e., the empty list).
		right_gears (list):     Additional list of gears that are linked to the right
								motor, to allow for better control. Defaults to
								:code:`None` (i.e., the empty list).
		l_control (Control):    The Motors themselves use a PID controller. To fully
								manipulate their behaviour, use the :class:`Control` class.
								This value alters the left motor's control.
		r_control (Control):    The Motors themselves use a PID controller. To fully
								manipulate their behaviour, use the :class:`Control` class.
								This value alters the right motor's control.
		v_control (Control):    The Motors themselves use a PID controller. To fully
								manipulate their behaviour, use the :class:`Control` class.
								This value alters the linear velocity control.
		h_control (Control):    The Motors themselves use a PID controller. To fully
								manipulate their behaviour, use the :class:`Control` class.
								This value alters the rotational velocity control.

	:Input Ports:
		- **IN1** -- The linear velocity in mm/s.
		- **IN2** -- The angular velocity (top view) in deg/s. This is not the wheel rotation velocity.

	Warning:
		You cannot manipulate the motors individually while this block is active.
	"""
	def __init__(self, block_name, left_port_name, right_port_name, wheel_diameter, axle_length,
	             ldirection=Direction.CLOCKWISE, rdirection=Direction.CLOCKWISE, left_gears=None, right_gears=None,
	             l_control=None, r_control=None, v_control=None, h_control=None):
		super().__init__(block_name, input_ports=["IN1", "IN2"], output_ports=[])
		self.left_port = getattr(Port, left_port_name)
		self.right_port = getattr(Port, right_port_name)

		self.left_motor = Motor(self.left_port, ldirection, left_gears)
		if l_control is not None:
			self.left_motor.control = l_control

		self.right_motor = Motor(self.right_port, rdirection, right_gears)
		if r_control is not None:
			self.right_motor.control = r_control

		self.drive_base = DriveBase(self.left_motor, self.right_motor, wheel_diameter, axle_length)
		if v_control is not None:
			self.drive_base.distance_control = v_control
		if h_control is not None:
			self.drive_base.heading_control = h_control

	def compute(self, curIteration):
		v = self.getInputSignal(curIteration, "IN1")
		h = self.getInputSignal(curIteration, "IN2")

		self.drive_base.drive(v, h)

	def __del__(self):
		# Ensures that the motors actually stop
		self.drive_base.stop()