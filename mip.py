
from gurobipy import *
from collections import defaultdict
def choose_groups_exact(groups, reachable_facts):
    coverable_facts = set()
    for group in groups:
        coverable_facts.update(group)
    uncovered_facts = reachable_facts - coverable_facts
    print(len(uncovered_facts), "uncovered facts")

    try:
        choice_var = {}
        hit_set = defaultdict(set)

        # Create a new model
        m = Model("mip1")
        m.setParam(GRB.Param.Threads,1)

        for i,group in enumerate(groups):
            group = tuple(group)
            choice_var[group] = m.addVar(vtype=GRB.BINARY,name=str("group" + str(i)))
            for fact in group:
                hit_set[fact].add(group)

        # Integrate new variables
        m.update()

        obj = sum([var for var in choice_var.values()])
        # Set objective
        m.setObjective(obj, GRB.MINIMIZE)

        for fact in coverable_facts:
            cst = sum([choice_var[group] for group in hit_set[fact]])
            m.addConstr(cst >= 1)

        # Add constraint: x + y >= 1
#         m.addConstr(x + y >= 1, "c1")

        m.optimize()

        result = []
        covered_facts = set()
        for group,v in choice_var.items():
            if v.x >=1:
                tmp = []
                for item in group:
                    if not item in covered_facts:
                        tmp.append(item)
                covered_facts.update(group)
                result.append(tmp)

        print('Obj: %g' % m.objVal)

        result += [[fact] for fact in uncovered_facts]
        return result

    except GurobiError as e:
        print('Error reported')
        print(e.message)

def choose_groups_essential_exact(groups, exactly1,reachable_facts):
    groups = sorted(([tuple(group) for group in groups]))
    exactly1 = sorted(([tuple(group) for group in exactly1]))
    coverable_facts = set()
    for group in groups:
        coverable_facts.update(group)
    uncovered_facts = reachable_facts - coverable_facts
#     for atom in coverable_facts:
#         print(atom)
    print(len(uncovered_facts), "uncovered facts")
    result = []

    try:
        choice_group = {}
        choice_delete = {}
        choice_to_group = {}
        hit_set = defaultdict(set)

        # Create a new model
        m = Model("mip1")
        m.setParam(GRB.Param.Threads,1)

        for i,group in enumerate(groups):
            choice_group[group] = m.addVar(vtype=GRB.BINARY,name=str("group" + str(i)))

        for i,group in enumerate(exactly1):
            for fact in group:
                if not fact in choice_delete:
                    choice_delete[fact] = m.addVar(vtype=GRB.BINARY,name=str("exactly_group" + str(i) + str(fact)))

        m.update()

        for i,group in enumerate(groups):
            for fact in sorted(group):
                hit_set[fact].add(choice_group[group])
        for i,group in enumerate(exactly1):
            for fact in sorted(group):
                choice_to_group.setdefault(fact,group)
                hit_set[fact].add(choice_delete[fact])

        obj = (len(exactly1) + 1) * sum([var for var in sorted(choice_group.values())]) + sum([var for var in sorted(choice_delete.values())])
#         print(obj)
        # Set objective
        m.setObjective(obj, GRB.MINIMIZE)

        for fact in sorted(coverable_facts):
            cst = sum([var for var in sorted(hit_set[fact])])
#             cst += sum(choice_delete[group][fact] for group,fact in hit_set_delete[fact])
            m.addConstr(cst >= 1)
        for group in exactly1:
            cst = sum([choice_delete[fact] for fact in sorted(group)])
            m.addConstr(cst <= 1)

        m.optimize()

        essentials = []
        inessentials = defaultdict(list)
        covered_facts = set()

        for fact in sorted(choice_delete):
            v = choice_delete[fact]
            if v.x >=1:
                other = [item for item in choice_to_group[fact] if not item == fact]
                covered_facts.add(fact)
                inessentials[fact]=other

        for group in sorted(choice_group):
            v = choice_group[group]
            if v.x >=1:
                mutex = []
                for item in group:
                    if not item in covered_facts:
                        mutex.append(item)
                covered_facts.update(group)
                essentials.append(mutex)
#
        print('Obj: %g' % m.objVal)
        essentials += [[fact] for fact in uncovered_facts]
        return essentials,inessentials
#

    except GurobiError as e:
        print('Error reported')
        print(e.message)
