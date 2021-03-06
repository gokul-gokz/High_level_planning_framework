from game.data_generation.helpers import *
from plan_helpers import *
import threading
from CanVsBin.option_receiver import *

import pre_load
temp=1
class Proposition:
    def __init__(self, symb_list, prec_option, parent, param):
        self.symb_list = frozenset(symb_list)
        self.prec_option = prec_option
        self.parent = parent
        self.param = param

    def get_neighbors(self, visited):
        neighbors = []

        #Checking whether the preconditions are satisfied for an option, if so then set isIn to true
        for o in pre_load.preconditions:
            isIn = False
            for pre in pre_load.preconditions[o]:

                if pre.issubset(self.symb_list):
                    isIn = True
                    break
            if isIn:
                if 'move' in o:
                    for loc in pre_load.move_partitions:
                        new_prop = Proposition((self.symb_list | loc[0]) - loc[1], o, self, loc[2])
                        if new_prop.symb_list not in visited:
                            visited.add(frozenset(new_prop.symb_list))
                            neighbors.append(new_prop)
                else:
                    for outcome in [val for i, val in enumerate(pre_load.effects_plus.keys()) if o == val[:val.index('_')]]:
                        for p in pre_load.effects_plus[outcome]:
                            if True in pre_load.pmasks[p][3:]:
                                obj = (pre_load.pmasks[p].index(True)) / 3
                        new_prop = Proposition((self.symb_list | pre_load.effects_plus[outcome]) - pre_load.effects_less[outcome], outcome, self, obj)

                        if new_prop.symb_list not in visited:
                            visited.add(frozenset(new_prop.symb_list))
                            neighbors.append(new_prop)

        return neighbors


    def replanning_get_neighbors(self, visited, failed_option,level):
            neighbors = []
            global temp
            # Removing the failed option for the tree

            options=pre_load.preconditions.copy()
            #del options["move1"]
            del options[failed_option[:-2]]

            if(level>1):
                options=pre_load.preconditions.copy()

            #print "level",temp
            #print options
            temp=temp+1

            for o in options:
                isIn = False
                for pre in options[o]:

                    if pre.issubset(self.symb_list):
                        isIn = True
                        break
                if isIn:
                    if 'move' in o:
                        for loc in pre_load.move_partitions:
                            new_prop = Proposition((self.symb_list | loc[0]) - loc[1], o, self, loc[2])
                            if new_prop.symb_list not in visited:
                                visited.add(frozenset(new_prop.symb_list))
                                neighbors.append(new_prop)
                    else:
                        for outcome in [val for i, val in enumerate(pre_load.effects_plus.keys()) if o == val[:val.index('_')]]:
                            for p in pre_load.effects_plus[outcome]:
                                if True in pre_load.pmasks[p][3:]:
                                    obj = (pre_load.pmasks[p].index(True)) / 3
                            new_prop = Proposition((self.symb_list | pre_load.effects_plus[outcome]) - pre_load.effects_less[outcome], outcome, self, obj)

                            if new_prop.symb_list not in visited:
                                visited.add(frozenset(new_prop.symb_list))
                                neighbors.append(new_prop)

            return neighbors


