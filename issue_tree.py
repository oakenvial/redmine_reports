"""Module containing IssueTree, IssueNode classes for storing information about bugtracker issues."""

from collections import defaultdict
from functools import partial


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
        self.store = defaultdict(partial(defaultdict, int))
        self.children = []

    def add_data(self, user, activity, hours):
        """Update an issue node with new time entry data."""
        self.store[user][activity] += hours

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

    def init_node(self, issue_id, subject, parent=None) -> IssueNode:
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

    def __str__(self) -> str:
        roots_str = ''
        for root in self.roots:
            roots_str += root.__str__()
        return roots_str
