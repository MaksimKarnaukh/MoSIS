"""
This visual DEVS plotter is based on Bill Song's DEVS Visual Modeling and Simulation Environment,
however, it has been ported to the PythonPDEVS logic.

See Also:
	`http://msdl.uantwerpen.be/people/bill/devsenv/summerpresentation.pdf`_
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import xml.etree.ElementTree as ET

class Window:
	def __init__(self):
		self.root = tk.Tk()

		self.filename = fd.askopenfilename(parent=self.root, title="Open an XML trace file",
		                                   initialdir="/", filetypes=[("XML files", "*.xml")])
		if not self.filename:
			self.root.quit()

		self.root.title("DEVS Plotting Environment - %s" % self.filename)

		self.frame = ttk.Frame(self.root, padding=10)
		self.frame.pack(fill=tk.BOTH, expand=True)

		self.toolbar = ttk.Frame(self.frame)
		self.toolbar.pack(side=tk.TOP, fill=tk.X)

		self.container = ttk.Frame(self.frame)
		self.container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
		self.trees = ttk.Frame(self.container)
		self.trees.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.time = 0.0
		self.button_first = ttk.Button(self.toolbar, text="<<", command=self.to_first)
		self.button_first.pack(side=tk.LEFT)
		self.button_prev = ttk.Button(self.toolbar, text="<", command=self.to_prev)
		self.button_prev.pack(side=tk.LEFT)
		self.button_next = ttk.Button(self.toolbar, text=">", command=self.to_next)
		self.button_next.pack(side=tk.LEFT)
		self.button_last = ttk.Button(self.toolbar, text=">>", command=self.to_last)
		self.button_last.pack(side=tk.LEFT)
		# sep = ttk.Separator(self.toolbar)
		# sep.pack(side=tk.LEFT)
		lbl_window = ttk.Label(self.toolbar, text="   Window Size: ")
		lbl_window.pack(side=tk.LEFT)
		self.window_size = ttk.Spinbox(self.toolbar, from_=0, to=50)
		self.window_size.set(10)
		self.window_size.pack(side=tk.LEFT)

		self.mtree = ttk.Treeview(self.trees, selectmode="browse", columns=["path"], displaycolumns=[])
		self.mtree.heading('#0', text="Select a Model:", anchor=tk.W)
		self.mtree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
		self.mtree.bind("<<TreeviewSelect>>", self.select_in_mtree)

		self.stree = ttk.Treeview(self.trees, selectmode="browse", columns=["path"], displaycolumns=[])
		self.stree.heading('#0', text="Plottable Attributes:", anchor=tk.W)
		self.stree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
		self.stree.pack_forget()
		self.stree.bind("<<TreeviewSelect>>", self.select_in_stree)

		# load in the model
		self.trace = {}
		self.parse_trace_file()
		self._build_model_mtree()

		self.figure = plt.figure(dpi=100)
		# self.figure.tight_layout()
		self.axis = self.figure.add_subplot(111)
		self.axis.set_xlabel("time")
		self.axis.set_ylim((0, 1))
		self.canvas = FigureCanvasTkAgg(self.figure, master=self.container)
		self.canvas.draw()
		self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		self.__cursor, = self.axis.plot([0, 0], [0, 0], '--', c='b', alpha=0.7)
		self.__line, = self.axis.plot([], [], c='r')
		self.__dots, = self.axis.plot([], [], 'o', c='g')
		self.__ani = animation.FuncAnimation(self.figure, lambda _: self.update(), interval=100)

		self.active_model = ""
		self.active_state = ""

		self.output = tk.Text(self.frame, height=7)
		self.output.pack(side=tk.BOTTOM, fill=tk.X, expand=True)
		self.output.pack_forget()

		self.root.mainloop()

	def to_first(self):
		if self.active_model != "" and self.active_state != "":
			self.time = 0

	def to_prev(self):
		if self.active_model != "" and self.active_state != "":
			for ev in reversed(self.trace[self.active_model]):
				if ev["time"] < self.time:
					self.time = ev["time"]
					break

	def to_next(self):
		if self.active_model != "" and self.active_state != "":
			for ev in self.trace[self.active_model]:
				if ev["time"] > self.time:
					self.time = ev["time"]
					break

	def to_last(self):
		if self.active_model != "" and self.active_state != "":
			self.time = self.trace[self.active_model][-1]["time"]

	def get_window(self):
		return int(self.window_size.get())

	def parse_trace_file(self):
		tree = ET.parse(self.filename)
		root = tree.getroot()

		for item in root.findall('event'):
			model = item.find("model").text
			data = {}
			data["time"] = float(item.find("time").text)
			data["kind"] = item.find("kind").text
			data["state"] = self._parse_attributes(item.find("state"))
			if data["kind"] == "IN":
				port = item.find("port")
				data["port"] = {
					"name": port.get("name"),
					"category": port.get("category"),       # I or O (in or out)
					"message": port.find("message").text
				}

			self.trace.setdefault(model, []).append(data)

	def _parse_attributes(self, node):
		res = {}
		for attr in node.findall('attribute'):
			name = attr.find("name").text
			valueN = attr.find("value")
			if len(valueN.findall("attribute")) > 0:
				res[name] = self._parse_attributes(valueN)
			else:
				res[name] = valueN.text
		return res

	def _build_model_mtree(self):
		ix = 0
		tree_ids = {}
		for model in self.trace:
			lst = model.split(".")
			for mix in range(len(lst)):
				parent = ".".join(lst[:mix])
				path = ".".join(lst[:mix + 1])
				if path not in tree_ids:
					self.mtree.insert(tree_ids.get(parent, ''), tk.END, ix, text=lst[mix], open=True, values=[path])
					tree_ids[path] = ix
					ix += 1

	def _build_model_stree(self, model):
		self.stree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
		if len(self.stree.get_children()) > 0:
			self.stree.delete(self.stree.get_children())
		event_list = self.trace[model]
		state = {}
		for evt in event_list:
			state.update(evt["state"])
		self._build_stree(state)

	def _build_stree(self, state, pid='', parent=""):
		uid = pid
		if pid == '':
			uid = 0
		uid += 1
		for s, v in state.items():
			path = s
			if parent != "":
				path = parent + "." + path
			self.stree.insert(pid, tk.END, uid, text=s, open=True, values=[path])
			if isinstance(v, dict):
				self._build_stree(v, uid, path)
				uid += len(v)
			else:
				uid += 1

	def update(self):
		if self.active_model != "" and self.active_state != "":
			self.create_plot_for_active_model_state()
			self.output.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
			self.output.delete("1.0", tk.END)
			tam = self.trace[self.active_model]
			for ix, ev in enumerate(tam):
				if ev["time"] == self.time:
					state = ev["state"]
					for p in self.active_state.split("."):
						state = state[p]
					self.output.insert(tk.END, "TIME: %.4f\nSTATE: %s\n" % (self.time, str(state)))
					if ev["kind"] == "IN":
						self.output.insert(tk.END, 'Internal Transition:\n  Port: %s\n  Output: %s\n  Time Next: %.4f' %
						                   (ev["port"]["name"], ev["port"]["message"], tam[ix + 1]["time"] if ix + 1 < len(tam) else "N/A"))
					else:
						self.output.insert(tk.END, 'External Transition')
					break

		else:
			self.clear_plot()

	def select_in_mtree(self, event):
		tree = event.widget
		selection = [tree.item(item)["values"][0] for item in tree.selection() if len(tree.get_children(item)) == 0]
		if len(selection) == 1:
			self.active_model = selection[0]
			self._build_model_stree(self.active_model)
		else:
			self.active_model = ""
			self.stree.pack_forget()
		self.active_state = ""

	def select_in_stree(self, event):
		tree = event.widget
		selection = [tree.item(item)["values"][0] for item in tree.selection() if len(tree.get_children(item)) == 0]
		if len(selection) == 1:
			self.active_state = selection[0]

	def clear_plot(self):
		self.__line.set_data([], [])
		self.__dots.set_data([], [])
		self.axis.set_title("")
		self.axis.set_xlim((0, 1))
		self.axis.set_ylim((-0.5, 0.5))
		self.axis.set_yticks([])
		self.axis.set_yticklabels([])

	def create_plot_for_active_model_state(self):
		event_list = self.trace[self.active_model]
		path = self.active_state.split(".")
		in_times = []
		in_evts = []
		states = []
		for ev in event_list:
			state = ev["state"]
			for p in path:
				state = state[p]
			states.append(state)
			if ev["kind"] == "IN":
				in_times.append(ev["time"])
				in_evts.append(state)

		state_sets = list(sorted(set(states)))
		times = [x["time"] for x in event_list]
		values = [state_sets.index(x) for x in states]

		ts, vs = [], []
		for time in times:
			ts.append(time)
			ts.append(time)
		for val in values:
			vs.append(val)
			vs.append(val)
		ts.pop(0)
		vs.pop()

		self.axis.set_title("%s: %s" % (self.active_model, self.active_state))

		mid = self.time
		ws = self.get_window()
		lower = max(times[0], mid - ws/2)
		upper = lower + ws
		self.axis.set_xlim((lower, upper))
		self.axis.set_ylim((-0.5, len(state_sets) - 0.5))
		self.axis.set_yticks(range(len(state_sets)))
		self.axis.set_yticklabels(state_sets)

		self.__cursor.set_data([mid, mid], [-0.5, len(state_sets) - 0.5])
		self.__line.set_data(ts, vs)
		self.__dots.set_data(in_times, [state_sets.index(x) for x in in_evts])



if __name__ == '__main__':
	Window()