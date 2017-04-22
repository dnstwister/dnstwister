"""Write out email examples to disk to easily review."""
from dnstwister.domain.email_report import EmailReport
import dnstwister.tools.email as email_tools


# Brings it a little closer to the gmail style.
FORMATTING = """
<style type="text/css">
    * {
        font-family: sans-serif;
    }
</style>
"""

def test_generate_example_email():
    """Generic email report."""
    new = (
        ('www.examp1e.com', '127.0.0.1'),
    )
    updated = (
        ('www.exampl3.com', '127.0.0.1', '127.0.0.2'),
    )
    deleted = (
        'www.examplle.com',
        'www.eeexamplez.com',
        'wwwexample.com',
    )
    noisy = (
        'www.examplle.com',
    )

    delta_report = {
        'new': new,
        'updated': updated,
        'deleted': deleted,
    }

    report = EmailReport(delta_report, noisy, include_noisy_domains=True)

    template = email_tools.render_email(
        'report.html',
        domain='www.example.com',
        report=report,
        unsubscribe_link='https://dnstwister.report/...',
    )

    with open('tests/manual/example_email.html', 'wb') as email_f:
        email_f.write(FORMATTING)
        email_f.write(template)


def test_generate_example_noisy_not_included():
    """Noisy domains, but they are not included."""
    new = (
        ('www.examp1e.com', '127.0.0.1'),
    )
    updated = (
        ('www.exampl3.com', '127.0.0.1', '127.0.0.2'),
    )
    deleted = (
        'www.examplle.com',
        'www.eeexamplez.com',
        'wwwexample.com',
    )
    noisy = (
        'www.examplle.com',
    )

    delta_report = {
        'new': new,
        'updated': updated,
        'deleted': deleted,
    }

    report = EmailReport(delta_report, noisy, include_noisy_domains=False)

    template = email_tools.render_email(
        'report.html',
        domain='www.example.com',
        report=report,
        unsubscribe_link='https://dnstwister.report/...',
    )

    with open('tests/manual/example_email_noisy_excluded.html', 'wb') as email_f:
        email_f.write(FORMATTING)
        email_f.write(template)



def test_generate_example_email_no_noisy():
    """Email when no noisy domains."""
    new = (
        ('www.examp1e.com', '127.0.0.1'),
    )
    updated = (
        ('www.exampl3.com', '127.0.0.1', '127.0.0.2'),
    )
    deleted = (
        'www.examplle.com',
        'www.eeexamplez.com',
        'wwwexample.com',
    )
    noisy = set()

    delta_report = {
        'new': new,
        'updated': updated,
        'deleted': deleted,
    }

    report = EmailReport(delta_report, noisy, include_noisy_domains=True)

    template = email_tools.render_email(
        'report.html',
        domain='www.example.com',
        report=report,
        unsubscribe_link='https://dnstwister.report/...',
    )

    with open('tests/manual/example_email_no_noisy.html', 'wb') as email_f:
        email_f.write(FORMATTING)
        email_f.write(template)


def test_generate_example_all_noisy():
    """Email when just noisy domains."""
    new = set()
    updated = set()
    deleted = set()
    noisy = (
        'www.examplle.com',
        'www.eeexamplez.com',
        'wwwexample.com',
    )

    delta_report = {
        'new': new,
        'updated': updated,
        'deleted': deleted,
    }

    report = EmailReport(delta_report, noisy, include_noisy_domains=True)

    template = email_tools.render_email(
        'report.html',
        domain='www.example.com',
        report=report,
        unsubscribe_link='https://dnstwister.report/...',
    )

    with open('tests/manual/example_email_all_noisy.html', 'wb') as email_f:
        email_f.write(FORMATTING)
        email_f.write(template)
