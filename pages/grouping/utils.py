# find all children nodes
def find_leaf_nodes(obj):
    leaves = []
    if isinstance(obj, dict):
        for value in obj.values():
            leaves.extend(find_leaf_nodes(value))
    elif isinstance(obj, list):
        for item in obj:
            leaves.extend(find_leaf_nodes(item))
    else:
        leaves.append(obj)
    return leaves
