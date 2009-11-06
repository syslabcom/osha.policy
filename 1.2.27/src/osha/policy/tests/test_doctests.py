import os, sys

import glob
import doctest
import unittest
from Globals import package_home
from base import OSHAPolicyFunctionalTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

from osha.policy.config import product_globals

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return unittest.TestSuite((

            Suite('doc/lmsretrievers.txt',
                   optionflags=OPTIONFLAGS,
                   package='osha.policy',
                   test_class=OSHAPolicyFunctionalTestCase) ,



        ))