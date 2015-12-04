""" Build out a set of 'dnsresolve' apps.
"""
import os
import yaml
import shutil
import sys


def usage():
    """ Print usage.
    """
    print 'Usage: python build.py [count]\n'


def build(number):
    """ Build a number of applications.
    """
    for i in range(number):
        appid = 'dnsresolve{}'.format(i)

        # Copy in the files
        shutil.copytree('../dnsresolve/', appid)

        # Update the YAML
        with open(os.path.join(appid, 'app.yaml'), 'rb') as yamlf:
            conf = yaml.load(yamlf.read())

        conf['application'] = appid

        with open(os.path.join(appid, 'app.yaml'), 'wb') as yamlf:
            yamlf.write(yaml.dump(conf, default_flow_style=False))


if __name__ == '__main__':

    # Check (as best as can) that we're in the right directory
    files = os.listdir('.')
    if len(files) != 1 or files[0] != __file__:
        raise Exception(
            'build.py must be ran from within a directory only ' + \
            'containing build.py - delete any previously built resolvers.'
        )

    count = 0

    # No count passed in
    if len(sys.argv) == 1:

        # Grab the count
        sys.path.append('../dnstwister/')
        try:
            import resolvers
        except ImportError:
            usage()
            raise Exception('Failed to find dnstwister/resolvers.py')

        count = resolvers.COUNT

    # Count passed in
    elif len(sys.argv) == 2:

        try:
            count = int(sys.argv[-1])
        except ValueError:
            usage()
            raise Exception('Could not parse [count] as integer')

    else:
        usage()
        raise Exception('Wrong number of arguments')

    build(count)

    # Update the stored count
    with open('../dnstwister/resolvers.py', 'wb') as modf:
        modf.write('COUNT = {}'.format(count))
