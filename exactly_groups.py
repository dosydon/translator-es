from collections import defaultdict
import pddl
def compute_groups(task,actions,mutex_groups):
    result = []
    threats = defaultdict(set)
    for action in actions:
        for cond,atom in action.del_effects:
            threats[atom].add(action)

    for invariant in mutex_groups:
        if not is_hold_init(invariant,task.init):
            continue
        if is_balanced(invariant,threats):
            result.append(invariant)
    return result

def is_hold_init(invariant,init):
    init = [fact for fact in init if not isinstance(fact,pddl.Assign)]
    for fact in invariant:
        if fact in init:
            return True
    return False

def is_balanced(invariant,threats):
        for atom in invariant:
            for threat in threats[atom]:
                if count_add(invariant,threat) < 1:
                    return False
        return True

def count_add(invariant,op):
    add_effects = set([atom for cond,atom in op.add_effects])
    return len([atom for atom in invariant if atom in add_effects])

