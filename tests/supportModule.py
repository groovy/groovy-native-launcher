# -*- mode:python; coding:utf-8; -*-
# jedit: :mode=python:

#  Groovy -- A native launcher for Groovy
#
#  Copyright © 2008-9 Russel Winder
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in
#  compliance with the License. You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is
#  distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
#  implied. See the License for the specific language governing permissions and limitations under the
#  License.

import os
import re
import tempfile
import unittest

#  Temporary file names generated by Python can contain characters that are not permitted as Java class
#  names.  This function generates temporary files that are compatible.

def javaNameCompatibleTemporaryFile ( ) :
    while True :
        file = tempfile.NamedTemporaryFile ( )
        if re.compile ( '[-]' ).search ( file.name ) == None : break
        file.close ( )
    return file

#  Execute a command returning a tuple of the return value and the output.  On Posix-compliant systems the
#  return value is an amalgam of signal and return code.  Fortunately we know that the signal is in the low
#  byte and the return value in the next byte.

def executeCommand ( command , prefixCommand = '' ) :
    commandLine = ( prefixCommand + ' ' if prefixCommand else '' ) +  executablePath + ' ' + command
#    print "executing: " + commandLine
    process = os.popen ( commandLine )
    output = process.read ( ).strip ( )
    returnCode = process.close ( )
    if returnCode != None :
        #  Posix-compliant platforms fiddle with the sub-process return code.
        if platform in [ 'posix' , 'darwin' , 'sunos' , 'cygwin' ] :
            returnCode >>= 8
    return ( returnCode , output )

#  The standard SCons entry.

def runTests ( path , architecture , testClass ) :
    global executablePath
    executablePath = path
    global platform
    platform = architecture
    if os.environ['xmlOutputRequired'] == 'True' :
        resultsDirectory = os.environ['xmlTestOutputDirectory']
        if not os.path.exists ( resultsDirectory ) : os.mkdir ( resultsDirectory )
        outputFile = file ( os.path.join ( resultsDirectory , 'TEST-' + testClass.__name__ + '.xml' ) , 'w' )
        #  Shouldn't have to do this next bit, it should be done for us but isn't :-(
        outputFile.write('<?xml version="1.0" encoding="utf-8"?>\n')
        try :
            import xmltestrunner , glob
            testrunner = xmltestrunner.XMLTestRunner ( outputFile )
            returnCode = testrunner.run ( unittest.defaultTestLoader.loadTestsFromTestCase ( testClass ) ).wasSuccessful ( )
        finally :
            outputFile.close ( )
    else :
        returnCode = unittest.TextTestRunner ( ).run ( unittest.defaultTestLoader.loadTestsFromTestCase ( testClass ) ).wasSuccessful ( )
    return returnCode
  
if __name__ == '__main__' :
    print 'Run tests using command "scons test".'
