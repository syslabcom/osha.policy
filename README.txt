Package description
*******************

.. contents::

.. Note!
   -----
   
   - code repository
   - bug tracker
   - questions/comments feedback mail


- Code repository: http://svn.syslab.com/svn/OSHA/osha.policy
- Questions and comments to info (at) syslab (dot) com
- Report bugs at http://products.syslab.com/products/osha.policy/issues


JavaScript Registry
===================

The JS registry: (portal_javascripts) is cleared and re-imported from osha/policy/profiles/default/osha-jsregistry.xml by the resetJSRegistry setuphandler. Please note that all JavaScript should be managed in this file to avoid trouble with re-ordering etc. caused by installed JS via other profiles.


VDEX Tools
==========
This egg provides a number of shell scripts that shall support people in
updating vdex definitions. They are meant for developers and have not a lot
of error handling.

cmd_parser
    Tool to parse some excel file for generating command lists for the vdex
    updater. This is error prone and should be avoided

vdex_updater
    Tool to update a vdex file. You should provide a file with a command list
    and the vdex file. The command list is a little dsl that is described below.
    The output will always be stored in the file ./out.xml

xmltoxsl
    This works only with thesaurus files, and gives some statistical information
    about the vdex file. Its output will always be ./out.csv

ordervdex
    This tool takes a vdex file and orders the element according to id.
    It overrides the old xml file!

insertTranslations
    This tool takes the vdex file and then a list of translations provided
    as xls as in the form given out from xltoxsl.
    It assumes that the language id is in the filename in [27:29].
    It inserte the provided translations.
    The outputfile is always new.vdex.

VDEX UPDATER DSL
================
A line is one command.
A line consists of fields, separated by pipe characters.
The first field is the command.

c = Create
    The next fields contain the new id, the parent id, a caption
    and a description that is currently ignored.
    The new term will be added below the last child if the parent term
    those termIdentifier is lower than the new id. Thus, an ordered
    tree will still be ordered.

u = Update
    The next fields contain the id, the caption and description. The
    description is currently ignored.

m = Move
    The next fields contain the old id, the new id and the new father id.
    The Term gets removed from the old place and added below the father.
    Where it gets added is calculated with the same rules as the Create
    command. All commands have another parameter now, the last one, must
    be keep_names or something else. This is only relevant if you copy
    your term over to an existing term. with keep_names, in any combination
    of upper and lower case letter, we will not do anything. With another
    value, like, overwrite_names, we will override the target term name
    and its translations.

d = Delete
    The next field contains the id of the term to be deleted.


Testing
=======

osha.policy contains tests for the package itself and other dependencies
in the osha namespace (e.g. osha.theme) - these tests might move to their
respective packages in the future.

To run all the tests for osha.policy::

    $ bin/test-osha

To run a specific test from osha.policy::

    $ bin/test-osha -t test_oshaview

Running this command might take quite a lot of time, because there are
some very time consuming tests. If you run the tests frequently it is
advisable to use an alternative test runner, which runs the tests
without all the expensive tests.

To run a test runner for osha.policy without the time consuming tests::

    $ bin/test-osha-quick

Note that if you want to use the '-t' switch, just specify the filter 
immediately after the test runner script, without the '-t' (because
we already use the -t switch in the test runner to exclude the slow
tests)::

    $ bin/test-osha-quick test_oshaview

To run the tests for the other packages which are dependencies of
osha.policy::

    $ bin/test-deps

For other test options please consult the test runner help::

    $ bin/test --help


Credits
=======

Copyright European Agency for Health and Safety at Work and Syslab.com
GmbH.

osha.policy development was funded by the European Agency for Health
and Safety at Work.


License
=======

osha.policy is licensed under the GNU Lesser Generic Public License,
version 2 or later and EUPL version 1.1 only. The complete license
texts can be found in docs/LICENSE.GPL and docs/LICENSE.EUPL.
