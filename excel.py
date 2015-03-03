import os
from datetime import datetime, date
from time import time

import xlwt
from nose.exc import SkipTest
from nose.plugins.base import Plugin


SYMBOL_WIDTH = 256
CELL_MAX_WIDTH = 65535

DATETIME_FORMAT = '{0.day:0>2}.{0.month:0>2}.{0.year} {0.hour:0>2}:{0.minute:0>2}:{0.second:0>2}'.format

StatisticLabelStyle = xlwt.easyxf('alignment: horizontal left; font: bold 1')
StatisticValueStyle = xlwt.easyxf('alignment: horizontal left;')
TestTimeStyle = xlwt.easyxf('alignment: horizontal center;', num_format_str='0.000')
TestStatusStyle = xlwt.easyxf('alignment: horizontal left;')


def col_width(text_len):
    width = SYMBOL_WIDTH * text_len
    return CELL_MAX_WIDTH if width > CELL_MAX_WIDTH else width


def exc_message(exc_info):
    """Return the exception's message."""
    exc = exc_info[1]
    if exc is None:
        result = exc_info[0]
    else:
        result = str(exc)
    return result


def send_mail(
        from_,
        to_,
        subject,
        text,
        files=(),
        server="localhost",
        port=587,
        username='',
        password='',
        isTls=True):
    import smtplib
    from email import encoders
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email.utils import COMMASPACE, formatdate

    msg = MIMEMultipart()
    msg['From'] = from_
    msg['To'] = COMMASPACE.join(to_)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(file, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(file)))
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    if isTls:
        smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(from_, to_, msg.as_string())
    smtp.quit()


