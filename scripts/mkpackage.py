#!/usr/bin/python
# SPDX-FileCopyrightText: © 2022 ELABIT GmbH <mail@elabit.de>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the Robotmk project (https://www.robotmk.org)

# This script reads the current version tag and creates a versioned robotmk MKP

from mkp import dist
from pathlib2 import Path
import os
import sys
from shutil import copyfile, rmtree
import re
from collections import namedtuple
import requests


Target = namedtuple('Target', 'path, filename')
customfiles = {
    'agents/plugins/robotmk': Target('agents/custom/robotmk-external/lib/bin', 'robotmk.py'),
    'agents/plugins/robotmk-runner': Target('agents/custom/robotmk-external/lib/bin', 'robotmk-runner.py'),
    'agents/plugins/robotmk-runner': Target('agents/custom/robotmk-external/lib/bin', 'robotmk-runner.pyw'),
}

rootpath = Path(os.path.dirname(os.path.realpath(__file__)))

def get_tag():
    if '--tag' in sys.argv:
        tag = sys.argv[sys.argv.index('--tag') + 1]
    else:
        ostream = os.popen('git describe --tags')
        tag = ostream.read().strip()
        # match semantic version
        if not re.match('^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$', tag):
            print "ERROR: Last git tag does not match the expected version format! Exiting."
            sys.exit(1)
    return tag


def get_kw_lib(url):
    resp = requests.get(url)
    return resp.content


def embed_keywordlib(module_string, pluginfile, src_url):
    pluginfile = os.path.abspath(pluginfile)
    with open(pluginfile) as file:
        filedata = file.read()
    leftboundary = '#<robotmk-keywordlibrary'
    rightboundary = '#robotmk-keywordlibrary>'
    comment = '# Imported from %s' % src_url
    repl_string = re.sub(r'^(.*){}.*?{}(.*)'.format(leftboundary, rightboundary),
            r"\1%s\n%s\n%s\n%s\2" % (
                leftboundary,
                comment,
                module_string,
                rightboundary),
            filedata,
            flags=re.DOTALL)

    with open(pluginfile, 'w') as file:
        file.write(repl_string)

    file.close()

tag = get_tag()
robotmk_keywordlib_url = "https://raw.githubusercontent.com/simonmeggle/robotframework-robotmk/robotmk-%s/robotmk.py" % tag
robotmk_keywordlib_content = get_kw_lib(robotmk_keywordlib_url)
embed_keywordlib(robotmk_keywordlib_content, 'agents/plugins/robotmk', robotmk_keywordlib_url)



for file in customfiles:
    path = customfiles[file].path
    Path(path).mkdir(parents=True, exist_ok=True)
    copyfile(file, str(Path(path).joinpath(customfiles[file].filename)))

blacklist = [
    'local/lib',
    'test_robotmk_plugin.py',
    'agents/plugins/robotmk.py',
    '__pycache__',
]

pkg_desc = '''
    Robotmk integrates Robot Framework results into Checkmk.
    Robot Framework can test web based and native applications.
    It is easy to learn and highly extendable by libraries.
    Libraries provide the functionality to use modern test web
    technologies (Playwright/Selenium), control user interfaces
    (ImageHorizon, SikuliX, AutoIT, SAP, ...), REST/SOAP APIs
    and many more. It is based on Python and can be extended
    by own libraries as well.
    See https://robotframework.org for more information.
'''


dist({
    'author': 'Simon Meggle, https://www.simon-meggle.de',
    'description': pkg_desc,
    'download_url': 'https://www.robotmk.org',
    'name': 'robotmk',
    'title': 'Robotmk | Robot Framework End2End Test Integration',
    'version': tag.replace('v', ''),
    'version.min_required': '1.6',
}, blacklist=blacklist)

rmtree(str('agents/custom'))
