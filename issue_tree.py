"""Module containing IssueTree, IssueNode classes for storing information about bugtracker issues."""


class IssueNode:
    """Class IssueNode.

       issue_id - id of the bugtracker issue associated with the node
       store - dictionary for {user: {activity: hours}} structure
       parent - parent IssueNode
       children - list of child IssueNodes
       level - level in the hierarchy, root IssueNodes have level=0
    """
    def __init__(self, issue_id, subject, parent):
        self.parent = parent
        if parent:
            self.level = parent.level + 1
        else:
            self.level = 0
        self.issue_id = issue_id
        self.subject = subject
        self.store = {}
        self.children = []

    def add(self, user, activity, hours):
        """Add new or existing data to the node."""
        if user in self.store.keys():
            if activity in self.store[user].keys():  # This activity already recorded for user
                self.store[user][activity] += hours
            else:  # New activity for this user
                self.store[user][activity] = hours
        else:  # New user
            self.store[user] = {activity: hours}

    def __str__(self):
        children_str = ''
        for child in self.children:
            children_str += '\n' + child.__str__()
        return '--'*self.level + '|' + str(self.issue_id) + '| ' + self.store.__str__() + '\n' + children_str


class IssueTree:
    """IssueTree class for storing data associated with bugtracker issues.

       roots - list of all root elements (class IssueNode)
       leaves - list of all leaf elements (class IssueNode)
    """
    def __init__(self):
        self.roots = []
        self.leaves = []

    def init_node(self, issue_id, subject, parent=None):
        """Initialize a new node."""
        if parent:  # Parent issue exists
            parent.children.append(IssueNode(issue_id=issue_id,
                                             subject=subject,
                                             parent=parent))
            if parent in self.leaves:
                self.leaves.remove(parent)
            self.leaves.append(parent.children[-1])
            return parent.children[-1]
        else:  # No parent issue
            new_root = IssueNode(issue_id=issue_id,
                                 subject=subject,
                                 parent=parent)
            self.roots.append(new_root)
            self.leaves.append(new_root)
            return new_root

    def add_data(self, node, user, activity, hours):
        """Update an issue node with new time entry data."""
        node.add(user, activity, hours)
        return node

    def __str__(self):
        roots_str = ''
        for root in self.roots:
            roots_str += root.__str__()
        return roots_str
