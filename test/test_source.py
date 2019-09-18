'''
Author: Víctor Ruiz Gómez

Unitary test for method test_source in the module source.py.
'''


import unittest
from unittest import TestCase
from operator import eq, attrgetter
from itertools import starmap, repeat
from re import findall
from source import parse_source


class TestParseSource(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._single_names = ['foo', 'bar', 'qux', 'baz']
        self._composed_names = ['foo_bar', 'foo bar', 'foo_bar_qux', 'foo_bar qux']
        self._names = self._single_names + self._composed_names

    def test_vars(self):
        # We can pass additional context vars with keyword arguments
        self.assertEqual('bar', parse_source('{{foo}}', foo='bar'))


    def test_globalvars(self):
        # symbol_types and geometric_types are global variables (non empty lists)
        self.assertGreater(len(parse_source('{% for x in symbol_types %}@{% endfor %}')), 0)
        self.assertGreater(len(parse_source('{% for x in geometric_types %}@{% endfor %}')), 0)


    def test_filters(self):
        # filters pytitle, ctitle, getter, setter & plural are avaliable
        for filter in ('pytitle', 'ctitle', 'getter', 'setter', 'plural'):
            self.assertGreater(len(parse_source('{{foo|' + filter + '}}', foo='hello')), 0)

    def test_pytitle(self):
        for x in self._names:
            y = parse_source('{{x|pytitle}}', x=x)
            self.assertTrue(y[0].isupper())
            self.assertEqual(y.count('_') + y.count(' '), 0)
            self.assertEqual(len(findall('[A-Z]', y)), len(findall('[A-Z]', x.title())))

    def test_ctitle(self):
        for x in self._names:
            y = parse_source('{{x|ctitle}}', x=x)
            self.assertTrue(y[0].isupper())
            self.assertEqual(y.count('_'), x.count(' ') + x.count('_'))
            self.assertEqual(len(findall('[_ ][a-zA-Z]', x)), len(findall('_[A-Z]', y)))

    def test_getter(self):
        for x in self._single_names:
            y = parse_source('{{x|getter}}', x=x)
            self.assertEqual('get_'+x, y)

    def test_setter(self):
        for x in self._single_names:
            y = parse_source('{{x|setter}}', x=x)
            self.assertEqual('set_'+x, y)

    def test_plural(self):
        for x in self._names:
            y = parse_source('{{x|plural}}', x=x)
            self.assertEqual(x+'s', y)

        self.assertEqual(parse_source('{{x|plural}}', x='velocity'), 'velocities')
