from gurobipy import *
import pddl

def is_never_applicable(action):
    cond = {atom for atom in action.precondition if not atom.negated}
    add = {atom for _,atom in action.add_effects}
    del_cond = ([atom for _,atom in action.del_effects if atom in cond])
#     if(len(action.del_effects) > 0):
#         return False
    return add <= cond

def get_groups(task,reachable_action_params,atoms,actions):
    res = []

    var = {}
    m = Model("mip1")
    m.setParam(GRB.Param.Threads,1)

    for i,atom in enumerate(atoms):
        var[atom] = m.addVar(vtype=GRB.BINARY,name=str(atom))
#             var[atom] = m.addVar(vtype=GRB.BINARY,name="var"+str(i))

    m.update()

    obj = sum([v for v in var.values()])
    m.setObjective(obj, GRB.MAXIMIZE)

    init = [atom for atom in task.init if not isinstance(atom,pddl.Assign) and not atom.negated and atom in atoms]
    m.addConstr(sum([var[atom] for atom in init]) == 1)
    for action in actions:
#         if is_never_applicable(action):
#             continue
#         action.dump()
        cond = {atom for atom in action.precondition if not atom.negated}
        add = [var[atom] for _,atom in action.add_effects if not atom in cond]
        del_cond = [var[atom] for _,atom in action.del_effects if atom in cond]
        if len(add) < 1:
            continue
        m.addConstr(sum(add) <= sum(del_cond))


    while True:
        m.optimize()
#         m.write("out.lp")
#         print('Obj: %g' % m.objVal)

        if m.SolCount == 0:
            break
        mutex = [atom for atom,v in var.items() if v.x >= 1]
        if len(mutex) < 1:
            break
        m.addConstr(sum([var[atom] for atom in atoms if not atom in mutex]) >= 1)

        res.append(mutex)

    return res
