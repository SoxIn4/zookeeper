'''Return a list of installed profile names'''

from __future__ import absolute_import, print_function

import subprocess


def fact():
    '''Return the list of installed profiles for this machine'''
    return {'installed_profiles': get_profiles()}

def get_profiles():
        result = []
        attr_str = 'attribute: name:'

        cmd = ['/usr/bin/profiles', 'list', '-verbose']

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _error = process.communicate()

        if process.returncode == 0 and output:
            if isinstance(output, bytes):
                output = output.decode('utf-8').strip()
 
            for line in output.splitlines():
                line = line.strip()
                if attr_str in line:
                    # Partition and get the last result which should be the profile name.
                    try:
                        profile = line.partition(attr_str)[-1].strip()
                        if profile not in result:
                            result.append(profile)
                    except IndexError:
                        pass

        return result

if __name__ == '__main__':
    print(fact())
