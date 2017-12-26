from __future__ import print_function

import invariant_finder
import mip_invariant_finder
import options
import pddl
import timers
import mip
import exactly_groups
from collections import defaultdict


DEBUG = False


def expand_group(group, task, reachable_facts):
    result = []
    for fact in group:
        try:
            pos = list(fact.args).index("?X")
        except ValueError:
            result.append(fact)
        else:
            # NOTE: This could be optimized by only trying objects of the correct
            #       type, or by using a unifier which directly generates the
            #       applicable objects. It is not worth optimizing this at this stage,
            #       though.
            for obj in task.objects:
                newargs = list(fact.args)
                newargs[pos] = obj.name
                atom = pddl.Atom(fact.predicate, newargs)
                if atom in reachable_facts:
                    result.append(atom)
    return result

def instantiate_groups(groups, task, reachable_facts):
    return [expand_group(group, task, reachable_facts) for group in groups]

class GroupCoverQueue:
    def __init__(self, groups):
        if groups:
            self.max_size = max([len(group) for group in groups])
            self.groups_by_size = [[] for i in range(self.max_size + 1)]
            self.groups_by_fact = {}
            for group in groups:
                group = set(group) # Copy group, as it will be modified.
                self.groups_by_size[len(group)].append(group)
                for fact in group:
                    self.groups_by_fact.setdefault(fact, []).append(group)
            self._update_top()
        else:
            self.max_size = 0
    def __bool__(self):
        return self.max_size > 1
    __nonzero__ = __bool__
    def pop(self):
        result = list(self.top) # Copy; this group will shrink further.
        if options.use_partial_encoding:
            for fact in result:
                for group in self.groups_by_fact[fact]:
                    group.remove(fact)
        self._update_top()
        return result
    def _update_top(self):
        while self.max_size > 1:
            max_list = self.groups_by_size[self.max_size]
            while max_list:
                candidate = max_list.pop()
                if len(candidate) == self.max_size:
                    self.top = candidate
                    return
                self.groups_by_size[len(candidate)].append(candidate)
            self.max_size -= 1

def choose_groups(groups, reachable_facts):
    queue = GroupCoverQueue(groups)
    uncovered_facts = reachable_facts.copy()
    result = []
    while queue:
        group = queue.pop()
        uncovered_facts.difference_update(group)
        result.append(group)
    print(len(uncovered_facts), "uncovered facts")
    result += [[fact] for fact in uncovered_facts]
    return result

def build_translation_key(groups):
    group_keys = []
    for group in groups:
        group_key = [str(fact) for fact in group]
        if len(group) == 1:
            group_key.append(str(group[0].negate()))
        else:
            group_key.append("<none of those>")
        group_keys.append(group_key)
    return group_keys

def collect_all_mutex_groups(groups, atoms):
    # NOTE: This should be functionally identical to choose_groups
    # when partial_encoding is set to False. Maybe a future
    # refactoring could take that into account.
    all_groups = []
    uncovered_facts = atoms.copy()
    for group in groups:
        uncovered_facts.difference_update(group)
        all_groups.append(group)
    all_groups += [[fact] for fact in uncovered_facts]
    return all_groups

def sort_groups(groups):
    return sorted(sorted(group) for group in groups)

# def is_group_useful(group,atoms):
#     for item in group:
#         if not item in atoms:
#             return False
#     return True

def compute_groups(task, atoms, reachable_action_params,actions,axioms):

    print(options.invariant)
    if options.invariant == 'mip':
        groups = mip_invariant_finder.get_groups(task,reachable_action_params,atoms,actions)
    else:
        groups = invariant_finder.get_groups(task, reachable_action_params)
        
        with timers.timing("Instantiating groups"):
            groups = instantiate_groups(groups, task, atoms)
#         groups = [group for group in groups if is_group_useful(group,atoms)]

    # Sort here already to get deterministic mutex groups.
    groups = sort_groups(groups)
    # TODO: I think that collect_all_mutex_groups should do the same thing
    #       as choose_groups with partial_encoding=False, so these two should
    #       be unified.
    with timers.timing("Collecting mutex groups"):
        mutex_groups = collect_all_mutex_groups(groups, atoms)

    inessentials = defaultdict(list)
    if options.group_choice == 'exact':
        with timers.timing("Choosing groups", block=True):
            essentials = mip.choose_groups_exact(groups, atoms)
    elif options.group_choice == 'essential':
        with timers.timing("Computing exactly groups", block=True):
            exactly1 = exactly_groups.compute_groups(task,actions,mutex_groups)
        with timers.timing("Choosing groups", block=True):
            essentials,inessentials = mip.choose_groups_essential_exact(mutex_groups,exactly1,atoms)
    else:
        with timers.timing("Choosing groups", block=True):
            essentials = choose_groups(groups, atoms)
    groups = essentials + [[item] for item in inessentials.keys()]

    if options.group_choice == 'essential' and options.axiom:
        task.init = [item for item in task.init if  not isinstance(item,pddl.Assign) and not item in inessentials ]
        actions = [action.filt(inessentials) for action in actions]
        for k,v in inessentials.items():
            if len(v) <= 1:
                axiom = pddl.PropositionalAxiom(k,[],k)
                axioms.append(axiom)
                continue
            neg = pddl.Atom("neg-" + k.predicate,k.args)
            groups.append([neg])
            atoms.add(neg)
            for atom in v:
                neg_axiom = pddl.PropositionalAxiom(neg,[atom],neg)
                axiom = pddl.PropositionalAxiom(k,[neg.negate()],k)
                axioms.append(neg_axiom)
                axioms.append(axiom)

    groups = sort_groups(groups)
#     for item in groups:
#         print(item)
    with timers.timing("Building translation key"):
        translation_key = build_translation_key(groups)

    if DEBUG:
        for group in groups:
            if len(group) >= 2:
                print("{%s}" % ", ".join(map(str, group)))
    return groups, mutex_groups, translation_key,(inessentials)
