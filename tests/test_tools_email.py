"""Tests of the tools.email module."""
import textwrap

import dnstwister.tools.email as email_tools


def test_email_renderer():
    """Test the email rendering helper."""
    template = email_tools.render_email(
        'report.html',
        domain='www.example.com',
        updated_date='yesterday',
        new=(('www.examp1e.com', '127.0.0.1'),),
        updated=(('www.exampl3.com', '127.0.0.1', '127.0.0.2'),),
        deleted=('www.examplle.com',),
        unsubscribe_link='https://dnstwister.report/...',
    )

    assert template.strip() == textwrap.dedent("""
        <h1>dnstwister report for www.example.com</h1>
        <p>
            <a href="https://dnstwister.report/...">Unsubscribe</a>
        </p>
        <p>Here's your dnstwister report, updated yesterday.</p>
        <h2>New registrations</h2>
        <table>
            <thead>
                <tr>
                    <th>Registered Domain</th>
                    <th>Resolved IP</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>www.examp1e.com</td>
                    <td>127.0.0.1</td>
                </tr>
            </tbody>
        </table>
        <h2>Updated registrations</h2>
        <table>
            <thead>
                <tr>
                    <th>Registered Domain</th>
                    <th>Previously Resolved IP</th>
                    <th>Currently Resolved IP</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>www.exampl3.com</td>
                    <td>127.0.0.1</td>
                    <td>127.0.0.2</td>
                </tr>
            </tbody>
        </table>
        <h2>Deleted registrations</h2>
        <table>
            <thead>
                <tr>
                    <th>Previously Registered Domain</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>www.examplle.com</td>
                </tr>
            </tbody>
        </table>

        <p>
            <a href="https://dnstwister.report/...">Unsubscribe</a>
        </p>
    """).strip()
