"""Atom syndication."""
import werkzeug.contrib.atom


def view(hexdomain):
    """Return new atom items for changes in resolved domains."""
    # Parse out the requested domain
    domain = tools.parse_domain(hexdomain)
    if domain is None:
        flask.abort(500)

    # Prepare a feed
    feed = werkzeug.contrib.atom.AtomFeed(
        title='dnstwister report for {}'.format(domain),
        feed_url='https://dnstwister.report/atom/{}'.format(hexdomain),
        url='https://dnstwister.report/search/{}'.format(hexdomain),
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
            title='No report yet for {}'.format(domain),
            title_type='text',
            content=flask.render_template(
                'atom_placeholder.html', domain=domain
            ),
            content_type='html',
            author='dnstwister',
            updated=today,
            published=today,
            id='waiting:{}'.format(domain),
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
            'content_type': 'text',
            'author': 'dnstwister',
            'updated': updated,
            'published': updated,
            'url': feed.url,
        }

        for (dom, ip) in delta_report['new']:
            feed.add(
                title='NEW: {}'.format(dom),
                content='IP: {}'.format(ip),
                id='new:{}:{}:{}'.format(dom, ip, id_24hr),
                **common_kwargs
            )

        for (dom, old_ip, new_ip) in delta_report['updated']:
            feed.add(
                title='UPDATED: {}'.format(dom),
                content='IP: {} > {}'.format(old_ip, new_ip),
                id='updated:{}:{}:{}:{}'.format(dom, old_ip, new_ip, id_24hr),
                **common_kwargs
            )

        for (dom, ip) in delta_report['deleted']:
            feed.add(
                title='DELETED: {}'.format(dom),
                content='IP: {}'.format(ip),
                id='deleted:{}:{}:{}'.format(dom, ip, id_24hr),
                **common_kwargs
            )

    feed_response = feed.get_response()

    repository.mark_delta_report_as_read(domain)

    return feed_response
