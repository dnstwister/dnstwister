"""Tools to help with delta reports."""
def extract_domains(delta_report):
    """Return the domains in a delta report."""
    return (
        [d[0] for d in delta_report['new']] +
        [d[0] for d in delta_report['updated']] +
        delta_report['deleted']
    )
