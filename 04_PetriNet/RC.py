#!/usr/bin/env python3
"""
	Simple script for generating a Reachability or a Coverability Graph from a TAPAAL
	Petri-Net (https://www.tapaal.net/). Additionally, it is possible to generate the
	P-Invariant formulas for the given net. The net must not be a Game Net or a Timed
	Net. It is allowed to contain inhibitor and/or weighted arcs. Note that the net
	should not yield any errors in TAPAAL for this script to work.

	Upon execution of this script, a GraphViz file will be created, which can be
	converted to an image or viewed in xdot, GraphDonkey or any other GraphViz viewer.
	Large graphs (over 1000 nodes) might not be displayable due to their size. In general,
	the LTL/CTL languages are used for Petri-Net analysis. This script is therefore purely
	meant for educational purposes, hence the limited node size should not be a problem.

	The script can easily be executed with "./RC.py input [output] type", where the output
	file is optional and the 'type' is expected to be a prefix of either 'reachability' or
	'coverability' (case-insensitve), depending on what was desired. More info and options
	are given when the script is executed with the '-h' or '--help' flag.
"""

import xml.etree.ElementTree as ET
import math

def gcd(collection):
	r = 0
	for c in collection:
		r = math.gcd(r, c)
	return r

NAMESPACE = 'http://www.informatik.hu-berlin.de/top/pnml/ptNetb'  # The namespace of the *.tapn XML
nm = lambda n: '{%s}%s' % (NAMESPACE, n)                          # Automatically applies the namespace

OMEGA = u"\u03C9"   # The omega symbol

