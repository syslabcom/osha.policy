import doctest
import unittest2 as unittest

from osha.policy.tests.base import OSHA_FUNCTIONAL_TESTING
from plone.testing import layered

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    suite  = unittest.TestSuite()
    suite.addTests([
            layered(
                doctest.DocFileSuite(
                    "../doc/lmsretrievers.txt", optionflags=OPTIONFLAGS),
                layer=OSHA_FUNCTIONAL_TESTING),
            ])
    return suite
