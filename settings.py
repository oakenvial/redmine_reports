from datetime import date, timedelta

# All capitalized variables used in the project are declared here.
# [REDMINE]

# [Required]
# Parameters used to connect to Redmine server

# Redmine URL
REDMINE_URL = 'http://www.redmine.org'

# Redmine API Key
REDMINE_KEY = ''

# [Optional]
# Other settings, default values provided

# Suppress warnings. requests lib will raise warnings if the certificate used for connection is not valid.
SUPPRESS_WARNINGS = True

# Path to the certificate. If SUPPRESS_WARNINGS = False, it will be used by python-redmine.
# certifi or other modules can be imported to specify this
CERT_PATH = ''

# Dictionary of activity override settings (depending on the role)
# Example of key-value pair: ('Developer', 'Testing'): 'Development'
ROLE_ACT_EXCEPTIONS = {}

# Activities that should be excluded from the report
EXCLUDED_ACTIVITIES = {}

# Number of days as timedelta from today in the past for getting time entries
NUM_DAYS = 30

# Alternative way to specify time period is to assign values to TO_DATE and FROM_DATE.
# In this case NUM_DAYS will be ignored.
TO_DATE = date.today()
FROM_DATE = date.today() - timedelta(days=NUM_DAYS)

# Report filename
FILENAME = 'redmine_report_{}_{}.pdf'.format(FROM_DATE, TO_DATE)

# Report language. Options: 'RU', 'EN'
LANG = 'EN'

# Text strings used in the resulting pdf reports
REPORT_MESSAGES = {'resource_info': {'RU': 'Информация по ресурсам за период времени с {} до {}',
                                     'EN': 'Information about resources for time period: {} to {}'},
                   'project_spent_time': {'RU': 'Время, затраченное на проекты в целом (задача не указана):',
                                          'EN': 'Time spent on projects (issue not specified)'},
                   'root_issues_spent_time': {'RU': 'Суммарное время, затраченное на корневые задачи по проектам:',
                                              'EN': 'Total time spent on project''s root issues'},
                   'project': {'RU': 'Проект',
                               'EN': 'Project'},
                   'total': {'RU': 'Всего: ',
                             'EN': 'Total: '},
                   }