class PetriNet:
	"""
	Simple Petri-Net class.

	Args:
		fname (str):	The name of the *.tapn file, which contains the Petri-Net.

	Raises:
		TypeError if the net is not a P/T net, or when it is a Game Net or a Timed Net.
	"""
	def __init__(self, fname):
		self.places = {}       # The set of places:   {ID -> [name, marking]}
		self.transitions = {}  # The transitions:     {ID -> name}
		self.arcs = {}         # The arcs:            {ID -> (source, target, isInhibitor, weight)}
		self._sa = {}          # The source-arc link: {SourceID -> ArcID*}
		self._ta = {}          # The target-arc link: {TargetID -> ArcID*}
		self._mvec = []        # The ordered marking vector; all place IDs
		self._vars = {}        # The variables that can be used as weights in a net
		self._shared = set()   # A dictionary of all shared places

		tree = ET.parse(fname)
		root = tree.getroot()

		duplicates = {}

		# Check validity
		fts = root.find(nm('feature')).attrib
		if fts['isGame'] != "false" and fts['isTimed'] != "false":
			raise TypeError("Invalid Net")

		# Obtain all constants
		for var in root.iter(nm('constant')):
			attr = var.attrib
			self._vars[attr['name']] = float(attr['value'])

		# Obtain all shared places
		# Shared places do not get a prefix
		# This prevents name collisions
		for place in root.iter(nm('shared-place')):
			attr = place.attrib
			id = attr['name']
			self._shared.add(id)
			self.places[id] = [id, int(attr['initialMarking'])]
			self._mvec.append(id)

		for net in root.iter(nm('net')):
			if net.attrib['type'] != "P/T net":
				raise TypeError("Invalid Net")

			net_id = net.attrib['id']

			# Prepend all ids and names with the net_id
			#  to prevent name collisions
			def get_name(name):
				if name in self._shared:
					return name
				return net_id + "." + name

			ctr = 0
			for place in net.iter(nm('place')):
				attr = place.attrib
				if attr['id'] in self._shared:
					continue
				id = get_name(attr['id'])
				self.places[id] = [get_name(attr['name']), int(attr['initialMarking'])]
				self._mvec.append(id)
				ctr += 1
			ctr = 0
			for trans in net.iter(nm('transition')):
				attr = trans.attrib
				id = get_name(attr['id'])
				self.transitions[id] = get_name(attr['name'])
				ctr += 1
			ctr = 0
			for arc in net.iter(nm('arc')):
				attr = arc.attrib
				id = get_name(attr['id'])
				if id in self.arcs:
					if id not in duplicates:
						duplicates[id] = 2
					else:
						duplicates[id] += 1
					id += "-" + str(duplicates[id])
				weight = int(self._vars.get(attr['weight'], attr['weight']))
				self.arcs[id] = (get_name(attr['source']), get_name(attr['target']), (attr['type'] == 'tapnInhibitor'), weight)
				self._sa.setdefault(get_name(attr['source']), []).append(id)
				self._ta.setdefault(get_name(attr['target']), []).append(id)
				if self.arcs[id][0] in self.places and self.arcs[id][1] in self.places:
					raise ValueError("Cannot connect place %s to place %s!" % (self.arcs[id][0], self.arcs[id][1]))
				if self.arcs[id][0] in self.transitions and self.arcs[id][1] in self.transitions:
					raise ValueError("Cannot connect transition %s to transition %s!" % (self.arcs[id][0], self.arcs[id][1]))
				ctr += 1

			# print(net_id)
			# for k, v in self.arcs.items():
			# 	print("\t", k, "=>", v)
		self._mvec.sort()

	def setMarking(self, marking):
		"""
		Sets the current marking.

		Args:
			marking (iter):	The marking to set.
		"""
		for i, m in enumerate(marking):
			self.places[self._mvec[i]][1] = m

	def getMarking(self):
		"""
		Obtains the current marking.
		"""
		res = []
		for pid in self._mvec:
			res.append(self.places[pid][1])
		return res

	@staticmethod
	def toString(marking):
		"""
		Converts a marking to a string. This prevents the quotes around omegas.
		"""
		return "[%s]" % ", ".join([str(x) for x in marking])

	def canFire(self, trans):
		"""
		Checks if a transition can fire.

		Args:
			trans (str):	The transition's ID.
		"""
		for aid in self._ta.get(trans, []):
			source, _, inh, w = self.arcs[aid]
			tokens = self.places[source][1]
			if inh and PetriNet.intLTE(w, tokens):
				return False
			elif not inh and type(tokens) == int and PetriNet.intLT(tokens, w):
				return False
		return True

	def fire(self, trans):
		"""
		Fires a transition if :func:`canFire` returned :code:`True`.
		Otherwise, an AssertionError is thrown.

		Args:
			trans (str):	The transition's ID.
		"""
		assert self.canFire(trans), "Cannot fire the transition"
		for aid in self._ta.get(trans, []):
			source, _, inh, w = self.arcs[aid]
			if not inh and type(self.places[source][1]) == int:
				self.places[source][1] -= w
		for aid in self._sa.get(trans, []):
			_, target, __, w = self.arcs[aid]
			if target not in self.places:
				print("WARNING: No such place %s reachable from %s. Please recreate both to make your model valid." % (target, trans))
				continue
			if type(self.places[target][1]) == int:
				self.places[target][1] += w

	def nextMarkings(self):
		"""
		Obtains a set of all transitions that can fire and connects
		them to the marking after they would have fired.
		"""
		initial = self.getMarking()[:]
		result = []
		for trans in self.transitions.keys():
			if self.canFire(trans):
				self.fire(trans)
				result.append((trans, self.getMarking()[:]))
				self.setMarking(initial)
		return result

	@staticmethod
	def markingLTE(M1, M2):
		"""
		Checks if M1 <= M2.

		Args:
			M1 (iter):	Marking 1
			M2 (iter):	Marking 2
		"""
		assert len(M1) == len(M2), "Can only compare markings of equal length"
		for i in range(len(M1)):
			if PetriNet.intLT(M2[i], M1[i]):
				return False
		return True

	@staticmethod
	def markingLT(M1, M2):
		"""
		Checks if M1 < M2.

		Args:
			M1 (iter):	Marking 1
			M2 (iter):	Marking 2
		"""
		assert len(M1) == len(M2), "Can only compare markings of equal length"
		for i in range(len(M1)):
			if PetriNet.intLTE(M2[i], M1[i]):
				return False
		return True

	@staticmethod
	def markingLTsome(M1, M2):
		"""
		Checks if there is at least some marking in M1 that is less than M2.

		Args:
			M1 (iter):	Marking 1
			M2 (iter):	Marking 2
		"""
		assert len(M1) == len(M2), "Can only compare markings of equal length"
		for i in range(len(M1)):
			if PetriNet.intLT(M1[i], M2[i]):
				return True
		return False

	@staticmethod
	def markingDominates(M1, M2):
		"""
		Checks if M1 dominates M2.

		Args:
			M1 (iter):	Marking 1
			M2 (iter):	Marking 2
		"""
		assert len(M1) == len(M2), "Can only compare markings of equal length"
		return PetriNet.markingLTE(M2, M1) and PetriNet.markingLTsome(M2, M1)

	@staticmethod
	def intLT(a, b):
		"""
		Checks if a < b.

		Args:
			a:	Either an integer, or :attr:`OMEGA`.
			b:	Either an integer, or :attr:`OMEGA`.
		"""
		return type(b) == int and type(a) == int and a < b

	@staticmethod
	def intLTE(a, b):
		"""
		Checks if a <= b.

		Args:
			a:	Either an integer, or :attr:`OMEGA`.
			b:	Either an integer, or :attr:`OMEGA`.
		"""
		return type(b) == str or (type(a) == int and a <= b)

	def graphviz(self):
		"""
		Obtains the net as a Graphviz file.
		"""
		res = "digraph Net {\n"
		map = {}
		for ip, p in enumerate(self.places.values()):
			res += "\tP%i [label=\"%s\\n%i\"];\n" % (ip, p[0], p[1])
			map[p[0]] = "P%i" % ip
		for it, t in enumerate(self.transitions.values()):
			res += "\tT%i [label=\"%s\", shape=box];\n" % (it, t)
			map[t] = "T%i" % it
		for arc in self.arcs.values():
			source, target, inh, weight = arc
			shape = ""
			if inh:
				shape = ",arrowhead=odot"
			res += "\t%s -> %s [label=\"%i\"%s];\n" % (map[source], map[target], weight, shape)
		res += "}\n"
		return res


	def reachabilityGraph(self, title, start, iterations, tablize=False):
		"""
		Constructs a Reachability Graph for the given net, starting from the
		current marking. This results in a GraphViz string. It is not (yet)
		written to a file.

		Args:
			title (str):		The title for the graph.
			start (str):		The shape for the start node.
			iterations (int):	The maximal amount of iterations to compute.
								This prevents infinite loops.
			tablize (bool):		When :code:`True`, a table with all the values is printed
								to the console, instead of it being added in the nodes themselves.
		"""
		initial = self.getMarking()[:]
		markings = { "S0": initial }
		imarks = { tuple(initial): "S0" }
		edges = {}

		i = 1
		lc = 0
		stack = [initial]
		visited = set()
		while len(stack) > 0 and lc < iterations:
			M = stack.pop()
			S = imarks[tuple(M)]
			if S in visited: continue

			self.setMarking(M)
			nxt = self.nextMarkings()
			for t, n in nxt:
				tn = tuple(n)
				if tn not in imarks:
					imarks[tn] = "S%d" % i
					markings["S%d" % i] = n[:]
					i += 1
				edges.setdefault((S, imarks[tn]), set()).add(t)
				stack.append(n)
			visited.add(S)
			lc += 1

		self.setMarking(initial)
		print("Creating graph with %i nodes..." % len(markings))

		if lc >= iterations:
			print("WARNING: The Reachability Graph's construction was prematurely terminated.\n"
					"         It may be infinite. Try generating the Coverability Graph instead.")

		if len(markings) > 1000:
			print("WARNING: There are over 1000 nodes in the graph. It may not be displayable.")
			if tablize:
				print("\tSkipping table printout.")

		elif tablize:
			with open("table.csv", "wb") as file:
				file.write(("state," + str(self._mvec)[1:-1] + "\n").encode('utf-8'))
				for k, v in markings.items():
					file.write((k + "," + str(v)[1:-1] + "\n").encode('utf-8'))

		dot = "\ndigraph RG {\n"
		dot += "  label=\"%s\";\n" % title
		dot += "  labelloc=t;\n"
		if tablize:
			dot += "  S0 [shape=%s];\n" % (start)
		else:
			dot += "  S0 [shape=%s, label=\"%s\"];\n" % (start, self.toString(initial))
		for k, v in markings.items():
			if k == "S0": continue
			if tablize:
				dot += "  %s;\n" % k
			else:
				dot += "  %s [label=\"%s\"];\n" % (k, self.toString(v))
		for (s, m), t in edges.items():
			t = sorted(t)
			dot += "  %s -> %s [label=\"%s\"];\n" % (s, m, ", ".join([str(x) for x in t]))
		return dot + "}\n"

	def coverabilityGraph(self, title, start, iterations, tablize=False):
		"""
		Constructs a Coverability Graph for the given net, starting from the
		current marking. This results in a GraphViz string. It is not (yet)
		written to a file.

		Args:
			title (str):		The title for the graph.
			start (str):		The shape for the start node.
			iterations (int):	The maximal amount of iterations to compute.
								While technically always ending, this prevents
								too long loops/too large graphs.
			tablize (bool):		When :code:`True`, a table with all the values is printed
								to the console, instead of it being added in the nodes themselves.
		"""
		initial = self.getMarking()[:]
		markings = { "S0": initial }
		imarks = { tuple(initial): "S0" }
		edges = {}
		# paths = { "S0": set() }

		i = 1
		lc = 0
		stack = [initial]
		visited = set()
		while len(stack) > 0 and lc <= iterations:
			# print("-----")
			# print("STACK:", len(stack))
			M = stack.pop()
			S = imarks[tuple(M)]
			if S in visited: continue

			self.setMarking(M)
			nxt = self.nextMarkings()
			for t, n in nxt:
				# print("FIREING", t)
				tn = tuple(n)

				new = False
				if tn not in imarks:
					new = True
					name = "S%d" % i
					imarks[tn] = name
					markings[name] = n[:]
					# if name not in paths:
					# 	paths[name] = set()
					i += 1
				name = imarks[tn]
				# paths[name] |= paths[S] | {S}
				# for G in paths:
				# 	if name in paths[G]:
				# 		paths[G] |= paths[name]

				chngd = True
				while chngd:
					chngd = False
					for node in sorted(markings):
						if self.markingDominates(n, markings[node]):
							for j in range(len(n)):
								if self.intLT(markings[node][j], n[j]):
									n[j] = OMEGA
									chngd = True
				markings[name] = n[:]
				en = tuple(n)
				imarks[en] = name
				tn = en

				# if any([not isinstance(x, str) and x > 20 for x in n]):
				# 	print("FIREING", t, tn)
				# 	print("NAME", name)
					# print(paths[name])

				edges.setdefault((S, imarks[tn]), set()).add(t)
				if new:
					stack.append(n)
					# print("added", n, name)
			visited.add(S)
			if iterations > 0:
				lc += 1

		# Merge duplicate nodes
		to_del_e = set()
		to_del_m = set()
		to_add_e = {}
		korder = markings.keys()
		# Keep doing this node merging as long as the graph keeps changing
		old_e = old_m = 0
		while old_e != len(to_del_e) or old_m != len(to_del_m):
			print("merging...")
			old_e = len(to_del_e)
			old_m = len(to_del_m)
			for i1, S1 in enumerate(korder):
				M1 = markings[S1]
				for i2, S2 in enumerate(korder):
					if i2 <= i1: continue
					M2 = markings[S2]
					if M1 == M2:
						for (s, e), t in edges.items():
							if e == S2:
								to_del_e.add((s, e))
								if s == S2:
									s = S1
								to_add_e[(s, S1)] = t
							elif s == S2:
								to_del_e.add((s, e))
								if e == S2:
									e = S1
								to_add_e[(S1, e)] = t
						to_del_m.add(S2)
			for e in to_del_e:
				del edges[e]
			for m in to_del_m:
				del markings[m]
			for k, v in to_add_e.items():
				edges[k] = v


		self.setMarking(initial)
		print("Creating graph with %i nodes..." % len(markings))

		print(self.places)
		for idx, i in enumerate(self.places):
			print(idx, self.places[i])
		print(len(self.places))

		if lc > iterations:
			print("WARNING: The Coverability Graph's construction was prematurely terminated.\n"
					"         The graph may be incomplete.")

		if len(markings) > 1000:
			print("WARNING: There are over 1000 nodes in the graph. It may not be displayable.")
			if tablize:
				print("\tSkipping table printout.")

		elif tablize:
			with open("table.csv", "wb") as file:
				file.write(("state," + ",".join(self._mvec) + "\n").encode("utf-8"))
				for k, v in markings.items():
					file.write((k + "," + ",".join([str(x) for x in v]) + "\n").encode('utf-8'))

		dot = "digraph CG {\n"
		dot += "  label=\"%s\";\n" % title
		dot += "  labelloc=t;\n"
		if tablize:
			dot += "  S0 [shape=%s];\n" % (start)
		else:
			dot += "  S0 [shape=%s, label=\"%s\"];\n" % (start, self.toString(initial))
		for k, v in markings.items():
			if k == "S0": continue
			if tablize:
				dot += "  %s;\n" % k
			else:
				dot += "  %s [label=\"%s\"];\n" % (k, self.toString(v))
		for (s, m), t in edges.items():
			t = sorted(t)
			dot += "  %s -> %s [label=\"%s\"];\n" % (s, m, ", ".join([str(x) for x in t]))
		return dot + "}\n"

	def getIncidenceMatrix(self):
		"""
		Obtains the incidence matrix of the net.
		"""
		C = []
		for _ in range(len(self.places)):
			C.append([0] * len(self.transitions))

		torder = sorted(self.transitions.keys())
		for tix in range(len(torder)):
			t = torder[tix]
			arcs = self._sa.get(t, [])
			for ax in arcs:
				a = self.arcs[ax]
				if not a[2] and a[1] in self._mvec:
					C[self._mvec.index(a[1])][tix] += a[-1]
			arcs = self._ta.get(t, [])
			for ax in arcs:
				a = self.arcs[ax]
				if not a[2] and a[0] in self._mvec:
					C[self._mvec.index(a[0])][tix] -= a[-1]
		return C

	def Pinv(self):
		"""
		Compute the P-invariants of the net.
		"""
		invs = Matrix.farkas(self.getIncidenceMatrix())
		if len(invs) == 0:
			return ""
		res = ""
		for places in invs:
			s = 0
			for pi in range(len(places)):
				if places[pi] == 0: continue
				place = self.places[self._mvec[pi]]
				if places[pi] == 1:
					res += "M(%s) + " % place[0]
				else:
					res += "%i * M(%s) + " % (places[pi], place[0])
				s += place[1] * places[pi]
			res = res[:-2] + "= %i\n" % s
		return res[:-1]

	def Tinv(self):
		"""
		Compute the T-invariants of the net.
		This might take a long time, so it is not possible by default.
		"""
		C = self.getIncidenceMatrix()
		C = Matrix.transpose(C)
		invs = Matrix.farkas(C)
		return invs

