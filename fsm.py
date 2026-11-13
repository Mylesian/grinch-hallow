from typing import Collection
import random as rand

class State:
    def __init__(self, trigger, logic = None):
        self.trigger = trigger
        self.logic = logic

class Machine:
    def __init__(self, states: Collection[State], start_state: State):
        self.states = states
        self.current_state = start_state

    def check_state(self):
        possible_states = []
        for s in self.states:
            if s.trigger():
                possible_states.append(s)
        
        self.current_state = rand.choice(possible_states)