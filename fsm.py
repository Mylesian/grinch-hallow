from typing import Collection
import random as rand

class State:
    def __init__(self, name, trigger, logic = None):
        self.trigger = trigger
        self.name = name
        self.logic = logic

class Machine:
    def __init__(self, states: Collection[State], start_state: State):
        self.states = states
        self.current_state = start_state

    def check_state(self):
        state_name = self.current_state.name
        possible_states = []
        for s in self.states:
            if s.trigger():
                possible_states.append(s)
        
        self.current_state = rand.choice(possible_states)
        if self.current_state.logic is not None and self.current_state.name != state_name: self.current_state.logic()

def calc_f(platform, target):
    g = (platform.pos - target.pos).magnitude()
    h = platform.pos.x - target.pos.x + platform.pos.y - target.pos.y
    
    return g + h