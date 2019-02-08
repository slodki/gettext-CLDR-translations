#!/usr/bin/env python3
# vi:tabstop=4:expandtab:shiftwidth=4:softtabstop=4:autoindent:smarttab:fileencoding=utf-8
from babel import Locale, localedata, UnknownLocaleError
from babel.messages import Catalog, pofile, mofile
from os import makedirs
import logging
from argparse import ArgumentParser

domain = 'currencies'
parser = ArgumentParser(description='Generate gettext translations for %s using CLDR data.' % domain)
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
parser.add_argument('-p', '--po', default=True, action='store_true', help='generate source .po files')
parser.add_argument('-m', '--mo', action='store_true', help='generate compiled .mo files')
parser.add_argument('-s', '--stats', default=True, action='store_true', help='print statistics')
parser.add_argument('locale', nargs='*', help='generate for selected locales only',
    default=localedata.locale_identifiers())
args = parser.parse_args()
if not args.po and not args.mo:
    parser.error ('Either -p or -m is required.')

header = '''\
# Translations template for %s
# Copyright (C) YEAR ORGANIZATION
# This file is distributed under the MIT license
#
''' % domain
C = Locale.parse('en_US_POSIX')
max_cur = len(C.currencies)
t = 0

for loc in sorted(args.locale):
    try:
        locale = Locale.parse(loc)
    except UnknownLocaleError as e:
        logging.error(e.args[0])
        continue

    catalog = Catalog(locale, domain, header, fuzzy=None,
        project='gettext-CLDR-translations', version='1.0',
        copyright_holder='Tomasz Słodkowicz')
    for c in sorted(locale.currencies):
        catalog.add(C.currencies[c], locale.currencies[c], auto_comments=[c])

    subdir = catalog.locale_identifier
    if args.po:
        makedirs('po/%s' % subdir, exist_ok=True)
        with open('po/%s/%s.po' % (subdir, domain), 'wb') as f:
            pofile.write_po(f, catalog)
    if args.mo:
        makedirs('mo/%s' % subdir, exist_ok=True)
        with open('mo/%s/%s.mo' % (subdir, domain), 'wb') as f:
            mofile.write_mo(f, catalog)

    if args.stats:
        print('%3i%% %s' % (len(catalog._messages)*100/max_cur, locale.english_name))
        t += len(catalog._messages)
    else:
        print(locale.english_name)

if args.stats:
    langs = {}
    langs.update(map(lambda x: (x.partition('_')[0], None), args.locale))
    print('stats: %i languages, %i locales, %i currencies, %i translated strings (%i%%)'
        % (len(langs), len(args.locale), max_cur, t, 100*t/(len(args.locale*max_cur))))
