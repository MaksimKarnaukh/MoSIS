"""Implementation of statechart b.
Generated by itemis CREATE code generator.
"""

import queue
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from yakindu.rx import Observable

class B:
	"""Implementation of the state machine B.
	"""

	class State:
		""" State Enum
		"""
		(
			main_region_outer,
			main_region_outer_r1inner,
			null_state
		) = range(3)
	
	
	def __init__(self):
		""" Declares all necessary variables including list of states, histories etc. 
		"""
		
		self.outer = None
		self.outer_observable = Observable()
		self.inner = None
		self.inner_observable = Observable()
		
		self.in_event_queue = queue.Queue()
		# enumeration of all states:
		self.__State = B.State
		self.__state_conf_vector_changed = None
		self.__state_vector = [None] * 1
		for __state_index in range(1):
			self.__state_vector[__state_index] = self.State.null_state
		
		# for timed statechart:
		self.timer_service = None
		self.__time_events = [None] * 2
		
		# initializations:
		self.__is_executing = False
	
	def is_active(self):
		"""Checks if the state machine is active.
		"""
		return self.__state_vector[0] is not self.__State.null_state
	
	def is_final(self):
		"""Checks if the statemachine is final.
		Always returns 'false' since this state machine can never become final.
		"""
		return False
			
	def is_state_active(self, state):
		"""Checks if the state is currently active.
		"""
		s = state
		if s == self.__State.main_region_outer:
			return (self.__state_vector[0] >= self.__State.main_region_outer)\
				and (self.__state_vector[0] <= self.__State.main_region_outer_r1inner)
		if s == self.__State.main_region_outer_r1inner:
			return self.__state_vector[0] == self.__State.main_region_outer_r1inner
		return False
		
	def time_elapsed(self, event_id):
		"""Add time events to in event queue
		"""
		if event_id in range(2):
			self.in_event_queue.put(lambda: self.raise_time_event(event_id))
			self.run_cycle()
	
	def raise_time_event(self, event_id):
		"""Raise timed events using the event_id.
		"""
		self.__time_events[event_id] = True
	
	def __execute_queued_event(self, func):
		func()
	
	def __get_next_event(self):
		if not self.in_event_queue.empty():
			return self.in_event_queue.get()
		return None
	
	def __entry_action_main_region_outer(self):
		"""Entry action for state 'Outer'..
		"""
		#Entry action for state 'Outer'.
		self.timer_service.set_timer(self, 0, (3 * 1000), False)
		
	def __entry_action_main_region_outer_r1_inner(self):
		"""Entry action for state 'Inner'..
		"""
		#Entry action for state 'Inner'.
		self.timer_service.set_timer(self, 1, (2 * 1000), False)
		
	def __exit_action_main_region_outer(self):
		"""Exit action for state 'Outer'..
		"""
		#Exit action for state 'Outer'.
		self.timer_service.unset_timer(self, 0)
		
	def __exit_action_main_region_outer_r1_inner(self):
		"""Exit action for state 'Inner'..
		"""
		#Exit action for state 'Inner'.
		self.timer_service.unset_timer(self, 1)
		
	def __enter_sequence_main_region_outer_default(self):
		"""'default' enter sequence for state Outer.
		"""
		#'default' enter sequence for state Outer
		self.__entry_action_main_region_outer()
		self.__enter_sequence_main_region_outer_r1_default()
		
	def __enter_sequence_main_region_outer_r1_inner_default(self):
		"""'default' enter sequence for state Inner.
		"""
		#'default' enter sequence for state Inner
		self.__entry_action_main_region_outer_r1_inner()
		self.__state_vector[0] = self.State.main_region_outer_r1inner
		self.__state_conf_vector_changed = True
		
	def __enter_sequence_main_region_default(self):
		"""'default' enter sequence for region main region.
		"""
		#'default' enter sequence for region main region
		self.__react_main_region__entry_default()
		
	def __enter_sequence_main_region_outer_r1_default(self):
		"""'default' enter sequence for region r1.
		"""
		#'default' enter sequence for region r1
		self.__react_main_region_outer_r1__entry_default()
		
	def __exit_sequence_main_region_outer(self):
		"""Default exit sequence for state Outer.
		"""
		#Default exit sequence for state Outer
		self.__exit_sequence_main_region_outer_r1()
		self.__exit_action_main_region_outer()
		
	def __exit_sequence_main_region_outer_r1_inner(self):
		"""Default exit sequence for state Inner.
		"""
		#Default exit sequence for state Inner
		self.__state_vector[0] = self.State.null_state
		self.__exit_action_main_region_outer_r1_inner()
		
	def __exit_sequence_main_region(self):
		"""Default exit sequence for region main region.
		"""
		#Default exit sequence for region main region
		state = self.__state_vector[0]
		if state == self.State.main_region_outer_r1inner:
			self.__exit_sequence_main_region_outer_r1_inner()
			self.__exit_action_main_region_outer()
		
	def __exit_sequence_main_region_outer_r1(self):
		"""Default exit sequence for region r1.
		"""
		#Default exit sequence for region r1
		state = self.__state_vector[0]
		if state == self.State.main_region_outer_r1inner:
			self.__exit_sequence_main_region_outer_r1_inner()
		
	def __react_main_region_outer_r1__entry_default(self):
		"""Default react sequence for initial entry .
		"""
		#Default react sequence for initial entry 
		self.__enter_sequence_main_region_outer_r1_inner_default()
		
	def __react_main_region__entry_default(self):
		"""Default react sequence for initial entry .
		"""
		#Default react sequence for initial entry 
		self.__enter_sequence_main_region_outer_default()
		
	def __react(self, transitioned_before):
		"""Implementation of __react function.
		"""
		#State machine reactions.
		return transitioned_before
	
	
	def __main_region_outer_react(self, transitioned_before):
		"""Implementation of __main_region_outer_react function.
		"""
		#The reactions of state Outer.
		transitioned_after = transitioned_before
		if transitioned_after < 0:
			if self.__time_events[0]:
				self.__exit_sequence_main_region_outer()
				self.outer_observable.next()
				self.__time_events[0] = False
				self.__enter_sequence_main_region_outer_default()
				self.__react(0)
				transitioned_after = 0
		#If no transition was taken
		if transitioned_after == transitioned_before:
			#then execute local reactions.
			transitioned_after = self.__react(transitioned_before)
		return transitioned_after
	
	
	def __main_region_outer_r1_inner_react(self, transitioned_before):
		"""Implementation of __main_region_outer_r1_inner_react function.
		"""
		#The reactions of state Inner.
		transitioned_after = transitioned_before
		if transitioned_after < 0:
			if self.__time_events[1]:
				self.__exit_sequence_main_region_outer_r1_inner()
				self.inner_observable.next()
				self.__time_events[1] = False
				self.__enter_sequence_main_region_outer_r1_inner_default()
				self.__main_region_outer_react(0)
				transitioned_after = 0
		#If no transition was taken
		if transitioned_after == transitioned_before:
			#then execute local reactions.
			transitioned_after = self.__main_region_outer_react(transitioned_before)
		return transitioned_after
	
	
	def __clear_in_events(self):
		"""Implementation of __clear_in_events function.
		"""
		self.__time_events[0] = False
		self.__time_events[1] = False
	
	
	def __micro_step(self):
		"""Implementation of __micro_step function.
		"""
		state = self.__state_vector[0]
		if state == self.State.main_region_outer_r1inner:
			self.__main_region_outer_r1_inner_react(-1)
	
	
	def run_cycle(self):
		"""Implementation of run_cycle function.
		"""
		#Performs a 'run to completion' step.
		if self.timer_service is None:
			raise ValueError('Timer service must be set.')
		
		if self.__is_executing:
			return
		self.__is_executing = True
		next_event = self.__get_next_event()
		if next_event is not None:
			self.__execute_queued_event(next_event)
		condition_0 = True
		while condition_0:
			self.__micro_step()
			self.__clear_in_events()
			condition_0 = False
			next_event = self.__get_next_event()
			if next_event is not None:
				self.__execute_queued_event(next_event)
				condition_0 = True
		self.__is_executing = False
	
	
	def enter(self):
		"""Implementation of enter function.
		"""
		#Activates the state machine.
		if self.timer_service is None:
			raise ValueError('Timer service must be set.')
		
		if self.__is_executing:
			return
		self.__is_executing = True
		#Default enter sequence for statechart B
		self.__enter_sequence_main_region_default()
		self.__is_executing = False
	
	
	def exit(self):
		"""Implementation of exit function.
		"""
		#Deactivates the state machine.
		if self.__is_executing:
			return
		self.__is_executing = True
		#Default exit sequence for statechart B
		self.__exit_sequence_main_region()
		self.__is_executing = False
	
	
	def trigger_without_event(self):
		"""Implementation of triggerWithoutEvent function.
		"""
		self.run_cycle()
	
