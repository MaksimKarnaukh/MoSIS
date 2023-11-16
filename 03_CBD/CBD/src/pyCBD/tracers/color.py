"""
Helper file for color information when printing to the terminal.
"""
import re

class COLOR:
	"""
	Color interface to write colored text to the console. This can be used
	to mark certain components of a trace, when writing to the console.

	Colors may be combined using string concatenation (+).

	Note:
		To make this work on Windows 10, `VT100 emulation
		<https://docs.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences?redirectedfrom=MSDN>`_
		needs to be enabled. For other versions, `ANSICON <https://github.com/adoxa/ansicon>`_
		needs to be used. On other OS, it should work out-of-the-bag.
	"""

	@staticmethod
	def colorize(text, *colors):
		"""
		Colors the text in a given set of colors and terminates the coloring at the end.

		Args:
			text (str): The text to color.
			*colors:    The colors for the text. May be given as a set of arguments, or
						as a concatenated string.
		"""
		col = "".join(colors)
		return col + text + COLOR.ENDC

	@staticmethod
	def uncolorize(text):
		"""
		Removes all colorization indicators from the string.

		Args:
			text (str): The string to remove color from.
		"""
		return re.sub(r"\033\[\d+m", "", text)

	@staticmethod
	def rainbow(text, colors=None):
		"""
		Colors each letter of the text in another color, based on the color list.

		Args:
			text (str):     Text to color.
			colors (iter):  An ordered sequence of colors.
							Defaults to the colors of the rainbow.
		"""
		if colors is None:
			colors = (COLOR.RED, COLOR.DARK + COLOR.LYELLOW, COLOR.YELLOW,
			          COLOR.GREEN, COLOR.CYAN, COLOR.DARK + COLOR.BLUE, COLOR.PURPLE)
		ntext = ""
		L = len(colors)
		for i in range(len(text)):
			ntext += COLOR.colorize(text[i], colors[i % L])
		return ntext

	ENDC = '\033[0m'
	"""Ends any coloring. Must be used at the end to prevent color "creep"."""

	BOLD = '\033[1m'
	"""Makes the text bold."""

	DARK = '\033[2m'
	"""Makes the text slightly darker."""

	ITALIC = '\033[3m'
	"""Makes the text slanted/cursive/italic."""

	ULINE = '\033[4m'
	"""Makes the text underlined."""

	BLINK = '\033[5m'
	"""Makes the text blink at the cursor blink rate."""

	HIGHLIGHT = '\033[7m'
	"""Highlights the text by swapping foreground and background colors."""

	STRIKE = '\033[9m'
	"""Draws a line through the text, commonly known as 'strikethrough'."""

	UULINE = '\033[21m'
	"""Makes the text doubly underlined."""

	OLINE = '\033[53m'
	"""Makes the text overlined."""

	DARKGRAY = '\033[30m'
	"""Makes the text dark gray (depends on the terminal palette)."""

	RED = '\033[31m'
	"""Makes the text red (depends on the terminal palette)."""

	GREEN = '\033[32m'
	"""Makes the text green (depends on the terminal palette)."""

	YELLOW = '\033[33m'
	"""Makes the text yellow (depends on the terminal palette)."""

	BLUE = '\033[34m'
	"""Makes the text blue (depends on the terminal palette)."""

	PURPLE = '\033[35m'
	"""Makes the text purple (depends on the terminal palette)."""

	CYAN = '\033[36m'
	"""Makes the text cyan (depends on the terminal palette)."""

	LIGHTGRAY = '\033[37m'
	"""Makes the text light gray (depends on the terminal palette)."""

	BDARKGRAY = '\033[40m'
	"""Makes the background dark gray (depends on the terminal palette)."""

	BRED = '\033[41m'
	"""Makes the background red (depends on the terminal palette)."""

	BGREEN = '\033[42m'
	"""Makes the background green (depends on the terminal palette)."""

	BYELLOW = '\033[43m'
	"""Makes the background yellow (depends on the terminal palette)."""

	BBLUE = '\033[44m'
	"""Makes the background blue (depends on the terminal palette)."""

	BPURPLE = '\033[45m'
	"""Makes the background purple (depends on the terminal palette)."""

	BCYAN = '\033[46m'
	"""Makes the background cyan (depends on the terminal palette)."""

	BLIGHTGRAY = '\033[47m'
	"""Makes the background light gray (depends on the terminal palette)."""

	LDARKGRAY = '\033[90m'
	"""Makes the text a lighter dark gray (depends on the terminal palette)."""

	LRED = '\033[91m'
	"""Makes the text a lighter red (depends on the terminal palette)."""

	LGREEN = '\033[92m'
	"""Makes the text a lighter green (depends on the terminal palette)."""

	LYELLOW = '\033[93m'
	"""Makes the text a lighter yellow (depends on the terminal palette)."""

	LBLUE = '\033[94m'
	"""Makes the text a lighter blue (depends on the terminal palette)."""

	LPURPLE = '\033[95m'
	"""Makes the text a lighter purple (depends on the terminal palette)."""

	LCYAN = '\033[96m'
	"""Makes the text a lighter cyan (depends on the terminal palette)."""

	LLIGHTGRAY = '\033[97m'
	"""Makes the text a lighter light gray (depends on the terminal palette)."""

	BLDARKGRAY = '\033[100m'
	"""Makes the background a lighter dark gray (depends on the terminal palette)."""

	BLRED = '\033[101m'
	"""Makes the background a lighter red (depends on the terminal palette)."""

	BLGREEN = '\033[102m'
	"""Makes the background a lighter green (depends on the terminal palette)."""

	BLYELLOW = '\033[103m'
	"""Makes the background a lighter yellow (depends on the terminal palette)."""

	BLBLUE = '\033[104m'
	"""Makes the background a lighter blue (depends on the terminal palette)."""

	BLPURPLE = '\033[105m'
	"""Makes the background a lighter purple (depends on the terminal palette)."""

	BLCYAN = '\033[106m'
	"""Makes the background a lighter cyan (depends on the terminal palette)."""

	BLLIGHTGRAY = '\033[107m'
	"""Makes the background a lighter light gray (depends on the terminal palette)."""
