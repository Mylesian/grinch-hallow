import pygame
import math
import random
# import entity

from const import(
    screen_constants as sc,
    colors as c,
    maze_consts as mz
)

def discreteTriangleDistribution(min, max):
    span = max - min + 1
    halfSpan = span/2
    halfRoundUp = math.ceil(halfSpan)
    totalWeight = halfRoundUp*halfRoundUp
    lookupTable = []
    def futureWeightAt(fromMin):
        if fromMin < halfSpan:
            return totalWeight - fromMin * (fromMin + 1) / 2
        else:
            fromEnd = span - fromMin
            return fromEnd*(fromEnd+1)/2
    
    def getProbability(fromMin):
        here = futureWeightAt(fromMin)
        before = futureWeightAt(fromMin-1)

        return 1 - here/before

    for i in range(min, max):
        lookupTable.append(getProbability(i - min+1))

    def sample(value):
        
        if value < min:
            return 0
        if value >= max:
            return 1

        return lookupTable[value - min]
    return sample

class Pather:
    def __init__(self, controller):
        self.controller = controller

        # 1 = speedrunner (always full tilt), 0 = AFK. 0.8 = usually moving.
        self.move_probability = 0.8

        # Bounds on how long to wait between jumps / falls.
        self.min_seconds_on_platform = 1
        self.max_seconds_on_platform = 2

        self.jump_distribution = None   # grounded frame count -> chance to jump
        self.land_distribution = None   # airborne frame count -> chance to land

        self.backtrack_probability = 0.45   # chance to change direction on jump/landing
        self.height_variance = 1.0          # how far landings deviate from launch height

        self.successful_path = None   # last path that reached the end
        self.last_attempt = None      # last path tried, even if it failed
        self.attempts_used = 0        # attempts the last plan_path() call needed

        self.update()
    
    def update(self):
        min = round(self.min_seconds_on_platform/sc.DT)
        max = round(self.max_seconds_on_platform/sc.DT)
        if max < min:
            max = min
        self.jumpDistribution = discreteTriangleDistribution(min, max)
        
        hv = self.height_variance * self.height_variance

        min = round((self.controller.timeToPeak + (1.0 - hv) * self.controller.timeToFall)/sc.DT)
        max = round((self.controller.timeToPeak + (1.0 + 0.25 * hv) * self.controller.timeToFall)/sc.DT)
        if max < min:
            max = min
        self.landDistribution = discreteTriangleDistribution(min, max)

    def selectInputForState(self, state, jumpLimit):
        input = {"x" : 0, "jump": False}
        if random.random() < self.move_probability:
            if state.facing == 0:
                if random.random() < self.backtrack_probability:
                    state.facing = -1
                else:
                    state.facing = 1
            input["x"] = state.facing
        if state.y >= jumpLimit:
            if state.isOnGround(self.controller.coyoteFrames):
                pJump = self.jumpDistribution(state.framesOnGround)
                input["jump"] = random.random() < pJump

        return input

    def planPath(self, map, attemptLimit = 50):
        for attempts in range(attemptLimit):
            map.clear()
            path = self.attemptPath(map)

            if(path):
                self.attempts_used = attempts + 1
                print(f"found successful path in ${attempts + 1} attempt ${'s' if attempts > 0 else ' '}.")
                self.successfulPath = path
                return True

        self.attempts_used = attemptLimit
        self.successfulPath = None
        print("Failed to find path")
        return False

    def attemptPath(self, map):
        columns, rows = map.getDimensions()
        fallLimit = rows - 2
        controller = self.controller
        jumpLimit = controller.jumpHeight

        state = CharacterState(
            0,
            jumpLimit + math.floor(random.random() * (fallLimit - jumpLimit) + 1 - self.controller.height)
        )
        state.framesOnGround = 1
        state.facing = 1
        secondsBudget = 100
        ticksBudget = secondsBudget/sc.DT
        path = [state]

        
        bottom = state.bottomTile(self.controller.height)
        map.place(mz.SOLID_RESERVATION, 0, bottom + 1)
        map.place(mz.PLAYER_RESERVATION, 0, bottom)
        

        wasOnGround = True

        for i in range(ticksBudget): # type: ignore
            input = self.selectInputForState(state, jumpLimit)

            nearStart = state.x < 2 and len(path) < 3/sc.DT
            input["jump"] &= not nearStart
            newState = self.controller.step(state, input)
            (collided, left, right, top, bottom) = self.controller.handleCollision(newState, map)
            if newState.isFalling():
                needsFloor = False

                if wasOnGround:
                    endPlatform = self.jumpDistribution(state.framesOnGround)
                    needsFloor = nearStart or random.random() >= endPlatform
                else:
                    needsFloor = bottom > fallLimit or random.random() < self.landDistribution(newState.framesSinceGround)

                if needsFloor:
                    floorPlaced =False
                    for x in range(left, right):
                        if bottom > fallLimit or map.getTileAt(x, bottom) != mz.PLAYER_RESERVATION:
                            map.place(mz.SOLID_RESERVATION, x, bottom)
                            floorPlaced = True

                    if floorPlaced:
                        (collided, left, right, top, bottom) = self.controller.handleCollision(newState, map)

                    wasOnGround = floorPlaced
                else:
                    wasOnGround = False
            else:
                wasOnGround = newState.isOnGround()
            map.fill(mz.PLAYER_RESERVATION, left, top, right, top if newState.velY > 0 else bottom)
            state = newState
            path.append(state)
            if(state.x >= columns - 1 and state.isOnGround()):
                return path

        self.lastAttempt = path
        return None
