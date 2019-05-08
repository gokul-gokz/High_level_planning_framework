# "Well, it had to be" - Mihir

import numpy as np
import Queue as queue
from multiprocessing import Queue

path_length = 0
robot_hand_length = 100  # in grid cell units

class node:
    def __init__(self, val, x, y):
        self.color = val
        self.x = x
        self.y = y
        self.f = None
        self.g = 99999999  # a very high value
        self.h = None  # use Euclidean distance as heuristic
        self.parent = None

    def update(self, val, f, g, h, parent):
        self.color = val
        self.f = f
        self.g = g
        self.h = h
        self.parent = parent

    def isGoal(self, goal):
        if self.color == 4 or (self.x == goal.x and self.y == goal.y):
            return True
        else:
            return False

    def get_neighbors(self, open_list, maze):
        four_connected = ((-1,0), (0,-1), (1,0), (0,1))
        neighbors = []
        for dir1 in four_connected:
            #print(dir1)
            x = self.x + dir1[0]
            y = self.y + dir1[1]
            #print("---------------------")
            #print(x,y)
            if x < 0 or y < 0 or x > (len(maze)-1) or y > (len(maze[0])-1): # If out of bound block.
                continue
            elif int(maze[x][y].color) == 2 or int(maze[x][y].color) == 1:    # Visited node or obstacle, then dont add to neighbor
                continue
            elif self.in_open_list(x, y, open_list):    # Check if node is already in open list
                continue

            neighbors.append(maze[x][y])  # Add node as neighbor of the cell

        return neighbors

    def in_open_list(self, x, y, open_list):
        for item in open_list:  # Check if node is already in open list
                if item.x == x and item.y == y:
                    return True
        return False

def dist(a, goal):
    return np.sqrt((a.x - goal.x)**2 + (a.y - goal.y)**2) # Euclidean distance

def draw_path(start, goal, maze1, list):
    global path_length
    if dist(start, goal) == 0:
        return maze1, list
    while dist(start, goal) != 0:
        (x, y) = maze1[goal.x][goal.y].parent
        new_goal = maze1[x][y]
        maze1[x][y].color = 5
        path_length += 1
        list.append((x, y))
        return draw_path(start, new_goal, maze1, list)



class low_level_planner:
    def __init__(self, game_width, game_height, grid_size, robot_loc, object_loc):
        self.w = game_width
        self.h = game_height
        self.grid_size = grid_size
        self.l1 = game_height/grid_size
        self.l2 = game_width/grid_size
        self.grid = np.zeros((self.l1,self.l2))
        self.start = robot_loc
        self.goal = object_loc

    def update_start_goal_positions(self):

        points = [self.start, self.goal]
        for i in range(len(points)):
            if points[i] == self.start:
                color = 3
            elif points[i] == self.goal:
                color = 4
            else:
                color = 1
            i1 = int(points[i][0]/self.grid_size)
            j1 = int(points[i][1]/self.grid_size)
            self.grid[i1][j1] = color

    def update_object_information(self, rectangular_objects):
        for itr in range(len(rectangular_objects)):
            i1 = rectangular_objects[itr][0]/self.grid_size
            j1 = rectangular_objects[itr][1]/self.grid_size
            i2 = rectangular_objects[itr][2]/self.grid_size
            j2 = rectangular_objects[itr][3]/self.grid_size

            color = 1
            center_i = rectangular_objects[itr][0] + rectangular_objects[itr][2]/2
            center_j = rectangular_objects[itr][1] + rectangular_objects[itr][3]/2

            if abs(center_i - self.goal[0]) <= 1 and abs(center_j - self.goal[1]) <= 1:
                color = 4

            for i in range(i1, i1+i2+1):
                for j in range(j1, j1+j2+1):
                    self.grid[i][j] = color

    def plan_hand_motion(self, robot_loc, object_loc):
        entrance_node = (int(robot_loc[0]/self.grid_size), int(robot_loc[1]/self.grid_size))
        exit_node = (int(object_loc[0]/self.grid_size), int(object_loc[1]/self.grid_size))
        return self.a_star(self.grid, entrance_node, exit_node)

    #--------------------------------------------------------------------------------------------
    # This function uses BFS. adds (left, mid, right) for each point. new mid is calculated in right and then
    # in left. Both new mids are appended back to queue. Therefore, this checks for the feasibility of points
    # at each level first, hence BFS.
    # Returns success, point. success is boolean, true if path found. point is the point from which the path
    # is found.
    def get_feasible_position(self, (left1, mid1, right1)):
        q = queue.Queue()
        i = int(self.start[0]/self.grid_size)    # As robot only moves horizontally, 'i' doesn't change
        left = int(left1/self.grid_size)
        mid = int(mid1/self.grid_size)
        right = int(right1/self.grid_size)
        q.put((left, mid, right))
        q.put((None, right, None))
        q.put((None, left, None))
        #print "queue: ", q

        while True:
            if q.empty():
                print "Symbol INVALID! Can not perform option pick "
                return False, None, None

            left, mid, right = q.get()

            success, path = self.plan_hand_motion((self.start[0], mid*self.grid_size), self.goal)
            #print success, mid, path

            if success:
               # print "found the point for effect of move!"
                mid=mid*self.grid_size + self.grid_size/2
                return success, mid, path

            else:
                # Get neighbors
                if left is not None and right is not None:
                    if np.abs(right - mid) > 1: # The cells should be at least be one cell apart, else new mid will be same as right or mid
                        q.put((mid, int((mid+right)/2), right))
                    if np.abs(mid - left) > 1:
                        q.put((left, int((left+mid)/2), mid))




    def a_star(self, maze, start_node, exit_node):

        global path_length
        path_length = 0
        maze[start_node[0]][start_node[1]] = 3
        maze[exit_node[0]][exit_node[1]] = 4
        #global no_exapanded_nodes
        maze1 = [[node(maze[i][j], i, j) for j in range(len(maze[0]))] for i in range(len(maze))]
        goal = node(4, exit_node[0], exit_node[1])
        start = node(3, start_node[0], start_node[1])
        g = 0
        h = dist(start, goal)
        f = g+h
        start.update(3, f, g, h, None)
        open_list = []
        closed_list = []
        open_list.append(start)
        cost = 1
        list = []   # Stores the path grid indices (i,j)

        while True:
            if len(open_list) == 0:     # If no more nodes to expand, and goal not reached
                print("No path found")
                return False

            open_list.sort(key=lambda x: (x.f, x.g), reverse=True)
            current = open_list.pop()
            #no_exapnded_nodes += 1
            closed_list.append(current)
            maze1[current.x][current.y].color = '2'

            if current.isGoal(goal):    # If current expanded node is Goal
                global robot_hand_length
                #print("no_exapanded_nodes: ", len(closed_list))
                #print("Path Found!")
                maze1, list = draw_path(start, goal, maze1, list)
                #print("path_length: ", path_length+1)
                #draw_canvas(canvas, maze1)
                if path_length <= robot_hand_length:
                    return True, list
                return False, list
            else:
                neighbors = current.get_neighbors(open_list, maze1)
                for neighbor in neighbors:
                    g = current.g + cost
                    h = dist(neighbor, goal)
                    f = g + h
                    neighbor.update(0, f, g, h, (current.x, current.y))
                    open_list.append(neighbor)
                    maze1[neighbor.x][neighbor.y].parent = (current.x, current.y)
                    #maze1[neighbor.x][neighbor.y] = '5'

        #return False, list


    def grids_to_rectangles(self, path):
        list =[]
        for i in range(len(path)):
            list.append((path[i][0]*self.grid_size + self.grid_size/2, path[i][1]*self.grid_size + self.grid_size/2, self.grid_size, self.grid_size))
        return list

    def print_grid(self):
        print self.grid


