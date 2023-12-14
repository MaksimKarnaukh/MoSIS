"""Implementation of statechart statechart.
Generated by itemis CREATE code generator.
"""

import queue
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from yakindu.rx import Observable

class Statechart:
	"""Implementation of the state machine Statechart.
	"""

	class State:
		""" State Enum
		"""
		(
			main_region_orthogonal,
			main_region_orthogonal_toggle_mode_buttonnot_pressed,
			main_region_orthogonal_toggle_mode_buttonpressed,
			main_region_orthogonal_traffic_light_modesnormal,
			main_region_orthogonal_traffic_light_modesnormal_r1red,
			main_region_orthogonal_traffic_light_modesnormal_r1yellow,
			main_region_orthogonal_traffic_light_modesnormal_r1smart_green,
			main_region_orthogonal_traffic_light_modesnormal_r1smart_green_r1green,
			main_region_orthogonal_traffic_light_modesinterrupted,
			main_region_orthogonal_traffic_light_modesinterrupted_r1yellow,
			main_region_orthogonal_traffic_light_modesinterrupted_r1allblack,
			null_state
		) = range(12)
	
	
	def __init__(self):
		""" Declares all necessary variables including list of states, histories etc. 
		"""
		
		self.button_pressed = None
		self.button_released = None
		self.car_detected = None
		self.set_led = None
		self.set_led_value = None
		self.set_led_observable = Observable()
		self.set_red = None
		self.set_red_value = None
		self.set_red_observable = Observable()
		self.set_yellow = None
		self.set_yellow_value = None
		self.set_yellow_observable = Observable()
		self.set_green = None
		self.set_green_value = None
		self.set_green_observable = Observable()
		
		self.__internal_event_queue = queue.Queue()
		self.in_event_queue = queue.Queue()
		self.police_interrupt = None
		self.local_set_led = None
		self.local_set_led_value = None
		
		# enumeration of all states:
		self.__State = Statechart.State
		self.__state_conf_vector_changed = None
		self.__state_vector = [None] * 2
		for __state_index in range(2):
			self.__state_vector[__state_index] = self.State.null_state
		
		# for timed statechart:
		self.timer_service = None
		self.__time_events = [None] * 7
		
		# initializations:
		self.__is_executing = False
		self.__state_conf_vector_position = None
	
	def is_active(self):
		"""Checks if the state machine is active.
		"""
		return self.__state_vector[0] is not self.__State.null_state or self.__state_vector[1] is not self.__State.null_state
	
	def is_final(self):
		"""Checks if the statemachine is final.
		Always returns 'false' since this state machine can never become final.
		"""
		return False
			
	def is_state_active(self, state):
		"""Checks if the state is currently active.
		"""
		s = state
		if s == self.__State.main_region_orthogonal:
			return (self.__state_vector[0] >= self.__State.main_region_orthogonal)\
				and (self.__state_vector[0] <= self.__State.main_region_orthogonal_traffic_light_modesinterrupted_r1allblack)
		if s == self.__State.main_region_orthogonal_toggle_mode_buttonnot_pressed:
			return self.__state_vector[0] == self.__State.main_region_orthogonal_toggle_mode_buttonnot_pressed
		if s == self.__State.main_region_orthogonal_toggle_mode_buttonpressed:
			return self.__state_vector[0] == self.__State.main_region_orthogonal_toggle_mode_buttonpressed
		if s == self.__State.main_region_orthogonal_traffic_light_modesnormal:
			return (self.__state_vector[1] >= self.__State.main_region_orthogonal_traffic_light_modesnormal)\
				and (self.__state_vector[1] <= self.__State.main_region_orthogonal_traffic_light_modesnormal_r1smart_green_r1green)
		if s == self.__State.main_region_orthogonal_traffic_light_modesnormal_r1red:
			return self.__state_vector[1] == self.__State.main_region_orthogonal_traffic_light_modesnormal_r1red
		if s == self.__State.main_region_orthogonal_traffic_light_modesnormal_r1yellow:
			return self.__state_vector[1] == self.__State.main_region_orthogonal_traffic_light_modesnormal_r1yellow
		if s == self.__State.main_region_orthogonal_traffic_light_modesnormal_r1smart_green:
			return (self.__state_vector[1] >= self.__State.main_region_orthogonal_traffic_light_modesnormal_r1smart_green)\
				and (self.__state_vector[1] <= self.__State.main_region_orthogonal_traffic_light_modesnormal_r1smart_green_r1green)
		if s == self.__State.main_region_orthogonal_traffic_light_modesnormal_r1smart_green_r1green:
			return self.__state_vector[1] == self.__State.main_region_orthogonal_traffic_light_modesnormal_r1smart_green_r1green
		if s == self.__State.main_region_orthogonal_traffic_light_modesinterrupted:
			return (self.__state_vector[1] >= self.__State.main_region_orthogonal_traffic_light_modesinterrupted)\
				and (self.__state_vector[1] <= self.__State.main_region_orthogonal_traffic_light_modesinterrupted_r1allblack)
		if s == self.__State.main_region_orthogonal_traffic_light_modesinterrupted_r1yellow:
			return self.__state_vector[1] == self.__State.main_region_orthogonal_traffic_light_modesinterrupted_r1yellow
		if s == self.__State.main_region_orthogonal_traffic_light_modesinterrupted_r1allblack:
			return self.__state_vector[1] == self.__State.main_region_orthogonal_traffic_light_modesinterrupted_r1allblack
		return False
		
	def time_elapsed(self, event_id):
		"""Add time events to in event queue
		"""
		if event_id in range(7):
			self.in_event_queue.put(lambda: self.raise_time_event(event_id))
			self.run_cycle()
	
	def raise_time_event(self, event_id):
		"""Raise timed events using the event_id.
		"""
		self.__time_events[event_id] = True
	
	def __execute_queued_event(self, func):
		func()
	
	def __get_next_event(self):
		if not self.__internal_event_queue.empty():
			return self.__internal_event_queue.get()
		if not self.in_event_queue.empty():
			return self.in_event_queue.get()
		return None
	
	
	def raise_police_interrupt(self):
		"""Raise method for event police_interrupt.
		"""
		self.__internal_event_queue.put(self.__raise_police_interrupt_call)
	
	def __raise_police_interrupt_call(self):
		"""Raise callback for event police_interrupt.
		"""
		self.police_interrupt = True
	
	def raise_local_set_led(self, value):
		"""Raise method for event local_set_led.
		"""
		self.__internal_event_queue.put(lambda: self.__raise_local_set_led_call(value))
	
	def __raise_local_set_led_call(self, value):
		"""Raise callback for event local_set_led.
		"""
		self.local_set_led = True
		self.local_set_led_value = value
	
	def raise_button_pressed(self):
		"""Raise method for event button_pressed.
		"""
		self.in_event_queue.put(self.__raise_button_pressed_call)
		self.run_cycle()
	
	def __raise_button_pressed_call(self):
		"""Raise callback for event button_pressed.
		"""
		self.button_pressed = True
	
	def raise_button_released(self):
		"""Raise method for event button_released.
		"""
		self.in_event_queue.put(self.__raise_button_released_call)
		self.run_cycle()
	
	def __raise_button_released_call(self):
		"""Raise callback for event button_released.
		"""
		self.button_released = True
	
	def raise_car_detected(self):
		"""Raise method for event car_detected.
		"""
		self.in_event_queue.put(self.__raise_car_detected_call)
		self.run_cycle()
	
	def __raise_car_detected_call(self):
		"""Raise callback for event car_detected.
		"""
		self.car_detected = True
	
	def __entry_action_main_region_orthogonal_toggle_mode_button_pressed(self):
		"""Entry action for state 'pressed'..
		"""
		#Entry action for state 'pressed'.
		self.timer_service.set_timer(self, 0, (2 * 1000), False)
		
	def __entry_action_main_region_orthogonal_traffic_light_modes_normal_r1_red(self):
		"""Entry action for state 'red'..
		"""
		#Entry action for state 'red'.
		self.timer_service.set_timer(self, 1, (2 * 1000), False)
		self.set_red_observable.next(True)
		
	def __entry_action_main_region_orthogonal_traffic_light_modes_normal_r1_yellow(self):
		"""Entry action for state 'yellow'..
		"""
		#Entry action for state 'yellow'.
		self.timer_service.set_timer(self, 2, (1 * 1000), False)
		self.set_yellow_observable.next(True)
		
	def __entry_action_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green(self):
		"""Entry action for state 'smart green'..
		"""
		#Entry action for state 'smart green'.
		self.timer_service.set_timer(self, 3, (5 * 1000), False)
		self.set_green_observable.next(True)
		
	def __entry_action_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1_green(self):
		"""Entry action for state 'green'..
		"""
		#Entry action for state 'green'.
		self.timer_service.set_timer(self, 4, (2 * 1000), False)
		
	def __entry_action_main_region_orthogonal_traffic_light_modes_interrupted_r1_yellow(self):
		"""Entry action for state 'yellow'..
		"""
		#Entry action for state 'yellow'.
		self.timer_service.set_timer(self, 5, 500, False)
		self.set_yellow_observable.next(True)
		
	def __entry_action_main_region_orthogonal_traffic_light_modes_interrupted_r1_allblack(self):
		"""Entry action for state 'allblack'..
		"""
		#Entry action for state 'allblack'.
		self.timer_service.set_timer(self, 6, 500, False)
		
	def __exit_action_main_region_orthogonal_toggle_mode_button_pressed(self):
		"""Exit action for state 'pressed'..
		"""
		#Exit action for state 'pressed'.
		self.timer_service.unset_timer(self, 0)
		
	def __exit_action_main_region_orthogonal_traffic_light_modes_normal_r1_red(self):
		"""Exit action for state 'red'..
		"""
		#Exit action for state 'red'.
		self.timer_service.unset_timer(self, 1)
		self.set_red_observable.next(False)
		
	def __exit_action_main_region_orthogonal_traffic_light_modes_normal_r1_yellow(self):
		"""Exit action for state 'yellow'..
		"""
		#Exit action for state 'yellow'.
		self.timer_service.unset_timer(self, 2)
		self.set_yellow_observable.next(False)
		
	def __exit_action_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green(self):
		"""Exit action for state 'smart green'..
		"""
		#Exit action for state 'smart green'.
		self.timer_service.unset_timer(self, 3)
		self.set_green_observable.next(False)
		
	def __exit_action_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1_green(self):
		"""Exit action for state 'green'..
		"""
		#Exit action for state 'green'.
		self.timer_service.unset_timer(self, 4)
		
	def __exit_action_main_region_orthogonal_traffic_light_modes_interrupted_r1_yellow(self):
		"""Exit action for state 'yellow'..
		"""
		#Exit action for state 'yellow'.
		self.timer_service.unset_timer(self, 5)
		self.set_yellow_observable.next(False)
		
	def __exit_action_main_region_orthogonal_traffic_light_modes_interrupted_r1_allblack(self):
		"""Exit action for state 'allblack'..
		"""
		#Exit action for state 'allblack'.
		self.timer_service.unset_timer(self, 6)
		
	def __enter_sequence_main_region_orthogonal_default(self):
		"""'default' enter sequence for state orthogonal.
		"""
		#'default' enter sequence for state orthogonal
		self.__enter_sequence_main_region_orthogonal_toggle_mode_button_default()
		self.__enter_sequence_main_region_orthogonal_traffic_light_modes_default()
		
	def __enter_sequence_main_region_orthogonal_toggle_mode_button_not_pressed_default(self):
		"""'default' enter sequence for state not pressed.
		"""
		#'default' enter sequence for state not pressed
		self.__state_vector[0] = self.State.main_region_orthogonal_toggle_mode_buttonnot_pressed
		self.__state_conf_vector_position = 0
		self.__state_conf_vector_changed = True
		
	def __enter_sequence_main_region_orthogonal_toggle_mode_button_pressed_default(self):
		"""'default' enter sequence for state pressed.
		"""
		#'default' enter sequence for state pressed
		self.__entry_action_main_region_orthogonal_toggle_mode_button_pressed()
		self.__state_vector[0] = self.State.main_region_orthogonal_toggle_mode_buttonpressed
		self.__state_conf_vector_position = 0
		self.__state_conf_vector_changed = True
		
	def __enter_sequence_main_region_orthogonal_traffic_light_modes_normal_default(self):
		"""'default' enter sequence for state normal.
		"""
		#'default' enter sequence for state normal
		self.__enter_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_default()
		
	def __enter_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_red_default(self):
		"""'default' enter sequence for state red.
		"""
		#'default' enter sequence for state red
		self.__entry_action_main_region_orthogonal_traffic_light_modes_normal_r1_red()
		self.__state_vector[1] = self.State.main_region_orthogonal_traffic_light_modesnormal_r1red
		self.__state_conf_vector_position = 1
		self.__state_conf_vector_changed = True
		
	def __enter_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_yellow_default(self):
		"""'default' enter sequence for state yellow.
		"""
		#'default' enter sequence for state yellow
		self.__entry_action_main_region_orthogonal_traffic_light_modes_normal_r1_yellow()
		self.__state_vector[1] = self.State.main_region_orthogonal_traffic_light_modesnormal_r1yellow
		self.__state_conf_vector_position = 1
		self.__state_conf_vector_changed = True
		
	def __enter_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1_green_default(self):
		"""'default' enter sequence for state green.
		"""
		#'default' enter sequence for state green
		self.__entry_action_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1_green()
		self.__state_vector[1] = self.State.main_region_orthogonal_traffic_light_modesnormal_r1smart_green_r1green
		self.__state_conf_vector_position = 1
		self.__state_conf_vector_changed = True
		
	def __enter_sequence_main_region_orthogonal_traffic_light_modes_interrupted_default(self):
		"""'default' enter sequence for state interrupted.
		"""
		#'default' enter sequence for state interrupted
		self.__enter_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1_default()
		
	def __enter_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1_yellow_default(self):
		"""'default' enter sequence for state yellow.
		"""
		#'default' enter sequence for state yellow
		self.__entry_action_main_region_orthogonal_traffic_light_modes_interrupted_r1_yellow()
		self.__state_vector[1] = self.State.main_region_orthogonal_traffic_light_modesinterrupted_r1yellow
		self.__state_conf_vector_position = 1
		self.__state_conf_vector_changed = True
		
	def __enter_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1_allblack_default(self):
		"""'default' enter sequence for state allblack.
		"""
		#'default' enter sequence for state allblack
		self.__entry_action_main_region_orthogonal_traffic_light_modes_interrupted_r1_allblack()
		self.__state_vector[1] = self.State.main_region_orthogonal_traffic_light_modesinterrupted_r1allblack
		self.__state_conf_vector_position = 1
		self.__state_conf_vector_changed = True
		
	def __enter_sequence_main_region_default(self):
		"""'default' enter sequence for region main region.
		"""
		#'default' enter sequence for region main region
		self.__react_main_region__entry_default()
		
	def __enter_sequence_main_region_orthogonal_toggle_mode_button_default(self):
		"""'default' enter sequence for region TOGGLE MODE BUTTON.
		"""
		#'default' enter sequence for region TOGGLE MODE BUTTON
		self.__react_main_region_orthogonal_toggle_mode_button__entry_default()
		
	def __enter_sequence_main_region_orthogonal_traffic_light_modes_default(self):
		"""'default' enter sequence for region TRAFFIC LIGHT MODES.
		"""
		#'default' enter sequence for region TRAFFIC LIGHT MODES
		self.__react_main_region_orthogonal_traffic_light_modes__entry_default()
		
	def __enter_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_default(self):
		"""'default' enter sequence for region r1.
		"""
		#'default' enter sequence for region r1
		self.__react_main_region_orthogonal_traffic_light_modes_normal_r1__entry_default()
		
	def __enter_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1_default(self):
		"""'default' enter sequence for region r1.
		"""
		#'default' enter sequence for region r1
		self.__react_main_region_orthogonal_traffic_light_modes_interrupted_r1__entry_default()
		
	def __exit_sequence_main_region_orthogonal_toggle_mode_button_not_pressed(self):
		"""Default exit sequence for state not pressed.
		"""
		#Default exit sequence for state not pressed
		self.__state_vector[0] = self.State.null_state
		self.__state_conf_vector_position = 0
		
	def __exit_sequence_main_region_orthogonal_toggle_mode_button_pressed(self):
		"""Default exit sequence for state pressed.
		"""
		#Default exit sequence for state pressed
		self.__state_vector[0] = self.State.null_state
		self.__state_conf_vector_position = 0
		self.__exit_action_main_region_orthogonal_toggle_mode_button_pressed()
		
	def __exit_sequence_main_region_orthogonal_traffic_light_modes_normal(self):
		"""Default exit sequence for state normal.
		"""
		#Default exit sequence for state normal
		self.__exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1()
		
	def __exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_red(self):
		"""Default exit sequence for state red.
		"""
		#Default exit sequence for state red
		self.__state_vector[1] = self.State.null_state
		self.__state_conf_vector_position = 1
		self.__exit_action_main_region_orthogonal_traffic_light_modes_normal_r1_red()
		
	def __exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_yellow(self):
		"""Default exit sequence for state yellow.
		"""
		#Default exit sequence for state yellow
		self.__state_vector[1] = self.State.null_state
		self.__state_conf_vector_position = 1
		self.__exit_action_main_region_orthogonal_traffic_light_modes_normal_r1_yellow()
		
	def __exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green(self):
		"""Default exit sequence for state smart green.
		"""
		#Default exit sequence for state smart green
		self.__exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1()
		self.__exit_action_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green()
		
	def __exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1_green(self):
		"""Default exit sequence for state green.
		"""
		#Default exit sequence for state green
		self.__state_vector[1] = self.State.null_state
		self.__state_conf_vector_position = 1
		self.__exit_action_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1_green()
		
	def __exit_sequence_main_region_orthogonal_traffic_light_modes_interrupted(self):
		"""Default exit sequence for state interrupted.
		"""
		#Default exit sequence for state interrupted
		self.__exit_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1()
		
	def __exit_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1_yellow(self):
		"""Default exit sequence for state yellow.
		"""
		#Default exit sequence for state yellow
		self.__state_vector[1] = self.State.null_state
		self.__state_conf_vector_position = 1
		self.__exit_action_main_region_orthogonal_traffic_light_modes_interrupted_r1_yellow()
		
	def __exit_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1_allblack(self):
		"""Default exit sequence for state allblack.
		"""
		#Default exit sequence for state allblack
		self.__state_vector[1] = self.State.null_state
		self.__state_conf_vector_position = 1
		self.__exit_action_main_region_orthogonal_traffic_light_modes_interrupted_r1_allblack()
		
	def __exit_sequence_main_region(self):
		"""Default exit sequence for region main region.
		"""
		#Default exit sequence for region main region
		state = self.__state_vector[0]
		if state == self.State.main_region_orthogonal_toggle_mode_buttonnot_pressed:
			self.__exit_sequence_main_region_orthogonal_toggle_mode_button_not_pressed()
		elif state == self.State.main_region_orthogonal_toggle_mode_buttonpressed:
			self.__exit_sequence_main_region_orthogonal_toggle_mode_button_pressed()
		state = self.__state_vector[1]
		if state == self.State.main_region_orthogonal_traffic_light_modesnormal_r1red:
			self.__exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_red()
		elif state == self.State.main_region_orthogonal_traffic_light_modesnormal_r1yellow:
			self.__exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_yellow()
		elif state == self.State.main_region_orthogonal_traffic_light_modesnormal_r1smart_green_r1green:
			self.__exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1_green()
			self.__exit_action_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green()
		elif state == self.State.main_region_orthogonal_traffic_light_modesinterrupted_r1yellow:
			self.__exit_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1_yellow()
		elif state == self.State.main_region_orthogonal_traffic_light_modesinterrupted_r1allblack:
			self.__exit_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1_allblack()
		
	def __exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1(self):
		"""Default exit sequence for region r1.
		"""
		#Default exit sequence for region r1
		state = self.__state_vector[1]
		if state == self.State.main_region_orthogonal_traffic_light_modesnormal_r1red:
			self.__exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_red()
		elif state == self.State.main_region_orthogonal_traffic_light_modesnormal_r1yellow:
			self.__exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_yellow()
		elif state == self.State.main_region_orthogonal_traffic_light_modesnormal_r1smart_green_r1green:
			self.__exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1_green()
			self.__exit_action_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green()
		
	def __exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1(self):
		"""Default exit sequence for region r1.
		"""
		#Default exit sequence for region r1
		state = self.__state_vector[1]
		if state == self.State.main_region_orthogonal_traffic_light_modesnormal_r1smart_green_r1green:
			self.__exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1_green()
		
	def __exit_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1(self):
		"""Default exit sequence for region r1.
		"""
		#Default exit sequence for region r1
		state = self.__state_vector[1]
		if state == self.State.main_region_orthogonal_traffic_light_modesinterrupted_r1yellow:
			self.__exit_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1_yellow()
		elif state == self.State.main_region_orthogonal_traffic_light_modesinterrupted_r1allblack:
			self.__exit_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1_allblack()
		
	def __react_main_region_orthogonal_toggle_mode_button__entry_default(self):
		"""Default react sequence for initial entry .
		"""
		#Default react sequence for initial entry 
		self.__enter_sequence_main_region_orthogonal_toggle_mode_button_not_pressed_default()
		
	def __react_main_region_orthogonal_traffic_light_modes_normal_r1__entry_default(self):
		"""Default react sequence for initial entry .
		"""
		#Default react sequence for initial entry 
		self.__enter_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_red_default()
		
	def __react_main_region_orthogonal_traffic_light_modes_interrupted_r1__entry_default(self):
		"""Default react sequence for initial entry .
		"""
		#Default react sequence for initial entry 
		self.__enter_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1_yellow_default()
		
	def __react_main_region_orthogonal_traffic_light_modes__entry_default(self):
		"""Default react sequence for initial entry .
		"""
		#Default react sequence for initial entry 
		self.__enter_sequence_main_region_orthogonal_traffic_light_modes_normal_default()
		
	def __react_main_region__entry_default(self):
		"""Default react sequence for initial entry .
		"""
		#Default react sequence for initial entry 
		self.__enter_sequence_main_region_orthogonal_default()
		
	def __react(self, transitioned_before):
		"""Implementation of __react function.
		"""
		#State machine reactions.
		return transitioned_before
	
	
	def __main_region_orthogonal_react(self, transitioned_before):
		"""Implementation of __main_region_orthogonal_react function.
		"""
		#The reactions of state orthogonal.
		transitioned_after = transitioned_before
		#Always execute local reactions.
		transitioned_after = self.__react(transitioned_before)
		return transitioned_after
	
	
	def __main_region_orthogonal_toggle_mode_button_not_pressed_react(self, transitioned_before):
		"""Implementation of __main_region_orthogonal_toggle_mode_button_not_pressed_react function.
		"""
		#The reactions of state not pressed.
		transitioned_after = transitioned_before
		if transitioned_after < 0:
			if self.button_pressed:
				self.__exit_sequence_main_region_orthogonal_toggle_mode_button_not_pressed()
				self.__enter_sequence_main_region_orthogonal_toggle_mode_button_pressed_default()
				transitioned_after = 0
		return transitioned_after
	
	
	def __main_region_orthogonal_toggle_mode_button_pressed_react(self, transitioned_before):
		"""Implementation of __main_region_orthogonal_toggle_mode_button_pressed_react function.
		"""
		#The reactions of state pressed.
		transitioned_after = transitioned_before
		if transitioned_after < 0:
			if self.button_released:
				self.__exit_sequence_main_region_orthogonal_toggle_mode_button_pressed()
				self.set_led_observable.next(not self.local_set_led_value)
				self.raise_local_set_led(not self.local_set_led_value)
				self.__enter_sequence_main_region_orthogonal_toggle_mode_button_not_pressed_default()
				transitioned_after = 0
			elif self.__time_events[0]:
				self.__exit_sequence_main_region_orthogonal_toggle_mode_button_pressed()
				self.raise_police_interrupt()
				self.__time_events[0] = False
				self.__enter_sequence_main_region_orthogonal_toggle_mode_button_not_pressed_default()
				transitioned_after = 0
		return transitioned_after
	
	
	def __main_region_orthogonal_traffic_light_modes_normal_react(self, transitioned_before):
		"""Implementation of __main_region_orthogonal_traffic_light_modes_normal_react function.
		"""
		#The reactions of state normal.
		transitioned_after = transitioned_before
		if transitioned_after < 1:
			if self.police_interrupt:
				self.__exit_sequence_main_region_orthogonal_traffic_light_modes_normal()
				self.__enter_sequence_main_region_orthogonal_traffic_light_modes_interrupted_default()
				self.__main_region_orthogonal_react(0)
				transitioned_after = 1
		#If no transition was taken
		if transitioned_after == transitioned_before:
			#then execute local reactions.
			transitioned_after = self.__main_region_orthogonal_react(transitioned_before)
		return transitioned_after
	
	
	def __main_region_orthogonal_traffic_light_modes_normal_r1_red_react(self, transitioned_before):
		"""Implementation of __main_region_orthogonal_traffic_light_modes_normal_r1_red_react function.
		"""
		#The reactions of state red.
		transitioned_after = transitioned_before
		if transitioned_after < 1:
			if self.__time_events[1]:
				self.__exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_red()
				self.__time_events[1] = False
				self.__entry_action_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green()
				self.__enter_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1_green_default()
				self.__main_region_orthogonal_traffic_light_modes_normal_react(1)
				transitioned_after = 1
		#If no transition was taken
		if transitioned_after == transitioned_before:
			#then execute local reactions.
			transitioned_after = self.__main_region_orthogonal_traffic_light_modes_normal_react(transitioned_before)
		return transitioned_after
	
	
	def __main_region_orthogonal_traffic_light_modes_normal_r1_yellow_react(self, transitioned_before):
		"""Implementation of __main_region_orthogonal_traffic_light_modes_normal_r1_yellow_react function.
		"""
		#The reactions of state yellow.
		transitioned_after = transitioned_before
		if transitioned_after < 1:
			if self.__time_events[2]:
				self.__exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_yellow()
				self.__time_events[2] = False
				self.__enter_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_red_default()
				self.__main_region_orthogonal_traffic_light_modes_normal_react(1)
				transitioned_after = 1
		#If no transition was taken
		if transitioned_after == transitioned_before:
			#then execute local reactions.
			transitioned_after = self.__main_region_orthogonal_traffic_light_modes_normal_react(transitioned_before)
		return transitioned_after
	
	
	def __main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_react(self, transitioned_before):
		"""Implementation of __main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_react function.
		"""
		#The reactions of state smart green.
		transitioned_after = transitioned_before
		if transitioned_after < 1:
			if self.__time_events[3]:
				self.__exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green()
				self.__time_events[3] = False
				self.__enter_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_yellow_default()
				self.__main_region_orthogonal_traffic_light_modes_normal_react(1)
				transitioned_after = 1
		#If no transition was taken
		if transitioned_after == transitioned_before:
			#then execute local reactions.
			transitioned_after = self.__main_region_orthogonal_traffic_light_modes_normal_react(transitioned_before)
		return transitioned_after
	
	
	def __main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1_green_react(self, transitioned_before):
		"""Implementation of __main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1_green_react function.
		"""
		#The reactions of state green.
		transitioned_after = transitioned_before
		if transitioned_after < 1:
			if self.__time_events[4]:
				self.__exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green()
				self.__time_events[4] = False
				self.__enter_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_yellow_default()
				self.__main_region_orthogonal_traffic_light_modes_normal_react(1)
				transitioned_after = 1
			elif (self.car_detected) and (self.local_set_led_value):
				self.__exit_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1_green()
				self.__enter_sequence_main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1_green_default()
				self.__main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_react(1)
				transitioned_after = 1
		#If no transition was taken
		if transitioned_after == transitioned_before:
			#then execute local reactions.
			transitioned_after = self.__main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_react(transitioned_before)
		return transitioned_after
	
	
	def __main_region_orthogonal_traffic_light_modes_interrupted_react(self, transitioned_before):
		"""Implementation of __main_region_orthogonal_traffic_light_modes_interrupted_react function.
		"""
		#The reactions of state interrupted.
		transitioned_after = transitioned_before
		if transitioned_after < 1:
			if self.police_interrupt:
				self.__exit_sequence_main_region_orthogonal_traffic_light_modes_interrupted()
				self.__enter_sequence_main_region_orthogonal_traffic_light_modes_normal_default()
				self.__main_region_orthogonal_react(0)
				transitioned_after = 1
		#If no transition was taken
		if transitioned_after == transitioned_before:
			#then execute local reactions.
			transitioned_after = self.__main_region_orthogonal_react(transitioned_before)
		return transitioned_after
	
	
	def __main_region_orthogonal_traffic_light_modes_interrupted_r1_yellow_react(self, transitioned_before):
		"""Implementation of __main_region_orthogonal_traffic_light_modes_interrupted_r1_yellow_react function.
		"""
		#The reactions of state yellow.
		transitioned_after = transitioned_before
		if transitioned_after < 1:
			if self.__time_events[5]:
				self.__exit_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1_yellow()
				self.__time_events[5] = False
				self.__enter_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1_allblack_default()
				self.__main_region_orthogonal_traffic_light_modes_interrupted_react(1)
				transitioned_after = 1
		#If no transition was taken
		if transitioned_after == transitioned_before:
			#then execute local reactions.
			transitioned_after = self.__main_region_orthogonal_traffic_light_modes_interrupted_react(transitioned_before)
		return transitioned_after
	
	
	def __main_region_orthogonal_traffic_light_modes_interrupted_r1_allblack_react(self, transitioned_before):
		"""Implementation of __main_region_orthogonal_traffic_light_modes_interrupted_r1_allblack_react function.
		"""
		#The reactions of state allblack.
		transitioned_after = transitioned_before
		if transitioned_after < 1:
			if self.__time_events[6]:
				self.__exit_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1_allblack()
				self.__time_events[6] = False
				self.__enter_sequence_main_region_orthogonal_traffic_light_modes_interrupted_r1_yellow_default()
				self.__main_region_orthogonal_traffic_light_modes_interrupted_react(1)
				transitioned_after = 1
		#If no transition was taken
		if transitioned_after == transitioned_before:
			#then execute local reactions.
			transitioned_after = self.__main_region_orthogonal_traffic_light_modes_interrupted_react(transitioned_before)
		return transitioned_after
	
	
	def __clear_in_events(self):
		"""Implementation of __clear_in_events function.
		"""
		self.button_pressed = False
		self.button_released = False
		self.car_detected = False
		self.__time_events[0] = False
		self.__time_events[1] = False
		self.__time_events[2] = False
		self.__time_events[3] = False
		self.__time_events[4] = False
		self.__time_events[5] = False
		self.__time_events[6] = False
	
	
	def __clear_internal_events(self):
		"""Implementation of __clear_internal_events function.
		"""
		self.police_interrupt = False
		self.local_set_led = False
	
	
	def __micro_step(self):
		"""Implementation of __micro_step function.
		"""
		transitioned = -1
		self.__state_conf_vector_position = 0
		state = self.__state_vector[0]
		if state == self.State.main_region_orthogonal_toggle_mode_buttonnot_pressed:
			transitioned = self.__main_region_orthogonal_toggle_mode_button_not_pressed_react(transitioned)
		elif state == self.State.main_region_orthogonal_toggle_mode_buttonpressed:
			transitioned = self.__main_region_orthogonal_toggle_mode_button_pressed_react(transitioned)
		if self.__state_conf_vector_position < 1:
			state = self.__state_vector[1]
			if state == self.State.main_region_orthogonal_traffic_light_modesnormal_r1red:
				self.__main_region_orthogonal_traffic_light_modes_normal_r1_red_react(transitioned)
			elif state == self.State.main_region_orthogonal_traffic_light_modesnormal_r1yellow:
				self.__main_region_orthogonal_traffic_light_modes_normal_r1_yellow_react(transitioned)
			elif state == self.State.main_region_orthogonal_traffic_light_modesnormal_r1smart_green_r1green:
				self.__main_region_orthogonal_traffic_light_modes_normal_r1_smart_green_r1_green_react(transitioned)
			elif state == self.State.main_region_orthogonal_traffic_light_modesinterrupted_r1yellow:
				self.__main_region_orthogonal_traffic_light_modes_interrupted_r1_yellow_react(transitioned)
			elif state == self.State.main_region_orthogonal_traffic_light_modesinterrupted_r1allblack:
				self.__main_region_orthogonal_traffic_light_modes_interrupted_r1_allblack_react(transitioned)
	
	
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
			self.__clear_internal_events()
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
		#Default enter sequence for statechart Statechart
		self.__enter_sequence_main_region_default()
		self.__is_executing = False
	
	
	def exit(self):
		"""Implementation of exit function.
		"""
		#Deactivates the state machine.
		if self.__is_executing:
			return
		self.__is_executing = True
		#Default exit sequence for statechart Statechart
		self.__exit_sequence_main_region()
		self.__is_executing = False
	
	
	def trigger_without_event(self):
		"""Implementation of triggerWithoutEvent function.
		"""
		self.run_cycle()
	