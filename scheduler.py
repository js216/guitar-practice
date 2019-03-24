import os
import json
import time
import random
import logging
import configparser

def create_items(config, sections, all_items=[]):
    # stop recursion when it runs out of sections
    if not sections:
        return all_items

    # deal with the first of the remaining sections
    sect = sections.pop(0)
    items = []
    for key, val in config.items(sect):
        # for items with no subitems
        if val == "":
            items.append(sect+":"+key)

        # for subitems
        else:
            for sub_key in val.split(","):
                items.append(sect+":"+key+":"+sub_key.strip())

    # do a Cartesian product
    if not all_items:
        all_items = items
    else:
        all_items = [x+":"+y for x in all_items for y in items]

    # recursively deal with the next section
    return create_items(config, sections, all_items)

def read_syllabus():
    # read dict for all practice items if possible, else create a new one
    try:
        with open("practice_log.json", "r") as f:
            practice_log = json.load(f)
    except IOError:
        practice_log = {}

    # read all syllabus files
    for fname in os.listdir("syllabus/"):
        if fname[-4:] != ".ini":
            continue
        config = configparser.ConfigParser()
        config.read("syllabus/"+fname)
        for item in create_items(config, config.sections()):
            practice_log.setdefault(fname+":"+item, {})

    # write to file
    with open('practice_log.json', 'w') as f:
        json.dump(practice_log, f, sort_keys=True, indent=4)

def write_log(new, learning, already_learned):
    with open('practice_log.json', 'w') as f:
        practice_log = {**new, **learning, **already_learned}
        json.dump(practice_log, f, sort_keys=True, indent=4)

def do_practice():
    # read dict with practice items
    try:
        with open("practice_log.json", "r") as f:
            practice_log = json.load(f)
    except IOError:
        logging.error("Error: Practice log not found.")
        return

    # separate items into new, learning, and already learned
    new, learning, already_learned = {}, {}, {}
    for key, val in practice_log.items():
        if not val:
            new[key] = {}
        elif val["current"] < val["goal"]:
            learning[key] = val
        elif val["current"] >= val["goal"]:
            already_learned[key] = val

    # randomize new items
    sorted_new_keys = list(new.keys())
    random.shuffle(sorted_new_keys)
    new = {key:new[key] for key in sorted_new_keys}

    # sort items currently learning by how far away from the goal they are
    sorted_learning_keys = sorted(
            learning,
            key=lambda k: learning[k]['current']/learning[k]["goal"]
        )
    learning = {key:learning[key] for key in sorted_learning_keys}

    # sort already learned items by how recently they were practiced
    sorted_already_learned_keys = sorted(
            already_learned,
            key=lambda k: already_learned[k]['history'][-1][0]
        )
    already_learned = {key:already_learned[key] for key in sorted_already_learned_keys}

    # for counting how many items done so far
    i = 0

    ## practice the items currently learning
    #for key, val in learning.items():
    #    # ask for how well the user did this time
    #    print(key)
    #    print("goal = ", val["goal"])
    #    print("past = ", val["current"])
    #    val["current"] = int(input("current: "))
    #    i += 1
    #    print(i, " items done so far.\n")

    #    # write to file
    #    val["history"].append((time.time(), val["current"]))
    #    write_log(new, learning, already_learned)

    # practice new items
    for key, val in new.items():
        # ask for goal and how well the user did this time
        print(key)
        val["goal"] = int(input("goal: "))
        val["current"] = int(input("current: "))
        val["history"] = [(time.time(), val["current"])]
        write_log(new, learning, already_learned)
        i += 1
        print(i, " items done so far.\n")

    # practice the items already learned
    for key, val in already_learned.items():
        # ask for how well the user did this time
        print(key)
        print("goal = ", val["goal"])
        val["current"] = int(input("current: "))
        i += 1
        print(i, " items done so far.\n")

        # write to file
        val["history"].append((time.time(), val["current"]))
        write_log(new, learning, already_learned)


if __name__ == "__main__":
    read_syllabus()
    do_practice()
