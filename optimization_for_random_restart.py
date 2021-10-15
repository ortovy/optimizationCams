import multiprocessing
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.patches import Rectangle
from PIL import Image
import glob
import numpy as np

import myHillClimbing
import multiprocessing.dummy as mp
from multiprocessing import Pool
from threading import Thread

'''
cctv types:
type 1: 90 degree angle camera  |price:tbd
type 2: 126 degree angle camera |price:tbd
type 3: 143 degree angle camera |price:tbd
type 4: 151 degree angle camera |price:tbd

cctv camera range:
type 1: 3 meters
type 2: 2 meters
type 3: 1.5 meters
type 4: 1.5 meters
'''


def set_room(width, length):
    room_built = np.zeros((width, length))
    for i in range(width):
        for j in range(length):
            if i == 0 or j == 0:
                room_built[i, j] = -1
            if i == width-1 or j == length-1:
                room_built[i, j] = -1
    return room_built


def set_block(room_built, start_i, start_j, shape_i, shape_j):
    for i in range(shape_i):
        for j in range(shape_j):
            room_built[start_i + i, start_j + j] = -1
    return room_built


def install_camera(room_built, x, y, type):
    # each type has its own unique photo distance here we define it
    photo_dist = 0
    if type == 1:
        photo_dist = 3000
    if type == 2:
        photo_dist = 2000
    if type == 3:
        photo_dist = 1500
    if type == 4:
        photo_dist = 1000
    # grower helps to increase the field of view of each camera type
    grower = 0
    room_len = room_built.shape[0]
    room_width = room_built.shape[1]
    # installs a camera if its from top to bottom
    if room_built[x-1, y] == -1:
        # range_ makes sure the camera does not go out of the matrix
        range_ = min(room_len - 1, photo_dist)
        for i in range(range_):
            # top, bot makes sure the camera does not go out of the walls
            top = max(y-grower, 1)
            bot = min(y+grower, room_width-1)
            for j in range(top, bot):
                room_built[i, j] += 1
            grower += type
        return room_built
    # installs a camera if its from bottom to top
    if room_built[x+1, y] == -1:
        # range_ makes sure the camera does not go out of the matrix
        range_ = max(0, x - photo_dist)
        for i in range(x+1, range_, -1):
            # top, bot makes sure the camera does not go out of the walls
            top = max(y - grower, 1)
            bot = min(y + grower, room_width-1)
            for j in range(top, bot):
                room_built[i, j] += 1
            grower += type
        return room_built
    # installs a camera if its from right to left
    if room_built[x, y+1] == -1:
        # range_ makes sure the camera does not go out of the matrix
        range_ = max(0, y-photo_dist)
        for i in range(y+1, range_, -1):
            # top, bot makes sure the camera does not go out of the walls
            top = max(x - grower, 1)
            bot = min(x + grower, room_len - 1)
            for j in range(top, bot):
                room_built[j, i] += 1
            grower += type
        return room_built

    # installs a camera if its from left to right
    if room_built[x, y-1] == -1:
        # range_ makes sure the camera does not go out of the matrix
        range_ = min(room_width-1, photo_dist)
        for i in range(range_):
            # top, bot makes sure the camera does not go out of the walls
            top = max(x - grower, 1)
            bot = min(x + grower, room_len - 1)
            for j in range(top, bot):
                room_built[j, i] += 1
            grower += type
        return room_built


def calculate_hot_zones(room_, hot_zones_arr_):
    sum_ = 0
    percentage = 0
    score_ = 0
    # An array that represents a percentage of coverage for each hot zone
    percentage_coverage_hotzones = []
    for hotzone in hot_zones_arr_:
        x, y, length, width = hotzone['x'], hotzone['y'], hotzone['length'], hotzone['width']
        total_cover_size = width*length
        for i in range(length):
            for j in range(width):
                sum_ += room_[i + x, j + y]
                if room_[i+x, j+y] > 0:
                    percentage += 1
        percentage_coverage_hotzones.append((percentage / total_cover_size) * 100)
        percentage = 0
        """
         # We will require that each hot zone will be covered with at least 75 percent
    score_ += sum_
    
    for coverage in percentage_coverage_hotzones:
        if coverage < 75:
            score_ = 0
    print(percentage_coverage_hotzones)
        """

    return sum_


def main():
    frames = []
    width = 5000
    length = 5000
    num_of_cameras = 3
    iter = 0
    max_score_of_possible_solutions = -1
    got_max_sol = 0
    max_iterations = 0
    room_init = set_room(width, length)
    hot_zone1 = {'x': 400, 'y': 400, 'length': 200, 'width': 300}
    hot_zone2 = {'x': 1100, 'y': 600, 'length': 250, 'width': 500}
    hot_zone3 = {'x': 2000, 'y': 1400, 'length': 500, 'width': 500}
    hot_zone4 = {'x': 4000, 'y': 3400, 'length': 900, 'width': 600}
    hot_zones_arr = [hot_zone1, hot_zone2, hot_zone3, hot_zone4]
    ultimate_score = 0
    # generate random solution --> return a room where all the cameras from solution are installed
    for i in range(5):
        max_iterations = 0
        iter = 0
        room_init = set_room(width, length)
        solution, room = myHillClimbing.generate_random_solution(width, length, room_init, num_of_cameras)
        # evaluate random solution
        best_score = calculate_hot_zones(room, hot_zones_arr)
        print("reset number:", i)
        while not got_max_sol and max_iterations != 5:
            max_score_of_possible_solutions = -1
            iter += 1
            print(f'Best score so far: {best_score}')
            possible_solutions = myHillClimbing.get_random_neighbors(solution, width, length, num_of_cameras)
            pool = multiprocessing.Pool(processes=8)
            results_of_processes = [pool.apply_async(
                process,
                args=(possible_solutions[i], width, length, hot_zones_arr,),
                callback=None
            )for i in range(1, len(possible_solutions))]
            pool.close()
            pool.join()
            for score_solution in results_of_processes:
                if score_solution.get()[1] >= max_score_of_possible_solutions:
                    selected_solution = score_solution.get()[0]
                    max_score_of_possible_solutions = score_solution.get()[1]
            if max_score_of_possible_solutions < best_score:
                got_max_sol = 1
            else:
                best_score = max_score_of_possible_solutions
                solution = selected_solution
            room_init = set_room(width, length)
            room = myHillClimbing.install_all_cameras(selected_solution, room_init)
            plt.matshow(room)
            plt.colorbar()
            for hot_zone in hot_zones_arr:
                plt.gca().add_patch(Rectangle((hot_zone['x'], hot_zone['y']), hot_zone['length'], hot_zone['width'], linewidth=1, edgecolor='r', facecolor='none'))
            plt.savefig('foo' + str(iter) + '.png')
            max_iterations += 1
            # next iteration
        for i in range(1, iter + 1):
            new_frame = Image.open('foo' + str(i) + '.png')
            frames.append(new_frame)
        frames[0].save('hillClimbing10.gif', format='GIF',
                       append_images=frames[1:],
                       save_all=True,
                       duration=300, loop=0)
        if best_score > ultimate_score:
            ultimate_score = best_score


def process(solution, width, length, hot_zones):
    room_init = set_room(width, length)
    room = myHillClimbing.install_all_cameras(solution, room_init)
    # min score is 0, init max_score_of_possible_solutions = -1--> selected_solution initialize
    score = calculate_hot_zones(room, hot_zones)
    map_score2sol = [solution, score]
    return map_score2sol


if __name__ == '__main__':
    main()