"""
def uncertainty_handler(option_name):
    success = False
    if(option_name == 'pick'):
        success = plan_hand_motion()
        if success:
            print "success!"
            return
        else:
            print "failure :///"
            return
"""


def get_trajectory(game_width, game_height, grid_size, robot_loc, object_loc, test_objects):
    #game_width = 100
    #game_height = 50
    #grid_size = 10
    option_name = 'pick'
    success = False
    #robot_loc = (48, 50)
    #object_loc = (11, 50)

    #test_objects = [(2, 3, 20, 20)]  # List of objects position in terms of rectangles (x, y, height, width)

    planner = low_level_planner(game_width, game_height, grid_size, robot_loc, object_loc)
    planner.update_start_goal_positions()  # 1 for occupied
    #planner.start = robot_loc
    #planner.goal = object_loc
    #planner.update_grid([(30, 50)], 1)
    planner.update_object_information(test_objects)
    #planner.print_grid()

    if option_name == 'pick':
        success, path_found = planner.plan_hand_motion(robot_loc, object_loc)
        # if success:
        #     print "robot arm reaches object! :)"
        # else:
        #     print "robot arm does NOT reach the object :/"
        #print success
        #print path_found
        searched_path = planner.grids_to_rectangles(path_found)

        # ########### Sample points for symbol updation ##########
        # if not success:
        #     print planner.get_feasible_position(symbol_info)
        # ####################################
    return success, searched_path

def get_feasible_move_position(game_width, game_height, grid_size, robot_loc, object_loc, test_objects, symbol_info):


    planner = low_level_planner(game_width, game_height, grid_size, robot_loc, object_loc)
    planner.update_start_goal_positions()  # 1 for occupied

    planner.update_object_information(test_objects)
    #planner.print_grid()


    return planner.get_feasible_position(symbol_info)



# if __name__=='__main__':
#     game_width = 100
#     game_height = 50
#     grid_size = 10
#     option_name = 'pick'
#     success = False
#     robot_loc = (48, 50)
#     object_loc = (11, 50)
#
#     #test_objects = [(2, 3, 20, 20)]   # List of objects position in terms of rectangles (x, y, height, width)
#     #test_objects.append((30, 10, 5, 70))
#     test_objects = [(20, 10, 5, 80)]
#
#     symbol_info = (10, 50, 90) # left, mid, right
#
#
#     get_trajectory(game_width, game_height, grid_size, robot_loc, object_loc, test_objects)
#
#     get_feasible_move_position(game_width, game_height, grid_size, robot_loc, object_loc, test_objects,symbol_info)
