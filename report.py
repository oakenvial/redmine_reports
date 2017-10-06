from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from os import path


class Report:
    """Report class for operating Redmine reports.

    Provides some basic settings for report generation."""

    def __init__(self):
        self.doc = None
        self.elements = []
        self.table_style = None
        self.header_style = None
        self.text_style = None

    def assign_styles(self):
        self.table_style = TableStyle([('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.aliceblue, colors.white]),
                                       ('TEXTCOLOR', (0, 0), (-1, 0), colors.grey),  # First row
                                       ('TEXTCOLOR', (0, -1), (-1, -1), colors.blueviolet),  # Last row
                                       ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),  # Rows in the middle
                                       ('FONT', (0, 0), (-1, -1), 'FreeSans', 8),
                                       ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Align numbers
                                       ('BACKGROUND', (0, -1), (-1, -1), colors.white),
                                       ('LINEABOVE', (0, -1), (-1, -1), 0.5, colors.lightgrey),
                                       ]
                                      )
        self.header_style = TableStyle([('FONT', (0, 0), (-1, -1), 'FreeSans', 9),
                                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkblue),
                                        ]
                                       )
        self.text_style = getSampleStyleSheet()

    def create(self, filename='redmine_report.pdf', pagesize=A4):
        """Create report."""
        self.doc = SimpleDocTemplate(filename=filename,
                                     pagesize=pagesize,
                                     title='Redmine report',
                                     leftMargin=0.6*inch,
                                     rightMargin=0.6*inch,
                                     topMargin=0.25*inch,
                                     bottomMargin=0.25*inch
                                     )
        pdfmetrics.registerFont(TTFont('FreeSans', path.join('fonts', 'FreeSans.ttf')))
        self.assign_styles()

    def add_table(self, table):
        """Add new table to the report."""
        tb = Table(table, colWidths=[110] + [None] * (len(table[0]) - 1))
        tb.setStyle(self.table_style)
        self.elements.append(tb)

    def add_header(self, header):
        """Add header table row."""
        hd = Table([[header]])
        hd.setStyle(self.header_style)
        self.elements.append(hd)

    def build(self):
        """Write the report to disk."""
        self.doc.build(self.elements)

    def add_text(self, text, header=None, space_after=None):
        """Add a new text paragraph."""
        if not header:
            style = self.text_style['Normal']
        else:
            style = self.text_style['Heading' + str(header)]
        par = Paragraph('<font name="FreeSans">' + text + '</font>', style)
        self.elements.append(par)
        if space_after:
            self.add_space(num_inches=space_after)

    def add_space(self, num_inches=0.2):
        """Add empty vertical space."""
        self.elements.append(Spacer(1, num_inches * inch))
