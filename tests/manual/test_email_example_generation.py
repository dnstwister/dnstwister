"""Write out an email to disk to easily review."""
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
    """Not actually a test, but it is nice to write out an example email."""
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

    report = EmailReport(new, updated, deleted, noisy)

    template = email_tools.render_email(
        'report.html',
        domain='www.example.com',
        report=report,
        unsubscribe_link='https://dnstwister.report/...',
    )

    with open('tests/manual/example_email.html', 'wb') as email_f:
        email_f.write(FORMATTING)
        email_f.write(template)
