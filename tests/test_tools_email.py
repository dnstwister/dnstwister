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
        noisy_link='https://dnstwister.report/email/1/noisy',
    )

    assert template.strip() == textwrap.dedent("""
        <h1>dnstwister report for <strong>www<span>.</span>example<span>.</span>com</strong></h1>
        <p>
            <strong>NEW: dnstwister now supports Unicode domains.</strong>
        </p>
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
                    <td>
                        www<span>.</span>examp1e<span>.</span>com
                    </td>
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
                    <td>
                        www<span>.</span>exampl3<span>.</span>com
                    </td>
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
                    <td>
                        www<span>.</span>examplle<span>.</span>com
                    </td>
                </tr>
            </tbody>
        </table>
        <p>
            These emails <strong>exclude</strong> domains considered to be "noisy" -
            those that are either registered and unregistered constantly, or
            constantly change IP address. <a href="https://dnstwister.report/email/1/noisy">You can view a
            report of these domains at any time.</a>
        </p>
        <p>
            <a href="https://dnstwister.report/...">Unsubscribe</a>
        </p>
    """).strip()


def test_email_renderer_domain_sorting():
    """Test the email rendering helper sorts domains."""
    template = email_tools.render_email(
        'report.html',
        domain='www.example.com',
        new=(
            ('www.examp2e.com', '', ''),
            ('www.examp1e.com', '', ''),
            ('www.examp2f.com', '', ''),
            ('www.axample.com', 'z', ''),
            ('www.axample.com', 'a', ''),
        ),
        updated=[],
        deleted=[],
        unsubscribe_link='https://dnstwister.report/...',
        noisy_link='https://dnstwister.report/email/1/noisy',
    )

    assert template.strip() == textwrap.dedent("""
        <h1>dnstwister report for <strong>www<span>.</span>example<span>.</span>com</strong></h1>
        <p>
            <strong>NEW: dnstwister now supports Unicode domains.</strong>
        </p>
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
            These emails <strong>exclude</strong> domains considered to be "noisy" -
            those that are either registered and unregistered constantly, or
            constantly change IP address. <a href="https://dnstwister.report/email/1/noisy">You can view a
            report of these domains at any time.</a>
        </p>
        <p>
            <a href="https://dnstwister.report/...">Unsubscribe</a>
        </p>
    """).strip()


def test_hiding_noisy_text_renderer():
    """Test the noisy text isn't shown if no noisy link."""
    template = email_tools.render_email(
        'report.html',
        domain='www.example.com',
        new=(('www.examp1e.com', '127.0.0.1', 'http://dnstwister.report/analyse/1234'),),
        updated=(('www.exampl3.com', '127.0.0.1', '127.0.0.2', 'http://dnstwister.report/analyse/6789'),),
        deleted=('www.examplle.com',),
        unsubscribe_link='https://dnstwister.report/...',
        noisy_link=None,
    )

    assert template.strip() == textwrap.dedent("""
        <h1>dnstwister report for <strong>www<span>.</span>example<span>.</span>com</strong></h1>
        <p>
            <strong>NEW: dnstwister now supports Unicode domains.</strong>
        </p>
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
                    <td>
                        www<span>.</span>examp1e<span>.</span>com
                    </td>
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
                    <td>
                        www<span>.</span>exampl3<span>.</span>com
                    </td>
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
