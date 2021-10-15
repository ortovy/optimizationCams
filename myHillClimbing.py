from random import randrange
import optimization
import random
import copy
import numpy as np
LEARNING_RATE = 100


def generate_random_solution(width, length, room_built, num_of_cameras):
    solution = []
    camera_location = {}
    # up = 5  down = 6 right = 7 left = 8
    for i in range(num_of_cameras):
        # random location
        location = randrange(5, 8)
        # random camera type
        camera_type = randrange(1, 4)
        if location == 5:#up
            camera_location = {'type': camera_type, 'x': randrange(1, width - 2), 'y': 1, 'location': 'up'}
        if location == 6:#down
            camera_location = {'type': camera_type, 'x': randrange(1, width - 2), 'y': length - 2, 'location': 'down'}
        if location == 7:#left
            camera_location = {'type': camera_type, 'x': 1, 'y': randrange(1, length - 2), 'location': 'left'}
        if location == 8:#right
            camera_location = {'type': camera_type, 'x': width - 2, 'y': randrange(1, length - 2), 'location': 'right'}
        solution.append(camera_location)
    room = install_all_cameras(solution, room_built)
    return solution, room


def find_right_neighbor(cur_location_in_solution, width, length):
    if cur_location_in_solution['location'] == 'up' or cur_location_in_solution['location'] == 'down':
        if cur_location_in_solution['x'] < width - 2:
            cur_location_in_solution['x'] += 1
        # is not possible to increase x value, so moved to the closet sell in right wall
        elif cur_location_in_solution['x'] == width - 2 and cur_location_in_solution['location'] == 'up':
            cur_location_in_solution['y'] = 2
            cur_location_in_solution['location'] = 'right'
        # got to max x in bottom wall
        elif cur_location_in_solution['x'] == width - 2:
            cur_location_in_solution['y'] = length - 3
            cur_location_in_solution['location'] = 'right'

    elif cur_location_in_solution['location'] == 'left' or cur_location_in_solution['location'] == 'right':
        if cur_location_in_solution['y'] < length - 2:
            cur_location_in_solution['y'] += 1
        # # is not possible to increase y value, so moved to the closet sell in down wall
        elif cur_location_in_solution['y'] == length - 2 and cur_location_in_solution['location'] == 'left':
            cur_location_in_solution['x'] = 2
            cur_location_in_solution['location'] = 'down'
        elif cur_location_in_solution['y'] == length - 2:
            cur_location_in_solution['x'] = width - 3
            cur_location_in_solution['location'] = 'down'
    return cur_location_in_solution


def find_left_neighbor(cur_location_in_solution, width, length):
    if cur_location_in_solution['location'] == 'up' or cur_location_in_solution['location'] == 'down':
        if cur_location_in_solution['x'] > 1:
            cur_location_in_solution['x'] -= 1
        # is not possible to decrease x value, so moved to the closet sell
        elif cur_location_in_solution['x'] == 1 and cur_location_in_solution['location'] == 'up':
            cur_location_in_solution['y'] = 2
            cur_location_in_solution['location'] = 'left'
        # got to min x in bottom wall
        elif cur_location_in_solution['x'] == 1:
            cur_location_in_solution['y'] = length - 3
            cur_location_in_solution['location'] = 'left'

    elif cur_location_in_solution['location'] == 'left' or cur_location_in_solution['location'] == 'right':
        if cur_location_in_solution['y'] > 1:
            cur_location_in_solution['y'] -= 1
        elif cur_location_in_solution['y'] == 1 and cur_location_in_solution['location'] == 'left':
            cur_location_in_solution['x'] = 2
            cur_location_in_solution['location'] = 'up'
        elif cur_location_in_solution['y'] == 1:
            cur_location_in_solution['x'] = width - 3
            cur_location_in_solution['location'] = 'up'
    return cur_location_in_solution


def install_all_cameras(solution, room):
    for camera in solution:
        room = optimization.install_camera(room, camera['x'], camera['y'], camera['type'])
    return room


def get_permutations(n):
    perm_array = np.zeros(3**n)
    permutations = []
    for i in range(3**n):
        perm_array[i] = str(np.base_repr(i, 3))
    for sidor in perm_array:
        sidoron = str(int(sidor))
        length = len(sidoron)
        permutations.append('0'*(n-length) + sidoron)
    random.shuffle(permutations)
    return permutations[:5]


def get_new_location(cur_location_in_solution, move_bit, width, length):
    new_location = {}
    # case bit_move = 0 --> no movement
    if move_bit == '0':
        new_location = cur_location_in_solution
    # case bit_move = 1 --> move to right
    if move_bit == '1':
        new_location = find_right_neighbor(cur_location_in_solution, width, length)
        for i in range(LEARNING_RATE-1):
            new_location = find_right_neighbor(new_location, width, length)
    # case bit_move = 1 --> move to left
    if move_bit == '2':
        new_location = find_left_neighbor(cur_location_in_solution, width, length)
        for i in range(LEARNING_RATE-1):
            new_location = find_left_neighbor(new_location, width, length)
    return new_location


def get_random_neighbors(cur_solution, width, length, num_of_cameras):
    # len of each permutation is num_of_cameras
    cur_sol_copy = copy.deepcopy(cur_solution)
    permutations = get_permutations(num_of_cameras)
    solutions = [len(cur_solution)]
    # first bit is camera 1, second bit is camera 2..
    for permutation in permutations:
        solution = []
        # Each solution consists of the location of all the cameras
        for i in range(len(cur_sol_copy)):
            solution.append(get_new_location(cur_sol_copy[i], permutation[i], width, length))
            cur_sol_copy = copy.deepcopy(cur_solution)
        solutions.append(solution)
    return solutions


