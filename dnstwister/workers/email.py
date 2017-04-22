"""Sends emails to subscribers."""
import datetime
import time
import traceback

from dnstwister import emailer, repository
from dnstwister.domain.email_report import EmailReport
from dnstwister.tools import delta_reports
import dnstwister.repository.statistics as statistics_repository
import dnstwister.tools.email as email_tools

# Time in seconds between sending emails for a subscription.
PERIOD = 86400


def get_noisy_domains(candidate_domains):
    """Filter list of domains to those that are noisy."""
    results = set()
    for domain in candidate_domains:
        noise_stat = statistics_repository.get_noise_stat(domain)
        if noise_stat is not None and noise_stat.is_noisy is True:
            results.add(domain)
    return results


def send_noisy_domains():
    """Only send noisy domains on Mondays UTC."""
    return datetime.datetime.today().weekday() == 0


def send_email(domain, email_address, sub_id, report):
    """Format and send an email."""
    body = email_tools.render_email(
        'report.html',
        domain=domain,
        report=report,
        unsubscribe_link='https://dnstwister.report/email/unsubscribe/{}'.format(sub_id)
    )

    emailer.send(
        email_address, 'dnstwister report for {}'.format(domain), body
    )

    print 'Emailed delta for {} to {}'.format(domain, email_address)


def process_sub(sub_id, detail):
    """Process a subscription."""

    domain = detail['domain']
    email_address = detail['email_address']

    # Ensure the domain is registered for reporting, register if not.
    repository.register_domain(domain)

    # Mark delta report as "read" so it's not unsubscribed.
    repository.mark_delta_report_as_read(domain)

    # Don't send more than once every 24 hours
    last_sent = repository.email_last_send_for_sub(sub_id)
    if last_sent is not None:
        age_last_sent = datetime.datetime.now() - last_sent
        if age_last_sent < datetime.timedelta(seconds=PERIOD):
            print 'Skipping {} + {}, < 24h hours'.format(
                email_address, domain
            )
            return

    delta = repository.get_delta_report(domain)
    if delta is None:
        print 'Skipping {} + {}, no delta report yet'.format(
            email_address, domain
        )
        return

    delta_updated = repository.delta_report_updated(domain)

    # If the delta report was updated > 23 hours ago, we're too close to the
    # next delta report. This means we should hold off so we don't send the
    # same delta report twice.
    if delta_updated is not None:
        age_delta_updated = datetime.datetime.now() - delta_updated
        if age_delta_updated > datetime.timedelta(hours=23):
            print 'Skipping {} + {}, delta > 23h hours old'.format(
                email_address, domain
            )
            return

    delta_domains = delta_reports.extract_domains(delta)
    if len(delta_domains) == 0:
        print 'Skipping {} + {}, no changes'.format(
            email_address, domain
        )
        return

    noisy_domains = get_noisy_domains(delta_domains)
    if not send_noisy_domains():
        # If all the domains are noisy, and we're not sending noisy domains
        # today, don't send an email.
        if len(delta_domains) == len(noisy_domains):
            print 'Skipping {} + {}, only noisy domains and not a Monday'.format(
                email_address, domain
            )
            return

        noisy_domains = set()

    report = EmailReport(
        delta['new'],
        delta['updated'],
        delta['deleted'],
        noisy_domains
    )

    try:
        send_email(domain, email_address, sub_id, report)

    except:
        print 'Failed to send email for {}:\n {}'.format(
            domain, traceback.format_exc()
        )

    finally:
        # Mark as emailed to ensure we don't flood if there's an error after
        # the actual email has been sent.
        repository.update_last_email_sub_sent_date(sub_id)


def main():
    """Main code for worker."""
    while True:

        start = time.time()

        subs_iter = repository.isubscriptions()

        while True:

            try:
                sub = subs_iter.next()
            except StopIteration:
                print 'All subs processed in {} seconds'.format(
                    round(time.time() - start, 2)
                )
                break

            if sub is None:
                break

            sub_id, sub_detail = sub

            try:
                process_sub(sub_id, sub_detail)
            except:
                print 'Skipping {}, exception:\n {}'.format(
                    sub_id, traceback.format_exc()
                )

            time.sleep(1)

        time.sleep(60)


if __name__ == '__main__':
    main()
