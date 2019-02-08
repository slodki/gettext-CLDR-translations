#!/usr/bin/env python3
# vi:tabstop=4:expandtab:shiftwidth=4:softtabstop=4:autoindent:smarttab:fileencoding=utf-8
from babel import Locale, localedata, UnknownLocaleError, get_locale_identifier
from babel.messages import Catalog, pofile, mofile
from os import makedirs
import logging
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
parser.add_argument('-p', '--po', default=True, action='store_true', help='generate source .po files')
parser.add_argument('-m', '--mo', action='store_true', help='generate compiled .mo files')
parser.add_argument('locale', nargs='*', help='generate for selected locales only',
    default=localedata.locale_identifiers())
args = parser.parse_args()
if not args.po and not args.mo:
    parser.error ('Either -p or -m is required.')

domain = 'currencies'
header = '''\
# Translations template for %s
# Copyright (C) YEAR ORGANIZATION
# This file is distributed under the MIT license
#
''' % domain
C = Locale.parse('en_US_POSIX')

for loc in sorted(args.locale):
    try:
        locale = Locale.parse(loc)
    except UnknownLocaleError as e:
        logging.error(e.args[0])
        continue
    else:
        logging.info(locale.english_name)

    catalog = Catalog(locale, domain, header, fuzzy=None,
        project='gettext-CLDR-translations', version='1.0',
        copyright_holder='Tomasz Słodkowicz')
    for c in sorted(locale.currencies):
        catalog.add(C.currencies[c], locale.currencies[c], auto_comments=[c])

    subdir = get_locale_identifier((locale.language, locale.territory,
        locale.script, locale.variant))
    if args.po:
        makedirs('po/%s' % subdir, exist_ok=True)
        with open('po/%s/%s.po' % (subdir, domain), 'wb') as f:
            pofile.write_po(f, catalog)

    if args.mo:
        makedirs('mo/%s' % subdir, exist_ok=True)
        with open('mo/%s/%s.mo' % (subdir, domain), 'wb') as f:
            mofile.write_mo(f, catalog)
