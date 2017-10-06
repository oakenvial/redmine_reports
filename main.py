from settings import *
from report import Report
from redmine_manager import RedmineManager
from datetime import date, timedelta


if __name__ == '__main__':
    rmman = RedmineManager()
    rmman.connect()
    if TO_DATE and FROM_DATE:
        rmman.set_time_interval(from_date=FROM_DATE,
                                to_date=TO_DATE)
    else:
        rmman.set_time_interval(from_date=date.today() - timedelta(days=NUM_DAYS),
                                to_date=date.today())

    rmman.get_roles()  # Get role and activity information, process exceptions defined in settings
    rmman.get_projects()  # Get all projects
    rmman.get_project_time()  # Get project time entries for each project

    report = Report()  # Initialize the report
    report.create(filename=FILENAME)

    report.add_text(text='Redmine',
                    header=1,
                    space_after=0.05)
    report.add_text(text=REPORT_MESSAGES['resource_info'][LANG].format(rmman.from_date, rmman.to_date),
                    space_after=0.2)
    report.add_text(text=REPORT_MESSAGES['project_spent_time'][LANG],
                    space_after=0.2)

    for project in rmman.projects:
        table = rmman.gen_report_table(label=project.name,
                                       dictionary=project.time_entries)
        report.add_table(table)
        report.add_space()

    report.add_space()
    report.add_text(REPORT_MESSAGES['root_issues_spent_time'][LANG],
                    space_after=0.05)

    rmman.get_issues()
    for project in rmman.projects:
        report.add_text(text=REPORT_MESSAGES['project'][LANG] + ' ' + project.name,
                        header=2,
                        space_after=0.1)
        for issue_table in project.issue_tables_gen:
            report.add_header(issue_table[0])  # Issue subject used as a header
            report.add_table(issue_table[1])  # Data table
            report.add_space()

    report.build()
    print('Report generated.')
