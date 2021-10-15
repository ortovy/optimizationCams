import multiprocessing
import copy
from PIL import Image
import myHillClimbing
import optimization
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from operator import itemgetter
import random
import numpy as np
NUM_OF_CAMERAS = 3


def process_rand(width, length, num_of_cameras):
    room_built = optimization.set_room(width, length)
    solution, room_ = myHillClimbing.generate_random_solution(width, length, room_built, num_of_cameras)
    possible_solutions = [solution, room_]
    return possible_solutions


def rand_possible_solutions(num_of_solutions_to_rand, width, length, num_of_cameras):
    pool = multiprocessing.Pool(processes=12)
    possible_solutions_processes = [pool.apply_async(
        process_rand,
        args=(width, length, num_of_cameras,),
        callback=None
    ) for i in range(num_of_solutions_to_rand)]
    pool.close()
    pool.join()
    possible_solutions = []
    for x in possible_solutions_processes:
        possible_solutions.append(x.get())
    return possible_solutions


def create_room_to_solution(solution, width, length):
    room_built = optimization.set_room(width, length)
    room = myHillClimbing.install_all_cameras(solution, room_built)
    return room


def process_calc_score(sol, hot_zones_arr):
    # each sol contain tuple of solution&room of this solution
    score = optimization.calculate_hot_zones(sol[1], hot_zones_arr)
    scores_solution = [sol[0], score]
    return scores_solution


def calc_score_solution(possible_solutions, hot_zones_arr):
    # calc score un separate threads
    pool = multiprocessing.Pool(processes=12)
    processes_score_solution = [pool.apply_async(
        process_calc_score,
        args=(possible_solutions[i], hot_zones_arr,),
        callback=None
    ) for i in range(len(possible_solutions))]
    pool.close()
    pool.join()
    # add the items form processes_score_solution
    lst_tuple_scores_solutions = []
    for x in processes_score_solution:
        lst_tuple_scores_solutions.append(x.get())
    return lst_tuple_scores_solutions


def sort_solutions_by_score(scores_solutions):
    # get tuple of solution&score sort by score
    sorted_solutions_by_score = sorted(scores_solutions, key=itemgetter(1))
    p = sorted_solutions_by_score
    for i in p:
        print("sort_solutions_by_score")
        print(i[1])
        print(i[0])
    # return the "strongest" solutions
    return sorted_solutions_by_score[-5:]


def mutations_in_selected_solutions(selected_solutions, num_of_cameras, width, length):
    print("selected sol")
    print(selected_solutions)
    num_of_mutations_for_solutions = [3, 3, 2, 2, 1]
    survival_solutions = []
    permutations_ = permutations(num_of_cameras)
    # loop on "strongest" solutions" and create the next generation
    # the number of mutations for solution[i] is num_of_mutations_for_solutions[i]
    for i in range(len(selected_solutions)):
        # the lsat item in every solution is the score
        cur_sol = selected_solutions[i][0]
        mutations_of_solution = get_mutations_solution(cur_sol, permutations_,
                                                       num_of_mutations_for_solutions[i], width, length)
        for mutation_sol in mutations_of_solution:
            # create the room for this mutation
            room = create_room_to_solution(mutation_sol, width, length)
            # sol is tuple of solution and room for this solution
            survival_solutions.append(mutation_sol)
            survival_solutions.append(room)
    # add top solutions , calc their room
    for tuple_sol in selected_solutions:
        sol = tuple_sol[0]
        room = create_room_to_solution(sol, width, length)
        survival_solutions.append(sol)
        survival_solutions.append(room)
    # zip sol&room
    lst_tuple_survival_solutions = [x for x in zip(*[iter(survival_solutions)] * 2)]
    # add random solutions with their room
    rand_sols = rand_possible_solutions(4, width, length, num_of_cameras)
    for rand_sol in rand_sols:
        lst_tuple_survival_solutions.append(rand_sol)
    return lst_tuple_survival_solutions


def get_mutations_solution(solution_, permutations, num_mutations_solution, width, length):
    random.shuffle(permutations)
    sol = copy.deepcopy(solution_)
    cur_permutations = permutations[:num_mutations_solution]
    mutations_of_solution = []
    for permutation in cur_permutations:
        mutation_locations = []
        # Each solution consists of the location of all the cameras
        for i in range(NUM_OF_CAMERAS):
            p = myHillClimbing.get_new_location(sol[i], permutation[i], width, length)
            mutation_locations.append(p)
        mutations_of_solution.append(mutation_locations)
    return mutations_of_solution


def permutations(num_of_cameras):
    perm_array = np.zeros(3 ** num_of_cameras)
    permutations = []
    for i in range(3 ** num_of_cameras):
        # st
        perm_array[i] = str(np.base_repr(i, 3))
    for sidor in perm_array:
        sidoron = str(int(sidor))
        length = len(sidoron)
        permutations.append('0' * (num_of_cameras - length) + sidoron)
    return permutations


def drive_genetic_optimization():
    width = 5000
    iter = 0
    length = 5000
    hot_zone1 = {'x': 400, 'y': 400, 'length': 200, 'width': 300}
    hot_zone2 = {'x': 1100, 'y': 600, 'length': 250, 'width': 500}
    hot_zone3 = {'x': 2000, 'y': 1400, 'length': 500, 'width': 500}
    hot_zone4 = {'x': 4000, 'y': 3400, 'length': 900, 'width': 600}
    hot_zones_arr = [hot_zone1, hot_zone2, hot_zone3, hot_zone4]
    # at first lets rand 2o solutions
    print("Rand previous fathers")
    possible_solutions = rand_possible_solutions(20, width, length, NUM_OF_CAMERAS)
    for epoch in range(10):
        iter += 1
        print("Start iteration ", iter)
        # get score for each solution
        print("Calculate scores for every solution")
        scores_solutions = calc_score_solution(possible_solutions, hot_zones_arr)
        # sort by score
        print("Sort the solutions by score")
        selected_solutions = sort_solutions_by_score(scores_solutions)
        # for gif creation
        print("Best score so far: ", selected_solutions[len(selected_solutions)-1][1])
        best_perm = selected_solutions[len(selected_solutions)-1][0]
        room_init = optimization.set_room(width, length)
        room = myHillClimbing.install_all_cameras(best_perm, room_init)
        print("Create gif for iteration ", iter)
        plt.matshow(room)
        plt.colorbar()
        for hot_zone in hot_zones_arr:
            plt.gca().add_patch(
                Rectangle((hot_zone['x'], hot_zone['y']), hot_zone['length'], hot_zone['width'], linewidth=1,
                          edgecolor='r', facecolor='none'))
        plt.savefig('foo' + str(iter) + '.png')
        # create mutations in the solutions
        print("Create mutations in your best solutions")
        mutations_solutions = mutations_in_selected_solutions(selected_solutions, NUM_OF_CAMERAS, width, length)
        print("Get your next generation")
        possible_solutions = mutations_solutions

    # sort the last possible solutions and get the one with the best score
    score_last_solution = calc_score_solution(possible_solutions, hot_zones_arr)
    sort_best_solutions = sort_solutions_by_score(score_last_solution)
    best = sort_best_solutions.pop()
    best_sol, his_score = best[0], best[1]
    print(best_sol, his_score)
    frames = []
    for i in range(1, iter + 1):
        new_frame = Image.open('foo' + str(i) + '.png')
        frames.append(new_frame)
    frames[0].save('hillClimbing.gif', format='GIF',
                   append_images=frames[1:],
                   save_all=True,
                   duration=300, loop=0)


if __name__ == '__main__':
    drive_genetic_optimization()