class Excel(Plugin):
    """This plugin provides test results in the standard Excel XLS file."""
    name = 'excel'

    def _timeTaken(self):
        taken = 0
        if hasattr(self, '_timer'):
            taken = time() - self._timer
        return taken

    def options(self, parser, env=os.environ):
        """Sets additional command line options."""
        super(Excel, self).options(parser, env=env)
        parser.add_option(
            '--excel-file', action='store',
            dest='excel_file', metavar='FILE',
            default=env.get('NOSE_EXCEL_FILE', 'nosetests.xls'),
            help=("Path to xls file to store the excel report in. "
                  "Default is nosetests.xls in the working directory "
                  "[NOSE_EXCEL_FILE]"))
        parser.add_option(
            '--excel-testsuite-name', action='store',
            dest='excel_testsuite_name', metavar="PACKAGE",
            default=env.get('NOSE_EXCEL_TESTSUITE_NAME', 'nosetests'),
            help=("Name of the testsuite in the xls, generated by plugin. "
                  "Default test suite name is nosetests."
                  "[NOSE_EXCEL_TESTSUITE_NAME]"))
        parser.add_option(
            '--smtp-server', action='store',
            dest='smtp_server', metavar="SMTP_SERVER",
            default=env.get('NOSE_EXCEL_SMTP_SERVER', 'smtp.gmail.com'),
            help=("Domain name or ip-address of SMTP server. "
                  "Default server is smtp.gmail.com "
                  "[NOSE_EXCEL_SMTP_SERVER]"))
        parser.add_option(
            '--smtp-port', action='store',
            dest='smtp_port', metavar="SMTP_PORT",
            default=env.get('NOSE_EXCEL_SMTP_PORT', 587),
            help=("Port of SMTP server. "
                  "Default port is 587 "
                  "[NOSE_EXCEL_SMTP_PORT]"))
        parser.add_option(
            '--smtp-user', action='store',
            dest='smtp_user', metavar="SMTP_USER",
            help="Username for connect to SMTP server.")
        parser.add_option(
            '--smtp-password', action='store',
            dest='smtp_password', metavar="SMTP_PASSWORD",
            help="Password for connect to SMTP server.")
        parser.add_option(
            '--mail-from', action='store',
            dest='mail_from', metavar="MAIL_FROM",
            help="Email sender.")
        parser.add_option(
            '--mail-to', action='store',
            dest='mail_to', metavar="MAIL_TO",
            help="List of mail recipients.")
        parser.add_option(
            '--mail-subject', action='store',
            dest='mail_subject', metavar="MAIL_SUBJECTS",
            default="Результаты проведения автоматизированного тестирования за %s" % date.today(),
            help="Email subject.")

    def configure(self, options, conf):
        """Configures the excel plugin."""
        super(Excel, self).configure(options, conf)
        if self.enabled:
            self.stats = {'errors': 0, 'failures': 0, 'passes': 0, 'skipped': 0}
            self.errorlist = []
            self.error_report_file_name = os.path.realpath(options.excel_file)
            self.excel_testsuite_name = options.excel_testsuite_name
            self.smtp_server = options.smtp_server
            self.smtp_port = int(options.smtp_port)
            self.smtp_user = options.smtp_user
            self.smtp_password = options.smtp_password
            self.mail_from = options.mail_from
            self.mail_to = options.mail_to
            self.mail_subject = options.mail_subject

    def begin(self):
        self.start_datetime = datetime.now()

    def beforeTest(self, test):
        """Initializes a timer before starting a test."""
        self._timer = time()

    def report(self, stream):
        """Writes an XLS file"""
        end_datetime = datetime.now()
        total = self.stats['errors'] + self.stats['failures'] + self.stats['passes'] + self.stats['skipped']

        book = xlwt.Workbook()
        sheet = book.add_sheet('Results')

        sheet.write(0, 0, 'Suite', StatisticLabelStyle)
        sheet.write(0, 1, self.excel_testsuite_name, StatisticValueStyle)

        sheet.write(2, 0, 'Start datetime', StatisticLabelStyle)
        sheet.write(2, 1, DATETIME_FORMAT(self.start_datetime), StatisticValueStyle)
        sheet.write(3, 0, 'End datetime', StatisticLabelStyle)
        sheet.write(3, 1, DATETIME_FORMAT(end_datetime), StatisticValueStyle)

        sheet.write(5, 0, 'Total', StatisticLabelStyle)
        sheet.write(5, 1, total, StatisticValueStyle)
        sheet.write(6, 0, 'Errors', StatisticLabelStyle)
        sheet.write(6, 1, self.stats['errors'], StatisticValueStyle)
        sheet.write(7, 0, 'Failures', StatisticLabelStyle)
        sheet.write(7, 1, self.stats['failures'], StatisticValueStyle)
        sheet.write(8, 0, 'Passes', StatisticLabelStyle)
        sheet.write(8, 1, self.stats['passes'], StatisticValueStyle)
        sheet.write(9, 0, 'Skipped', StatisticLabelStyle)
        sheet.write(9, 1, self.stats['skipped'], StatisticValueStyle)

        row = 11
        for e in self.errorlist:
            sheet.write(row, 0, e['datetime'], StatisticValueStyle)
            sheet.write(row, 1, e['test'])
            sheet.write(row, 2, e['time'], TestTimeStyle)
            sheet.write(row, 3, e['status'], TestStatusStyle)
            sheet.write(row, 4, e['msg'])
            row += 1

        sheet.col(0).width = col_width(len(DATETIME_FORMAT(self.start_datetime)))
        sheet.col(1).width = col_width(max(map(lambda o: len(str(o['test'])), self.errorlist)))
        sheet.col(2).width = col_width(len(DATETIME_FORMAT(self.start_datetime)))
        sheet.col(3).width = col_width(10)
        sheet.col(4).width = col_width(max(map(lambda o: len(str(o['msg'])), self.errorlist)))

        book.save(self.error_report_file_name)

        if self.mail_to:
            msg_body = \
                """
                Доброго времени суток!

                Результаты проведения автоматизированного тестирования
                Всего: {0}
                Ошибок: {1}
                Проваленых: {2}
                Успешных: {3}
                Пропущеных: {4}

                Подробный отчет прикреплен к письму ({5})
                """.format(
                    total,
                    self.stats['errors'],
                    self.stats['failures'],
                    self.stats['passes'],
                    self.stats['skipped'],
                    os.path.basename(self.error_report_file_name))
            send_mail(
                from_=self.mail_from,
                to_=self.mail_to.split(','),
                subject=self.mail_subject,
                text=msg_body,
                files=[self.error_report_file_name],
                server=self.smtp_server,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password)

    def addError(self, test, err):
        """Add error/skipped to report."""
        if issubclass(err[0], SkipTest):
            status = 'skipped'
            self.stats['skipped'] += 1
        else:
            status = 'error'
            self.stats['errors'] += 1

        self.errorlist.append({
            'datetime': DATETIME_FORMAT(datetime.now()),
            'test': str(test),
            'time': self._timeTaken(),
            'status': status,
            'msg': exc_message(err)})

    def addFailure(self, test, err):
        """Add failure to report."""
        self.stats['failures'] += 1
        self.errorlist.append({
            'datetime': DATETIME_FORMAT(datetime.now()),
            'test': str(test),
            'time': self._timeTaken(),
            'status': 'failure',
            'msg': exc_message(err)})

    def addSuccess(self, test):
        """Add success to report."""
        self.stats['passes'] += 1
        self.errorlist.append({
            'datetime': DATETIME_FORMAT(datetime.now()),
            'test': str(test),
            'time': self._timeTaken(),
            'status': 'ok',
            'msg': ''})
