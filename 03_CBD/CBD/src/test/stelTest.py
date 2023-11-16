#!/usr/bin/env python
"""
Unit tests for the state event locators
"""

import unittest
import math

from pyCBD.state_events.locators import *
from pyCBD.state_events import Direction

class StELTestCase(unittest.TestCase):
	def setUp(self) -> None:
		self.func = lambda t: (math.sin(t) * math.cos(2*t)) + 6
		self.level = 6
		self.eps = 1e-5

		x1 = -0.421
		y1 = self.func(x1)
		x2 = 0.421
		y2 = self.func(x2)
		x3 = 2.721
		y3 = self.func(x2)

		self.p1 = x1, y1
		self.p2 = x2, y2
		self.p3 = x3, y3

	def testPre(self):
		stel = PreCrossingStateEventLocator()

		a = stel.algorithm(self.p1, self.p3, self.func, self.level, Direction.ANY)
		b = stel.algorithm(self.p1, self.p3, self.func, self.level, Direction.FROM_BELOW)
		c = stel.algorithm(self.p1, self.p3, self.func, self.level, Direction.FROM_ABOVE)
		d = stel.algorithm(self.p2, self.p3, self.func, self.level, Direction.ANY)

		self.assertAlmostEqual(self.p1[0], a, 5)
		self.assertAlmostEqual(self.p1[0], b, 5)
		self.assertAlmostEqual(self.p1[0], c, 5)
		self.assertAlmostEqual(self.p2[0], d, 5)

	def testPost(self):
		stel = PostCrossingStateEventLocator()

		a = stel.algorithm(self.p1, self.p3, self.func, self.level, Direction.ANY)
		b = stel.algorithm(self.p1, self.p3, self.func, self.level, Direction.FROM_BELOW)
		c = stel.algorithm(self.p1, self.p3, self.func, self.level, Direction.FROM_ABOVE)
		d = stel.algorithm(self.p1, self.p2, self.func, self.level, Direction.ANY)

		self.assertAlmostEqual(self.p3[0], a, 5)
		self.assertAlmostEqual(self.p3[0], b, 5)
		self.assertAlmostEqual(self.p3[0], c, 5)
		self.assertAlmostEqual(self.p2[0], d, 5)

	def testLinear(self):
		stel = LinearStateEventLocator()

		a = stel.algorithm(self.p1, self.p3, self.func, self.level, Direction.ANY)
		b = stel.algorithm(self.p1, self.p3, self.func, self.level, Direction.FROM_BELOW)
		c = stel.algorithm(self.p1, self.p3, self.func, self.level, Direction.FROM_ABOVE)
		d = stel.algorithm(self.p2, self.p3, self.func, self.level, Direction.ANY)

		mid = (self.p3[0] - self.p1[0]) / 2 + self.p1[0]

		self.assertAlmostEqual(mid, a, 5)
		self.assertAlmostEqual(mid, b, 5)
		self.assertAlmostEqual(mid, c, 5)
		self.assertAlmostEqual(self.p2[0], d, 5)

	def testBisection(self):
		stel = BisectionStateEventLocator(200)

		a = stel.algorithm(self.p1, self.p3, self.func, self.level, Direction.ANY)
		b = stel.algorithm(self.p1, self.p3, self.func, self.level, Direction.FROM_BELOW)
		c = stel.algorithm(self.p2, self.p3, self.func, self.level, Direction.ANY)
		d = stel.algorithm(self.p2, self.p3, self.func, self.level, Direction.FROM_ABOVE)

		x2 = math.pi * 0.25
		x3 = math.pi * 0.75

		self.assertAlmostEqual(x2, a, 5)
		self.assertAlmostEqual(x3, b, 5)
		self.assertAlmostEqual(x2, c, 5)
		self.assertAlmostEqual(x2, d, 5)

	def testRegulaFalsi(self):
		stel = RegulaFalsiStateEventLocator()

		a = stel.algorithm(self.p1, self.p3, self.func, self.level, Direction.ANY)
		b = stel.algorithm(self.p1, self.p3, self.func, self.level, Direction.FROM_BELOW)
		c = stel.algorithm(self.p2, self.p3, self.func, self.level, Direction.ANY)
		d = stel.algorithm(self.p2, self.p3, self.func, self.level, Direction.FROM_ABOVE)

		x2 = math.pi * 0.25
		x3 = math.pi * 0.75

		self.assertAlmostEqual(x3, a, 5)
		self.assertAlmostEqual(x3, b, 5)
		self.assertAlmostEqual(x2, c, 5)
		self.assertAlmostEqual(x2, d, 5)

	def testITP(self):
		stel = RegulaFalsiStateEventLocator()

		a = stel.algorithm(self.p1, self.p3, self.func, self.level, Direction.ANY)
		b = stel.algorithm(self.p1, self.p3, self.func, self.level, Direction.FROM_BELOW)
		c = stel.algorithm(self.p2, self.p3, self.func, self.level, Direction.ANY)
		d = stel.algorithm(self.p2, self.p3, self.func, self.level, Direction.FROM_ABOVE)

		x2 = math.pi * 0.25
		x3 = math.pi * 0.75

		self.assertAlmostEqual(x3, a, 5)
		self.assertAlmostEqual(x3, b, 5)
		self.assertAlmostEqual(x2, c, 5)
		self.assertAlmostEqual(x2, d, 5)
