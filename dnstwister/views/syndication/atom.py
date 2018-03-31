"""Atom syndication."""
import base64
import binascii
import datetime
import flask
import werkzeug.contrib.atom

from dnstwister import app, repository, tools
import dnstwister.dnstwist as dnstwist
import dnstwister.tools.template as template_tools


def _base64_redirect(encoded_domain):
    """Try to parse a domain into base64, return a redirect to the hex version
    if successful, otherwise None.
    """
    try:
        decoded_domain = base64.b64decode(encoded_domain)
        if dnstwist.validate_domain(decoded_domain):
            return '/atom/{}'.format(tools.encode_domain(decoded_domain))
    except:
        pass


@app.route('/atom/<hexdomain>')
def view(hexdomain):
    """Return new atom items for changes in resolved domains."""
    # Parse out the requested domain
    domain = tools.parse_domain(hexdomain)

    # Redirect old base64 requests to the new format.
    if domain is None:
        redirect_url = _base64_redirect(hexdomain)
        if redirect_url is not None:
            return flask.redirect(redirect_url, code=302)
        flask.abort(
            400,
            'Malformed domain or domain not represented in hexadecimal format.'
        )

    # Prepare a feed
    feed = werkzeug.contrib.atom.AtomFeed(
        title=u'dnstwister report for {}'.format(
            template_tools.domain_renderer(domain)
        ),
        feed_url='{}atom/{}'.format(flask.request.url_root, hexdomain),
        url='{}search/{}'.format(flask.request.url_root, hexdomain),
    )

    # The publish/update date for the placeholder is locked to 00:00:00.000
    # (midnight UTC) on the current day.
    today = datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # Ensure the domain is registered.
    if not repository.is_domain_registered(domain):
        repository.register_domain(domain)

    # Retrieve the delta report
    delta_report = repository.get_delta_report(domain)

    # If we don't have a delta report yet, show the placeholder.
    if delta_report is None:
        feed.add(
            title=u'No report yet for {}'.format(template_tools.domain_renderer(domain)),
            title_type='text',
            content=flask.render_template(
                'syndication/atom/placeholder.html', domain=domain
            ),
            content_type='html',
            author='dnstwister',
            updated=today,
            published=today,
            id=u'waiting:{}'.format(template_tools.domain_renderer(domain)),
            url=feed.url,
        )

    else:

        # If there is a delta report, generate the feed and return it. We use
        # the actual date of generation here.
        updated = repository.delta_report_updated(domain)
        if updated is None:
            updated = today

        # Setting the ID to be epoch seconds, floored per 24 hours, ensure the
        # updates are only every 24 hours max.
        id_24hr = (updated - datetime.datetime(1970, 1, 1)).total_seconds()

        common_kwargs = {
            'title_type': 'text',
            'content_type': 'html',
            'author': 'dnstwister',
            'updated': updated,
            'published': updated,
            'url': feed.url,
        }

        for (dom, ip) in delta_report['new']:
            feed.add(
                title=u'NEW: {}'.format(template_tools.domain_renderer(dom)),
                content=flask.render_template(
                    'syndication/atom/new.html',
                    ip=ip, hexdomain=tools.encode_domain(dom)
                ),
                id='new:{}:{}:{}'.format(dom.encode('idna'), ip, id_24hr),
                **common_kwargs
            )

        for (dom, old_ip, new_ip) in delta_report['updated']:
            feed.add(
                title=u'UPDATED: {}'.format(template_tools.domain_renderer(dom)),
                content=flask.render_template(
                    'syndication/atom/updated.html',
                    new_ip=new_ip, old_ip=old_ip,
                    hexdomain=tools.encode_domain(dom),
                ),
                id='updated:{}:{}:{}:{}'.format(
                    dom.encode('idna'),
                    old_ip,
                    new_ip,
                    id_24hr
                ),
                **common_kwargs
            )

        for dom in delta_report['deleted']:
            feed.add(
                title=u'DELETED: {}'.format(template_tools.domain_renderer(dom)),
                content=flask.render_template(
                    'syndication/atom/deleted.html',
                ),
                id='deleted:{}:{}'.format(dom.encode('idna'), id_24hr),
                **common_kwargs
            )

    feed_response = feed.get_response()

    repository.mark_delta_report_as_read(domain)

    return feed_response
