"""Tests of the tools.email module."""
import textwrap


from dnstwister.domain.email_report import EmailReport
import dnstwister.tools.email as email_tools


def test_email_renderer():
    """Test the email rendering helper."""
    new = (('www.examp1e.com', '127.0.0.1', 'http://dnstwister.report/analyse/1234'),)
    updated = (('www.exampl3.com', '127.0.0.1', '127.0.0.2', 'http://dnstwister.report/analyse/6789'),)
    deleted = ('www.examplle.com',)
    noisy = ('www.examplle.com',)

    report = EmailReport(new, updated, deleted, noisy)

    template = email_tools.render_email(
        'report.html',
        domain='www.example.com',
        report=report,
        unsubscribe_link='https://dnstwister.report/...',
    )

    assert template.strip() == textwrap.dedent("""
        <h1>dnstwister report for 'www<span>.</span>example<span>.</span>com'</h1>
        <p>
            <a href="https://dnstwister.report/...">Unsubscribe</a>
        </p>
        <h2>New registrations (1)</h2>
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
                    <td>
                        www<span>.</span>examp1e<span>.</span>com
                    </td>
                    <td>127.0.0.1</td>
                    <td><a href="http://dnstwister.report/analyse/1234">analyse</a></td>
                </tr>
            </tbody>
        </table>
        <h2>Updated registrations (1)</h2>
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
                    <td>
                        www<span>.</span>exampl3<span>.</span>com
                    </td>
                    <td>127.0.0.1</td>
                    <td>127.0.0.2</td>
                    <td><a href="http://dnstwister.report/analyse/6789">analyse</a></td>
                </tr>
            </tbody>
        </table>
        <hr />
        <h3>Noisy changes</h3>
        <p>
            Domains that change IP or are registered and unregistered regularly are
            considered "noisy" and are listed below. Most subscriptions will have one
            or more "noisy" domains.
        </p>
        <h4>Deleted registrations</h4>
        <table>
            <thead>
                <tr>
                    <th>Previously Registered Domain</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        www<span>.</span>examplle<span>.</span>com
                    </td>
                </tr>
            </tbody>
        </table>
        <p>
            <a href="https://dnstwister.report/...">Unsubscribe</a>
        </p>
    """).strip()


def test_email_renderer_domain_sorting():
    """Test the email rendering helper sorts domains."""
    new = (
        ('www.examp2e.com', '', ''),
        ('www.examp1e.com', '', ''),
        ('www.examp2f.com', '', ''),
        ('www.axample.com', 'z', ''),
        ('www.axample.com', 'a', ''),
    )
    updated = []
    deleted = []
    noisy = []

    report = EmailReport(new, updated, deleted, noisy)

    template = email_tools.render_email(
        'report.html',
        domain='www.example.com',
        report=report,
        unsubscribe_link='https://dnstwister.report/...',
    )

    assert template.strip() == textwrap.dedent("""
        <h1>dnstwister report for 'www<span>.</span>example<span>.</span>com'</h1>
        <p>
            <a href="https://dnstwister.report/...">Unsubscribe</a>
        </p>
        <h2>New registrations (5)</h2>
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
                    <td>
                        www<span>.</span>axample<span>.</span>com
                    </td>
                    <td>a</td>
                    <td><a href="">analyse</a></td>
                </tr>
                <tr>
                    <td>
                        www<span>.</span>axample<span>.</span>com
                    </td>
                    <td>z</td>
                    <td><a href="">analyse</a></td>
                </tr>
                <tr>
                    <td>
                        www<span>.</span>examp1e<span>.</span>com
                    </td>
                    <td></td>
                    <td><a href="">analyse</a></td>
                </tr>
                <tr>
                    <td>
                        www<span>.</span>examp2e<span>.</span>com
                    </td>
                    <td></td>
                    <td><a href="">analyse</a></td>
                </tr>
                <tr>
                    <td>
                        www<span>.</span>examp2f<span>.</span>com
                    </td>
                    <td></td>
                    <td><a href="">analyse</a></td>
                </tr>
            </tbody>
        </table>
        <p>
            <a href="https://dnstwister.report/...">Unsubscribe</a>
        </p>
    """).strip()
