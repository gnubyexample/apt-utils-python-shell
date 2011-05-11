#!/usr/bin/python
"""
Given the output of a historial dpkg --get-selections this program, lists
dpkg --purge suggestions which will get you some way to returning your
system back to the package state on that historical date.

Using this script and reading output as suggestions for actions to revert system
--------------------------------------------------------------------------------
Note: Installing a different system logger such as dsyslog would automatically
remove rsyslog. To completely reverse that step. You would install rsyslog,
which would automatically remove dsyslog.

This python script (through dpkg --purge) will suggest dpkg --purge dsyslog,
however the other half of the story (install rsyslog is not figured out for you)

Running all of the outputted dpkg --purge commands might work okay in simple
cases, but there is no substitute for using aptitude based no the hints output.


In order to have a program that is less dependent on particular version of
python-apt, this script sometimes avoids making use of python-apt Cache() class
inbuilt iteration functionality.
When python-apt reaches version 1.0, the api might then be stable,
and less subject to change.

The output from this script that is sent to stderr, is probably going
to be more useful than what is sent to stdout.

The output to stdout is just a filtered version of what was passed on stdin.

For the Future: The loop used for testing when (debug > 2) can maybe be improved
in initialisation of count and lineout.

Dependencies:- python-apt package (otherwise import apt is going to fail perhaps)
               http://packages.debian.org/stable/python-apt

A command line example to get you started:
echo -e "dash\t\t\t\t\t\tinstall" | python -W ignore ./get-sel-filter.py 2>/tmp/python.stderr
#echo -e "bash\t\t\t\t\t\tinstall" | python -W ignore ./get-sel-filter.py 2 > ~/python.stderr
#2 > ~/python.stderr with space padding would see get-sel-filter.py treat 2 as an argument!

For the Future: The final loop used for testing (debug > 2) can be altered
to insert bash continuation characters rather than starting a new dpkg statement.

This script is a companion script to get-selections-filter.py
"""

###
# (c) 2009,2010,2011 Gary Wright
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/
#
# http://static.wrightsolutions.co.uk/guide/code/python/
# V1.0 20110503GW Tested against 0.7.100.1 of python-apt and python 2.6.6 on Debian
###

import apt
import sys, fileinput
import logging as l    # avoid reserved mathematical word 'log'


# Log to stderr - leaving the output uncluttered and suitable for input to dpkg.
l.basicConfig(level=l.DEBUG)
debug = 3    # 2 rather than 1 gives you more chat. 3 for testing. 0 for silence.

all_packages = apt.Cache()
installed_packages = [i for i in all_packages if i.is_installed]
installed_packages_list = []
for i in installed_packages:
    installed_packages_list.append(i.name)
upgradable_packages = [i for i in installed_packages if i.is_upgradable]
if debug: l.debug("Total available packages:" + str(len(all_packages)) )
if debug: l.debug("Total installed packages:" + str(len(installed_packages)) )

""" Output using print in a format that is suitable for giving to dpkg. """
def output_selections():
    for i in install_list:
        print "%s\t\t\t\t\t\tinstall" % i


""" Generator function which for every item in list 1 checks that the
item exists also in list 2.
"""
def list_intersection(list1,list2):
    for item1 in list1:
        if item1 in list2: yield item1


# install_list -- Might be shorter than the whole list passed in via stdin
# as it would not include items marked 'deinstall' certainly.
install_list = []
for line in fileinput.input():
    line_split = line.strip().split('\t')     # last word on the line is the action
    pkgname = line_split[0]
    action = line_split[-1]
    if action == 'install':
        install_list.append(pkgname)
    if debug > 3: l.debug(action)
given_list=[ 'lzip' ]
all_packages_list = all_packages.keys()
#all_packages_list = [ 'latex-beamer','lzip' ]
#install_list = given_list

if debug: l.debug("given_list:" + str(len(given_list)) )
if debug: l.debug("install_list:" + str(len(install_list)) )
# li short for list item
install_list = [ li for li in \
                     list_intersection(install_list[:],all_packages.keys()) ]
if debug: l.debug("install_list:" + str(len(install_list)))
if (debug > 3): l.debug("install_list:\n" + "\n".join(install_list))
output_selections()
#print install_list

if (debug > 3):
    for i in upgradable_packages:
        print (i.name, i.candidateVersion, i.architecture, i.installedPriority)

if (debug > 2):
    install_list = list(set(install_list).intersection(all_packages_list))
    l.debug("install_list using casting to and from sets:" + str(len(install_list)))
    install_list_new = [i for i in all_packages if not i.is_installed]
    l.debug("install_list_new:" + str(len(install_list_new)) )
    install_list_new = [ li for li in \
                     list_intersection(install_list[:],install_list_new[:]) ]
    l.debug("install_list_new:" + str(len(install_list_new)) )
    install_list_new_setty = list(set(installed_packages_list) - set(install_list))
    l.debug("install_list_new_setty:" + str(len(install_list_new_setty)) )
    count = 0
    lineout = "dpkg --purge "
    for i in install_list_new_setty:
        if (count == 0): lineout = "dpkg --purge "
        lineout += i.ljust(len(i)+1)
        count += 1
        if (count == 3):   # You might want to change to == 8 or == 30 as you prefer.
            l.debug(lineout)
            count = 0
    if (lineout.strip().split()[-1] != "install"):
	l.debug(lineout)

    if (debug > 3): l.debug("zile" in installed_packages_list)
    if (debug > 3): l.debug("zile" in install_list_new_setty)

    l.debug("\n\nHint ... the purge list that follows can be piped into ... awk -F':purge ' '/^DEBUG:root:purge/ {print $2}'\n")

    l.debug("\n\npurge list (sorted):\n")
    for i in sorted(install_list_new_setty):
	l.debug("purge " + i.ljust(len(i)+1))



