"""Tests of the tools.email module."""
import textwrap


from dnstwister.domain.email_report import EmailReport
import dnstwister.tools.email as email_tools


def test_email_renderer():
    """Test the email rendering helper."""
    new = (('www.examp1e.com', '127.0.0.1'),)
    updated = (('www.exampl3.com', '127.0.0.1', '127.0.0.2'),)
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
        <style type="text/css">
            td,th {
                padding-right: 10px;
                text-align: left;
            }
        </style>
        <h1>dnstwister report for 'www<span>.</span>example<span>.</span>com'</h1>
        <p>
            <a href="https://dnstwister.report/...">Unsubscribe</a>
        </p>
        <h2>New registrations (1)</h2>
        <table>
            <thead>
                <tr>
                    <th>Domain</th>
                    <th>IP address</th>
                    <th>Tools</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        www<span>.</span>examp1e<span>.</span>com
                    </td>
                    <td>127.0.0.1</td>
                    <td><a href="https://dnstwister.report/analyse/7777772e6578616d7031652e636f6d">analyse</a></td>
                </tr>
            </tbody>
        </table>
        <h2>Updated registrations (1)</h2>
        <table>
            <thead>
                <tr>
                    <th>Domain</th>
                    <th>Old IP address</th>
                    <th>New IP address</th>
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
                    <td><a href="https://dnstwister.report/analyse/7777772e6578616d706c332e636f6d">analyse</a></td>
                </tr>
            </tbody>
        </table>
        <h2>Noisy domains (1)</h2>
        <p>
            The following domains continually change IP or fail then succeed IP
            resolution.
        </p>
        <table>
            <thead>
                <tr>
                    <th>Domain</th>
                    <th>Tools</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        www<span>.</span>examplle<span>.</span>com
                    </td>
                    <td><a href="https://dnstwister.report/analyse/7777772e6578616d706c6c652e636f6d">analyse</a></td>
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
        ('www.examp2e.com', ''),
        ('www.examp1e.com', ''),
        ('www.examp2f.com', ''),
        ('www.axample.com', 'z'),
        ('www.axample.com', 'a'),
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

    print template

    assert template.strip() == textwrap.dedent("""
        <style type="text/css">
            td,th {
                padding-right: 10px;
                text-align: left;
            }
        </style>
        <h1>dnstwister report for 'www<span>.</span>example<span>.</span>com'</h1>
        <p>
            <a href="https://dnstwister.report/...">Unsubscribe</a>
        </p>
        <h2>New registrations (5)</h2>
        <table>
            <thead>
                <tr>
                    <th>Domain</th>
                    <th>IP address</th>
                    <th>Tools</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        www<span>.</span>axample<span>.</span>com
                    </td>
                    <td>a</td>
                    <td><a href="https://dnstwister.report/analyse/7777772e6178616d706c652e636f6d">analyse</a></td>
                </tr>
                <tr>
                    <td>
                        www<span>.</span>axample<span>.</span>com
                    </td>
                    <td>z</td>
                    <td><a href="https://dnstwister.report/analyse/7777772e6178616d706c652e636f6d">analyse</a></td>
                </tr>
                <tr>
                    <td>
                        www<span>.</span>examp1e<span>.</span>com
                    </td>
                    <td></td>
                    <td><a href="https://dnstwister.report/analyse/7777772e6578616d7031652e636f6d">analyse</a></td>
                </tr>
                <tr>
                    <td>
                        www<span>.</span>examp2e<span>.</span>com
                    </td>
                    <td></td>
                    <td><a href="https://dnstwister.report/analyse/7777772e6578616d7032652e636f6d">analyse</a></td>
                </tr>
                <tr>
                    <td>
                        www<span>.</span>examp2f<span>.</span>com
                    </td>
                    <td></td>
                    <td><a href="https://dnstwister.report/analyse/7777772e6578616d7032662e636f6d">analyse</a></td>
                </tr>
            </tbody>
        </table>
        <p>
            <a href="https://dnstwister.report/...">Unsubscribe</a>
        </p>
    """).strip()
