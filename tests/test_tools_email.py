"""Tests of the tools.email module."""
import textwrap

import dnstwister.tools.email as email_tools


def test_email_renderer():
    """Test the email rendering helper."""
    template = email_tools.render_email(
        'report.html',
        domain='www.example.com',
        new=(('www.examp1e.com', '127.0.0.1', 'http://dnstwister.report/analyse/1234'),),
        updated=(('www.exampl3.com', '127.0.0.1', '127.0.0.2', 'http://dnstwister.report/analyse/6789'),),
        deleted=('www.examplle.com',),
        unsubscribe_link='https://dnstwister.report/...',
    )

    assert template.strip() == textwrap.dedent("""
        <h1>dnstwister report for <a>www.example.com</a></h1>
        <p>
            <a href="https://dnstwister.report/...">Unsubscribe</a>
        </p>
        <h2>New registrations</h2>
        <table>
            <thead>
                <tr>
                    <th>Registered Domain</th>
                    <th>Resolved IP</th>
                    <th>Tools</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><a>www.examp1e.com</a></td>
                    <td>127.0.0.1</td>
                    <td><a href="http://dnstwister.report/analyse/1234">analyse</a></td>
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
                    <th>Tools</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><a>www.exampl3.com</a></td>
                    <td>127.0.0.1</td>
                    <td>127.0.0.2</td>
                    <td><a href="http://dnstwister.report/analyse/6789">analyse</a></td>
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
                    <td><a>www.examplle.com</a></td>
                </tr>
            </tbody>
        </table>

        <p>
            <a href="https://dnstwister.report/...">Unsubscribe</a>
        </p>
    """).strip()