class PlannerThread(threading.Thread):
    optionT = None
    def __init__(self, threadID, name, optionThread):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.optionT = optionThread
        self.hl_start = None
        self.hl_end = None

    def run(self):
        self.runningT = True
        counter = 0
        while self.runningT:
            counter += 1
            while self.hl_start is None:
                time.sleep(0.5)
            # Wait until:
            # Option_receiver is either: success/fail/waiting
            # Read the worldstate, scale it to start statue, as the hl_start
            # Then you can start a plan

            #hl_start = convert_to_HL(startState, P, pmasks)

            if self.optionT.runningT == False:
                self.runningT = False
                break
            #print "start to plan"
            #flag=0
            path = self.bfs(self.hl_start, self.hl_end,0)
            #print path
            #print 'blep'

            if path is None:
                #print 'ERRROR! path is None Type!'
                time.sleep(5)
                self.optionT.tLock.acquire()
                worldState = self.optionT.worldState
                self.optionT.tLock.release()
                scaledState = apply_scale(pre_load.scaler, worldState)
                self.hl_start = convert_to_HL(scaledState, pre_load.P, pre_load.pmasks)
            elif len(path) < 2:
                #print 'ERRROR! No available return!'
                time.sleep(5)
            elif len(path) == 2:
                for i in range(len(path[0])):
                    print("Option",i)
                    if 'pick' in path[0][i]:
                        aPlan = ('pick', path[1][i]-1)
                    elif 'place' in path[0][i]:
                        aPlan = ('place', path[1][i]-1)
                    elif 'move' in path[0][i]:
                        aPlan = ('moveto', int(path[1][i]))
                    else:
                        print 'something wrong.'
                        aPlan = ('error', -1)
                    if aPlan[0]!='error':
                        # call optionT here
                        self.optionT.tLock.acquire()
                        self.optionT.tupleIn = aPlan
                        self.optionT.tLock.release()
                        # # time for executing the plan
                        time.sleep(1)

