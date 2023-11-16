"""
Helper module to allow for simplified logging.

Note:
	The logic in this file is based on https://stackoverflow.com/a/384125

Warning:
	In the future, this module may be removed. Its logic will
	be separated into some tracers and a SysLog logger.
"""
import logging

__all__ = ["logger"]

#These are the sequences need to get colored ouput
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color = True):
	if use_color:
		message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
	else:
		message = message.replace("$RESET", "").replace("$BOLD", "")
	return message

COLORS = {
	'WARNING': YELLOW,
	'INFO': CYAN,
	'DEBUG': BLUE,
	'CRITICAL': RED,
	'ERROR': RED
}

class ColoredFormatter(logging.Formatter):
	def __init__(self, msg, use_color = True):
		logging.Formatter.__init__(self, msg)
		self.use_color = use_color

	def format(self, record):
		levelname = record.levelname
		if self.use_color and levelname in COLORS:
			levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
			record.levelname = levelname_color
		if hasattr(record, "block"):
			record.simtime = record.block.getClock().getTime()
			record.blockname = record.block.getPath()
		return logging.Formatter.format(self, record)

class LoggingHandler(logging.StreamHandler):
	FORMAT = "[$BOLD%(name)s$RESET][%(blockname)-18s][$BOLD%(levelname)-18s$RESET]  %(message)s"
	COLOR_FORMAT = formatter_message(FORMAT, True)

	def __init__(self, stream=None):
		logging.StreamHandler.__init__(self, stream)
		color_formatter = ColoredFormatter(self.COLOR_FORMAT)
		self.setFormatter(color_formatter)

	def emit(self, record):
		super().emit(record)
		if record.levelno >= logging.ERROR:
			raise SystemExit(1)

logger = logging.getLogger("CBD")
logger.setLevel(logging.DEBUG)
logger.addHandler(LoggingHandler())