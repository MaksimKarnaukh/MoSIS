"""
This module contains a class to construct butcher tableaus and a set of predefined tables.
"""

class ButcherTableau:
	r"""
	Mnemonic device to store the Runge-Kutta matrix, weights and nodes in
	the computation of generic RK methods. The extended tableau also allows
	for the error computation for adaptive step sizes. The general form of
	a Butcher Tableau is shown below, where:

	* :math:`s` identifies the number of stages;
	* :math:`a_{ij}, 1 \leq j < i \leq s` represents a coefficient in the
	  Runge-Kutta matrix;
	* :math:`b_i` and :math:`b^*_i` correspond to the weights of a higher
	  and a lower order method, respectively; and
	* :math:`c_i` specifies the nodes.

	.. math::

		\begin{array}
			{c|ccccc}
			0\\
			c_2 & a_{2,1}\\
			c_3 & a_{3,1} & a_{3,2} \\
			\vdots & \vdots & & \ddots\\
			c_s & a_{s,1} & a_{s,2} & \cdots & a_{s,s-1}\\
			\hline
			& b_1 & b_2 & \cdots & b_{s-1} & b_s\\
			& b^*_1 & b^*_2 & \cdots & b^*_{s-1} & b^*_s\\
		\end{array}

	Args:
		rows (iter):    Sequence of tuples :math:`(c_i, [a_{i, j}\vert 1 \leq j < i])`.
						When :code:`None`, nothing will be added.
		weights (iter): Sequence of sequences of weights :math:`[b_{i}\vert i \leq s]`.
						When :code:`None`, no weights will be added.

	Note:
		Upon instantiation, the first (empty) row will be added automatically with a
		node of 0.
	"""
	def __init__(self, rows=None, weights=None):
		self._matrix = []
		self._weights = []
		self._nodes = [0]

		if rows is not None:
			for node, mtx in rows:
				self.addRow(node, mtx)
			if weights is not None:
				for w in weights:
					self.addWeights(w)

	def addRow(self, node, elems):
		r"""
		Adds a :math:`c_i` and :math:`a_{i, j}` to the tableau.

		Args:
			node (numeric): The :math:`c_i`-value.
			elems (iter):   :math:`a_{i, j}`, :math:`\forall j < i`; i.e. the
							sequence of matrix elements that correspond to the node.
		"""
		if len(self._nodes) != len(elems):
			raise ValueError("Inconsistent matrix! Expected row with %d elements!" % len(self._nodes))
		self._nodes.append(node)
		self._matrix.append(elems)

	def addWeights(self, *weights):
		"""
		Adds a row of weights to the bottom of the matrix.

		Args:
			*weights:   A sequence of the weights. I.e. :math:`b_{i}`, where :math:`1 \leq i \leq s`.
		"""
		if len(self._matrix) != 0 and (len(self._matrix[-1]) + 1) != len(weights):
			raise ValueError("Trying to set weights on incomplete matrix")
		if len(self._matrix) == 0 and len(weights) != 1:
			raise ValueError("First-Order tableau can only take a single weight")
		if len(self._weights) == 2:
			raise ValueError("Maximal amount of weight rows (2) reached")
		if abs(sum(weights) - 1) > 1e-6:
			raise ValueError("Inconsistent Butcher Tableau for Runge-Kutta approximation. "
			                 "The sum of the weights must equal 1.")
		self._weights.append(weights)

	def getNodes(self):
		"""
		Obtains the nodes, i.e. the :math:`c_i`-values.
		"""
		return self._nodes

	def getWeights(self):
		"""
		Obtains the weight lists, i.e. the :math:`b_i` and :math:`b^*_i`-values.
		"""
		return self._weights

	def getA(self, i, j):
		"""
		Obtains an element from the Runge-Kutta matrix.

		Args:
			i (int):    The row (1-indexed).
			j (int):    The column (1-indexed).
		"""
		return self._matrix[i - 1][j - 1]

	def getOrder(self, wix=-1):
		"""
		Computes the order of the Tableau.
		The order is the amount of non-zero weights.

		Args:
			wix (id):   The weight index. Defaults to -1 (i.e.
						the last weight row of the tableau).
		"""
		return int(round(sum([1 for i in self._weights[wix] if abs(i) > 1e-16])))

	@staticmethod
	def Euler():
		r"""
		Creates and returns the Butcher Tableau for Euler's method.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				\hline
				& 1
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addWeights(1)
		return tab

	@staticmethod
	def Heun():
		r"""
		Creates and returns the Butcher Tableau for Heun's method.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				1 & 1\\
				\hline
				& 1/2 & 1/2
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow(1, [1])
		tab.addWeights(1/2, 1/2)
		return tab

	@staticmethod
	def HeunEuler():
		r"""
		Creates and returns the extended Butcher Tableau for Heun's method,
		combined with the Euler method.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				1 & 1\\
				\hline
				& 1/2 & 1/2\\
				& 1 & 0
			\end{array}
		"""
		tab = ButcherTableau.Heun()
		tab.addWeights(1, 0)
		return tab

	@staticmethod
	def Ralston():
		r"""
		Creates and returns the Butcher Tableau for Ralston's method for 2nd order
		accuracy. The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				2/3 & 2/3\\
				\hline
				& 1/4 & 3/4
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow(2/3, [2/3])
		tab.addWeights(1/4, 3/4)
		return tab

	@staticmethod
	def RalstonEuler():
		r"""
		Creates and returns the extended Butcher Tableau for Ralston's method,
		combined with the Euler method.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				2/3 & 2/3\\
				\hline
				& 1/4 & 3/4\\
				& 1 & 0
			\end{array}
		"""
		tab = ButcherTableau.Ralston()
		tab.addWeights(1, 0)
		return tab

	@staticmethod
	def Midpoint():
		r"""
		Creates and returns the Butcher Tableau for the midpoint method.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				1/2 & 1/2\\
				\hline
				&   0 &   1
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow(1/2, [1/2])
		tab.addWeights(0, 1)
		return tab

	@staticmethod
	def MidpointEuler():
		r"""
		Creates and returns the extended Butcher Tableau for the midpoint method,
		combined with the Euler method.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				1/2 & 1/2\\
				\hline
				& 0 & 1\\
				& 1 & 0
			\end{array}
		"""
		tab = ButcherTableau.Midpoint()
		tab.addWeights(1, 0)
		return tab

	@staticmethod
	def RK4():
		r"""
		Creates and returns the Butcher Tableau for the default RK
		algorithm.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				1/2 & 1/2\\
				1/2 &   0 & 1/2\\
				1   &   0 &   0 &   1\\
				\hline
				    & 1/6 & 1/3 & 1/3 & 1/6
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow(1/2, [1/2])
		tab.addRow(1/2, [1/2, 1/2])
		tab.addRow(  1, [  0,   0, 1])
		tab.addWeights(1/6, 1/3, 1/3, 1/6)
		return tab

	@staticmethod
	def RK4Alt():
		r"""
		Creates and returns the Butcher Tableau for an alternative RK
		algorithm. It is also called the 3/8-rule.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				1/3 &  1/3\\
				2/3 & -1/3 &   1\\
				1   &    1 &  -1 &   1\\
				\hline
				    & 1/8 & 3/8 & 3/8 & 1/8
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow(1/3, [ 1/3])
		tab.addRow(2/3, [-1/3, 1])
		tab.addRow(  1, [   1, -1, 1])
		tab.addWeights(1/8, 3/8, 3/8, 1/8)
		return tab

	@staticmethod
	def RKF45():
		r"""
		Creates and returns the extended Butcher Tableau for the
		Runge-Kutta-Fehlberg algorithm of 4th and 5th order.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				    0\\
				  1/4 &       1/4\\
				  3/8 &      3/32 &       9/32\\
				12/13 & 1932/2197 & -7200/2197 &  7296/2197\\
				    1 &   439/216 &         -8 &   3680/513 &   -845/4104\\
				  1/2 &     -8/27 &          2 & -3544/2565 &   1859/4104 & -11/40\\
				\hline
				      &    16/135 &          0 & 6656/12825 & 28561/56430 &  -9/50 & 2/55\\
				      &    25/216 &          0 &  1408/2565 &   2197/4104 &   -1/5 &    0
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow(  1/4, [      1/4])
		tab.addRow(  3/8, [     3/32,       9/32])
		tab.addRow(12/13, [1932/2197, -7200/2197,  7296/2197])
		tab.addRow(    1, [  439/216,         -8,   3680/513,   -845/4104])
		tab.addRow(  1/2, [    -8/27,          2, -3544/2565,   1859/4104, -11/40])
		tab.addWeights(       16/135,          0, 6656/12825, 28561/56430,  -9/50, 2/55)
		tab.addWeights(       25/216,          0,  1408/2565,   2197/4104,   -1/5,    0)
		return tab

	@staticmethod
	def DOPRI():
		r"""
		Creates and returns the extended Butcher Tableau for the
		`Dormand-Prince method <https://www.sciencedirect.com/science/article/pii/0771050X80900133?via%3Dihub>`_.
		This is the default method in the :code:`ode45` solver for MATLAB and GNU Octave, among others.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				   0\\
				 1/5 &         1/5\\
				3/10 &        3/40 &        9/40\\
				 4/5 &       44/45 &      -56/15 &       32/9\\
				 8/9 &  19372/6561 & -25360/2187 & 64448/6561 & -212/729\\
				   1 &   9017/3168 &     -355/33 & 46732/5247 &   49/176 &   -5103/18656\\
				   1 &      35/384 &           0 &   500/1113 &  125/192 &    -2187/6784 &    11/84\\
				\hline
				      &     35/384 &           0 &   500/1113 &  125/192 &    -2187/6784 &    11/84 &    0\\
				      & 5179/57600 &           0 & 7571/16695 &  393/640 & -92097/339200 & 187/2100 & 1/40
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow( 1/5, [        1/5])
		tab.addRow(3/10, [       3/40,        9/40])
		tab.addRow( 4/5, [      44/45,      -56/15,       32/9])
		tab.addRow( 8/9, [ 19372/6561, -25360/2187, 64448/6561, -212/729])
		tab.addRow(   1, [  9017/3168,     -355/33, 46732/5247,   49/176,   -5103/18656])
		tab.addRow(   1, [     35/384,           0,   500/1113,  125/192,    -2187/6784,    11/84])
		tab.addWeights(        35/384,           0,   500/1113,  125/192,    -2187/6784,    11/84,    0)
		tab.addWeights(    5179/57600,           0, 7571/16695,  393/640, -92097/339200, 187/2100, 1/40)
		return tab

	RKDP = DOPRI
	"Alias of :func:`DOPRI`."

	DormandPrince = DOPRI
	"Alias of :func:`DOPRI`."

	@staticmethod
	def RKCK():
		r"""
		Creates and returns the extended Butcher Tableau for the
		`Cash-Karp method <https://dl.acm.org/doi/10.1145/79505.79507>`_ for 4th and 5th order
		accurate solutions.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				   0\\
				 1/5 &         1/5\\
				3/10 &        3/40 &    9/40\\
				 3/5 &        3/10 &   -9/10 &         6/5\\
				   1 &      -11/54 &     5/2 &      -70/27 &        35/27\\
				 7/8 &  1631/55296 & 175/512 &   575/13824 & 44275/110592 &  253/4096\\
				\hline
				      &     37/378 &       0 &     250/621 &      125/594 &         0 & 512/1771\\
				      & 2825/27648 &       0 & 18575/48384 &  13525/55296 & 277/14336 &      1/4
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow( 1/5, [       1/5])
		tab.addRow(3/10, [       3/40,    9/40])
		tab.addRow( 3/5, [       3/10,   -9/10,         6/5])
		tab.addRow(   1, [     -11/54,     5/2,      -70/27,        35/27])
		tab.addRow( 7/8, [ 1631/55296, 175/512,   575/13824, 44275/110592,  253/4096])
		tab.addWeights(        37/378,       0,     250/621,      125/594,         0, 512/1771)
		tab.addWeights(    2825/27648,       0, 18575/48384,  13525/55296, 277/14336,      1/4)
		return tab

	CashKarp = RKCK
	"Alias of :func:`RKCK`."

	@staticmethod
	def BogackiShampine():
		r"""
		Creates and returns the extended Butcher Tableau for the
		`Bogacki-Shampine method <https://doi.org/10.1016%2F0893-9659%2889%2990079-7>`_ for 3th order
		accurate solutions.

		It is implemented in the :code:`ode23` function in MATLAB.

		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				  0\\
				1/2 &  1/2\\
				3/4 &    0 & 3/4\\
				  1 &  2/9 & 1/3 & 4/9\\
				\hline
				    &  2/9 & 1/3 & 4/9 &   0\\
					& 7/24 & 1/4 & 1/3 & 1/8
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow(1/2, [ 1/2])
		tab.addRow(3/4, [   0, 3/4])
		tab.addRow(  1, [ 2/9, 1/3, 4/9])
		tab.addWeights(   2/9, 1/3, 4/9,   0)
		tab.addWeights(  7/24, 1/4, 1/3, 1/8)
		return tab