##-----------------------------------------    Replanning starts here -------------------------------------------------------------------------------------------
                        #This is the place where the option is sent to execute
                        #So make the option fail here
                        # if aPlan[0]=="pick" and aPlan[1]==7:
                        #     break_option=1
                        #     self.optionT.errorState=1
                        #     self.optionT.tLock.release()
                        #     #break
                        # else:
                        #     self.optionT.tupleIn = aPlan
                        #     self.optionT.tLock.release()
                        # # time for executing the plan
                        #     time.sleep(1)
                    #self.optionT.tLock.acquire()
                    print self.optionT.errorState
                    if self.optionT.errorState == ErrorCode.obstacle:
                        print '=====Re-planning ' + str(counter) + '====='
                        # Error happens
                        # Now world state is the new start state
                        time.sleep(5)

                        self.optionT.tLock.acquire()
                        worldState = self.optionT.worldState
                        self.optionT.tLock.release()

                        print worldState
                        scaledState = apply_scale(pre_load.scaler, worldState)
                        self.hl_start = convert_to_HL(scaledState, pre_load.P, pre_load.pmasks)
                        print self.hl_start
                        # Reset error state
                        self.optionT.tLock.acquire()
                        self.optionT.errorState = ErrorCode.no_error
                        self.optionT.tLock.release()

                        ##Added by gokul
                        #self.hl_end=set(['p53', 'p37' , 'p1', 'p63','p39', 'p70'])
                        #self.hl_end=set([ 'p53', 'p37', 'p70', 'p42', 'p1', 'p16', 'p64', 'p39', 'p63'])
                        #flag=1

                        #p1- object 4
                        #p16- object 5
                        #p37- object 1
                        #p39- object 7
                        #p42- object 3
                        #p44- object 9
                        #p53- object 0
                        #p70- object 2
                        #p64- object 6
                        #p63- oobject 8

                        object_symbols=['p53', 'p37', 'p70', 'p42', 'p1', 'p16', 'p64', 'p39', 'p63']
                        print self.hl_end
                        self.hl_end.add(object_symbols[self.optionT.errorInfo])
                        print self.hl_end
                        path = self.bfs(self.hl_start, self.hl_end, 1 )
                        if path is None:
                            #print 'ERRROR! path is None Type!'
                            time.sleep(5)
                            self.optionT.tLock.acquire()
                            worldState = self.optionT.worldState
                            self.optionT.tLock.release()
                            scaledState = apply_scale(pre_load.scaler, worldState)
                            self.hl_start = convert_to_HL(scaledState, pre_load.P, pre_load.pmasks)
                        elif len(path) < 2:
                            #print 'ERRROR! No available return!'
                            time.sleep(5)
                        elif len(path) == 2:
                            for i in range(len(path[0])):
                                if 'pick' in path[0][i]:
                                    aPlan = ('pick', path[1][i]-1)
                                elif 'place' in path[0][i]:
                                    aPlan = ('place', path[1][i]-1)
                                elif 'move' in path[0][i]:
                                    aPlan = ('moveto', int(path[1][i]))
                                else:
                                    print 'something wrong.'
                                    aPlan = ('error', -1)
                                if aPlan[0]!='error':
                                    # call optionT here
                                    self.optionT.tLock.acquire()

                                    self.optionT.tupleIn = aPlan
                                    self.optionT.tLock.release()
                                    # time for executing the plan
                                    time.sleep(1)
                                #self.optionT.tLock.acquire()

                        #self.optionT.tLock.release()
                            break
                        break
                     #else:
                    #     print 'continue'
                    #     self.optionT.tLock.release()

            ## for test
            if counter > 1:
               self.runningT = False
               self.optionT.runningT = False
               self.hl_start = None
               self.hl_end = None


    def bfs(self, start, goal,flag):
        if(not flag):
            start_time = time.time()

            queue = [Proposition(start, None, None, None)]
            cur = queue.pop()
            visited = {frozenset(cur.symb_list)}

            while not goal.issubset(cur.symb_list):

                queue = queue + cur.get_neighbors(visited)
                if len(queue) == 0:
                    print "no solution found"
                    break
                cur = queue.pop(0)     # this will break if there is no solution
            res, par, nodes = self.backtrace(cur)
            end_time = time.time()
            print "High_level_plan"
            print "------------------------------------------------------------"
            print "visited length: ", len(visited)
            print "Elapsed time: ", end_time - start_time, "seconds"
            if not(len(queue) == 0):
                print res
                # print ""
                # print par
                return res, par
            else:
                print "max depth explored: ", len(res)
                return


        else:
            #Hardcoding the failure
            failed_node='pick8_0'
            print"Node_failure at",failed_node
            print"Reason for failure:"
            print"Obstacle"
            print"Object7"
            print"Option exists for picking the Obstacle"

            #Replanning
            print "Replanning started"

            start_time=time.time();
            replan_queue = [Proposition(start, None, None, None)]
            cur = replan_queue.pop()
            visited = {frozenset(cur.symb_list)}

            #Variables to find the level of expansion
            max_node=0
            curr_node=0
            level=0

            while not goal.issubset(cur.symb_list):

                #While replanning, call the function replanning_get_neighbours
                #Arguments: Visited =current symbolic list
                #           Failed node
                #           level - the current level of expansion in the bfs tree

                replan_queue = replan_queue + cur.replanning_get_neighbors(visited,failed_node,level)

                #Steps to find the level
                if(max_node==curr_node):
                    max_node= len(replan_queue)
                    curr_node=0
                    level=level+1

                curr_node=curr_node+1


                if len(replan_queue) == 0:
                    print "no solution found"
                    break
                cur = replan_queue.pop(0)     # this will break if there is no solution
            end_time=time.time();
            res, par, nodes = self.backtrace(cur)

            end_time = time.time()

            #execute the plan.
            #res is the option
            #par is the parameters

            print"Replanning solution"
            print "visited length: ", len(visited)
            print "Elapsed time: ", end_time - start_time, "seconds"
            if not(len(replan_queue) == 0):
                print "Final result"
                print res
                # print ""
                # print par
                return res, par
            else:
                print "max depth explored: ", len(res)
                return
            self.runningT=False

    def backtrace(self, cur):
        opt_list = []
        opt_params = []
        shortest_path_nodes=[]
        while not cur.prec_option == None:
            opt_list.append(cur.prec_option)


            opt_params.append(cur.param)
            shortest_path_nodes.append(cur)
            cur = cur.parent

        return opt_list[::-1], opt_params[::-1],  shortest_path_nodes[::-1]

if __name__=='__main__':
    pygame.init()
    pre_load.init()

    test_optionT = OptionThread(10, 'Thread for input options')
    test_optionT.start()
    plannerT = PlannerThread(20, "Thread for input options", test_optionT)
    plannerT.start()

    plannerT.hl_start, plannerT.hl_end = pre_load.hl_start, pre_load.hl_end


