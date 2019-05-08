import random

objects = ["styrofoam", "spray", "white_box", "blockB", "lysol", "bottle"]
floor_objects = ["blockA", "black_poly", "wood_moistener"]
table_state = [[None, None, None, None, None, None, None], [None, None, None, "Bin", None, None, None], [None, None, None, None, None, None, None]]
human_state = [None, None, None]
floor_state = [[None, None, None], [None, None, None]]

random.shuffle(objects)
random.shuffle(floor_objects)
for i in range(6):
    depth = random.randint(0, 2)
    table_state[depth][i + int(i > 3)-1] = objects[i]
human_state[random.randint(0, 2)] = "human"

for i in range(3):
    depth = random.randint(0, 1)
    floor_state[depth][i -1] = floor_objects[i]
# print('\n'.join([''.join(['{:4}'.format(item) for item in row])
#       for row in table_state]))
print "table placement"
print table_state[0]
print table_state[1]
print table_state[2]
print "human placement"
print human_state
print "floor placement"
print floor_state[0]
print floor_state[1]
