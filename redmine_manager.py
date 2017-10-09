from redminelib import Redmine
from settings import *
from issue_tree import IssueTree
from operator import add
from decorators import timetrack, suppress_warnings
from collections import defaultdict
from functools import partial


class RedmineProject:
    """Class RedmineProject for storing time entries and dictionaries connected with the project."""
    def __init__(self, project):
        self.project = project
        self.name = project.name
        self.time_entries = defaultdict(partial(defaultdict, int))
        self.issues = []
        self.issue_tree = None
        self.issue_tables_gen = None
        self.user_roles = {}  # Username: {set of roles} pairs


class RedmineManager:
    """Class RedmineManager for storing information about certain Redmine resources."""

    def __init__(self):
        self.redmine = None
        self.activities = None
        self.reported_activities = None
        self.roles = None
        self.role_act_map = None
        self.projects = []  # List of RedmineProject objects
        self.from_date = None
        self.to_date = None

    def set_time_interval(self, from_date, to_date):
        """Set time boundaries for time tracking."""
        self.from_date = from_date
        self.to_date = to_date

    @suppress_warnings
    def connect(self, url=REDMINE_URL, api_key=REDMINE_KEY):
        """Connect to Redmine."""
        verify = False if SUPPRESS_WARNINGS else CERT_PATH
        self.redmine = Redmine(url=url,
                               key=api_key,
                               requests={'verify': verify})

    @suppress_warnings
    @timetrack('Getting roles and activities')
    def get_roles(self):
        """Get lists of roles and activties, create (role, activity) -> new_activity mapping."""
        # All Redmine user activities
        self.activities = [activity.name for activity in
                           self.redmine.enumeration.filter(resource='time_entry_activities')]
        # ALl Redmine user roles
        self.roles = [role.name for role in self.redmine.role.all()]
        # Role-activity mapping that enables activity override. Default: nothing is overriden
        self.role_act_map = {(role, activity): activity for role in self.roles for activity in self.activities}
        # For some (role, activity) pairs the resulting activity in the report may be different
        for exception in ROLE_ACT_EXCEPTIONS.keys():
            self.role_act_map[exception] = ROLE_ACT_EXCEPTIONS[exception]
        # A subset of all activities used for reporting
        self.reported_activities = [activity for activity in self.activities if activity not in EXCLUDED_ACTIVITIES]

    @suppress_warnings
    @timetrack('Getting projects')
    def get_projects(self):
        """Get all Redmine projects, including project memberships."""
        for project in self.redmine.project.all():
            self.projects.append(RedmineProject(project))
            for pm in project.memberships:
                if hasattr(pm, 'user') and hasattr(pm, 'roles'):
                    self.projects[-1].user_roles[pm.user.name] = {role.name for role in pm.roles if hasattr(role, 'name')}

    @suppress_warnings
    @timetrack('Getting time entries for all projects')
    def get_project_time(self):
        """Get project spent time."""
        for project in self.projects:
            time_entries = self.redmine.time_entry.filter(project_id=project.name,
                                                          subproject_id='!*',  # Not in a subproject
                                                          from_date=self.from_date,
                                                          to_date=self.to_date)
            for entry in time_entries:
                # Time spent on the project (and not its issues)
                set_of_roles = project.user_roles[entry.user.name]
                resulting_activity = self.calculate_activity(set_of_roles, entry.activity.name)
                if not hasattr(entry, 'issue'):
                    project.time_entries[entry.user.name][resulting_activity] += entry.hours

    @suppress_warnings
    @timetrack('Getting issue time entries')
    def get_issues(self):
        """Get Redmine issues."""
        for project in self.projects:
            project.issues = list(self.redmine.issue.filter(project_id=project.name,
                                                            subproject_id='!*',  # Not in a subproject
                                                            parent_id='!*',  # Is root
                                                            status_id='*'))  # Get issues in any status
            project.issue_tree = IssueTree()
            for issue in project.issues:
                print('.', end='', flush=True)
                project.issue_tree = self.walk(tree=project.issue_tree,
                                               issue_id=issue.id,
                                               subject=issue.subject,
                                               parent=None,
                                               level=0,
                                               project=project)
            project.issue_tables_gen = ((root.subject,
                                         self.gen_report_table(label='#' + str(root.issue_id), dictionary=root.store)
                                         )
                                         for root in project.issue_tree.roots
                                         if root.store)  # If there are any time entries
            print()

    def gen_report_table(self, label, dictionary) -> list:
        """Generate reports table based on dictionary.

        Inputs:
            label - project name or issue id or any other label
            dictionary - time entries dictionary, format:
                {username: {activity: hours}}
        Outputs:
            table - table ready to be added to the report, format:
                [[1, 2, 3],
                 [4, 5, 6],
                 [7, 8, 9]]
        """
        headers = [label, *self.reported_activities]
        data = []
        total = [0] * len(self.reported_activities)
        for user in dictionary.keys():
            row = [user]
            for activity in self.reported_activities:
                row.append(round(dictionary[user][activity], 3) if activity in dictionary[user].keys() else 0)
            data.append(row)
            total = list(map(add, total, row[1:]))
        table = [headers] + data + [[REPORT_MESSAGES['total'][LANG]] + total]
        return table

    def walk(self, tree, issue_id, subject, parent, level, project) -> IssueTree:
        """Walk the issue tree in Redmine constructing IssueTree object in the process.

        tree - IssueTree object
        issue_id - id of the current issue
        parent - parent IssueNode object
        level - level up to which the tree needs to be constructed (root level is 0)
        project - RedmineProject object
        """
        node = tree.init_node(issue_id, subject, parent)
        time_entries = self.redmine.time_entry.filter(issue_id=issue_id,
                                                      from_date=self.from_date,
                                                      to_date=self.to_date)
        for entry in time_entries:
            set_of_roles = project.user_roles[entry.user.name]
            resulting_activity = self.calculate_activity(set_of_roles, entry.activity.name)
            node.add_data(user=entry.user.name,
                          activity=resulting_activity,
                          hours=entry.hours)
        if node.level < level:
            issues = self.redmine.issue.filter(parent_id=issue_id,
                                               status_id='*')
            for issue in issues:
                self.walk(tree=tree,
                          issue_id=issue.id,
                          subject=issue.subject,
                          parent=node,
                          level=level,
                          project=project)
        return tree

    def calculate_activity(self, set_of_roles, activity) -> str:
        """Calculates the resulting activity depending on the role.

        settings.py contains ROLE_ACT_EXCEPTIONS, which enables override of some activities by others.
        """
        allowed_activities = {self.role_act_map[(role, activity)] for role in set_of_roles}
        if activity in allowed_activities:
            return activity
        else:
            priority_role = max(set_of_roles, key=len)
            return self.role_act_map[(priority_role, activity)]