class Matrix:
	@staticmethod
	def transpose(matrix):
		"""
		Transposes a matrix (list of lists).
		"""
		m = len(matrix)
		if m == 0:
			return []
		n = len(matrix[0])
		new = [[0] * m for _ in range(n)]
		for mi in range(m):
			for ni in range(n):
				new[ni][mi] = matrix[mi][ni]
		return new

	@staticmethod
	def farkas(C):
		"""
		Computes the linear optimization of a matrix.
		Based on:
			http://www.lsv.fr/~schwoon/enseignement/verification/ws0910/nets2
		"""
		n = len(C)
		if n == 0:
			return []
		m = len(C[0])
		En = [[1 if x == y else 0 for x in range(n)] for y in range(n)]
		D = []
		for i in range(n):
			D.append(C[i] + En[i])
		for i in range(m):
			ta = []
			for d1 in D:
				for d2 in D:
					if d1[i] * d2[i] < 0:
						d = [abs(d2[i]) * d1[u] + abs(d1[i]) * d2[u] for u in range(m+n)]
						assert d[i] == 0
						dp = [x // gcd(d) for x in d]
						if dp not in D:
							D.append(dp)
							break
			for j in range(len(D)-1, -1, -1):
				if D[j][i] != 0:
					D.pop(j)
		for j in range(len(D)):
			for _ in range(m):
				D[j].pop(0)
		return list(set([tuple(d) for d in D]))



if __name__ == '__main__':

	import argparse
	import sys

	def check_positive(value):
		val = int(value)
		if val <= 0:
			raise argparse.ArgumentTypeError("Only strictly positive iteration counts are allowed.")
		return val

	def check_type(value):
		if "reachability".startswith(value.lower()):
			return "R"
		elif "coverability".startswith(value.lower()):
			return "C"
		raise argparse.ArgumentTypeError("Invalid type: %s. Expected prefix of 'reachability' or 'coverability'." % value.lower())

	parser = argparse.ArgumentParser(description="Generate the Reachability/Coverability graph of a Petri Net or find the P-Invariants.")
	parser.add_argument('input', help="The *.tapn file.")
	parser.add_argument('output', nargs='?', type=argparse.FileType('wb'), default=None, help="The output file for GraphViz. When omitted, the console is used instead.")
	parser.add_argument('type', type=check_type, help="The kind of graph to construct. Must be a prefix of 'reachability' or 'coverability'. Casing will be ignored.")
	parser.add_argument('-t', '--title', default=None, help="The title to display in the plot. When omitted, the type of the graph will be shown.")
	parser.add_argument('-s', '--start', default="box", help="The GraphViz shape to use for the start node. Defaults to 'box'.")
	parser.add_argument('-m', '--markings', action='store_false', help="Do not to print the marking place information.")
	parser.add_argument('-T', '--table', action='store_true', help="Store the markings in a table.csv file, instead of using the node labels.")
	parser.add_argument('-I', '--iterations', type=check_positive, default=0, help="The maximal amount of iterations to use. For Reachability, the default is 1000; "
																					"for Coverability, no limit is set by default.")
	parser.add_argument('-p', '--invariants', action='store_true', help="Print out the P-Invariant formulas for the net.")
	parser.add_argument('-g', '--graphviz', action='store_true', help="When used, the script outputs a (net.dot) graphviz file that represents the internal net. This can be used for checking inconsistencies between the TAPAAL visualization and how it is stored.")

	args = parser.parse_args()

	net = PetriNet(args.input)

	if args.graphviz:
		with open("net.dot", "wb") as file:
			file.write(net.graphviz().encode("utf-8"))

	if args.invariants:
		invs = net.Pinv().replace("\n", "\n\t")
		if invs != "":
			print("P-Invariants:")
			print(invs + "\n")
	if args.markings:
		print("The markings are given w.r.t. the following places:", [net.places[x][0] for x in net._mvec])
	gv = ""
	it = args.iterations
	title = args.title
	if args.type == "R":
		if it == 0:
			it = 1000
		if title is None:
			title = "Reachability Graph"
		gv = net.reachabilityGraph(title, args.start, it, args.table)
	else:
		if title is None:
			title = "Coverability Graph"
		gv = net.coverabilityGraph(title, args.start, it, args.table)
	if args.output is None:
		print(gv)
	else:
		args.output.write(gv.encode('utf-8'))
		args.output.close()
