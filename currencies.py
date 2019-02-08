#!/usr/bin/env python3
# vi:tabstop=4:expandtab:shiftwidth=4:softtabstop=4:autoindent:smarttab:fileencoding=utf-8
from babel import Locale, UnknownLocaleError, get_locale_identifier, parse_locale
from babel.messages import Catalog, pofile, mofile
from os import makedirs
from itertools import product
from logging import info
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
parser.add_argument('-p', '--po', action='store_true', help='generate source .po files')
parser.add_argument('-m', '--mo', action='store_true', help='generate compiled .mo files')
parser.add_argument('locale', nargs='*', help='generate for selected locales only')
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

for loc in map(lambda s: parse_locale(s), args.locale) if args.locale \
           else product(sorted(C.languages), [None] + sorted(C.territories)):
    try:
        locale = Locale(*loc)
    except UnknownLocaleError as e:
        info('Locale error: %s', e.args)
        continue
    else:
        print(locale.english_name)

    catalog = Catalog(locale, domain, header, fuzzy=None,
        project='gettext-CLDR-translations', version='1.0',
        copyright_holder='Tomasz Słodkowicz')
    for c in sorted(locale.currencies):
        symbol = locale.currency_symbols.get(c, c)
        if symbol == c:
            symbol = C.currency_symbols.get(c, c)
        if symbol == c:
            symbol = ''
        else:
            symbol = 'symbol: %s' % symbol
        catalog.add(C.currencies[c], locale.currencies[c],
            auto_comments=[c], user_comments=[symbol])

    subdir = get_locale_identifier(loc)
    if args.po:
        makedirs('po/%s' % subdir, exist_ok=True)
        with open('po/%s/%s.po' % (subdir, domain), 'wb') as f:
            pofile.write_po(f, catalog)

    if args.mo:
        makedirs('mo/%s' % subdir, exist_ok=True)
        with open('mo/%s/%s.mo' % (subdir, domain), 'wb') as f:
            mofile.write_mo(f, catalog)
