# -*- mode:python coding:utf-8 -*-

#  Groovy -- A native launcher for Groovy
#
#  Copyright © 2008 Russel Winder
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

#  This tests realized in this Python script originated from the ones in the launcher_test.rb script by
#  Antti Karanta.

#  The directory in which the current executable is stored is calculated by SCons and includes the compiler
#  in use.  This means this test script is not entirely standalone but must be initiated by SCons.

import os
import re
import unittest

import supportModule

#  Class containing all the core tests.

class GroovyTestCase ( unittest.TestCase ) :

    def groovyExecutionTest ( self , command , expectedReturnCode , expectedOutput , extraMessage = None ) :
        '''Execute a Groovy command and then test that the return code is right and the output is right.'''
        ( returnCode , output ) = supportModule.executeCommand ( command )
        self.assertEqual ( returnCode , expectedReturnCode )
        if type ( expectedOutput ) == type ( re.compile ( 'a' ) ) :
            assert expectedOutput.search ( output ) != None , 'Failed to match ' + extraMessage
        else :
            self.assertEqual ( output, expectedOutput )

    def testVersion ( self ) :
        pattern = 'Groovy Version: .* JVM: '
        self.groovyExecutionTest ( '-v' , None , re.compile ( pattern ) , pattern )

    def testPassingJVMParameter ( self ) :
        self.groovyExecutionTest ( '-Xmx300m -e "println Runtime.runtime.maxMemory ( )"' , None , '312213504' if not supportModule.platform == 'sunos' else '311099392' )

    def testServerVM ( self ) :
        self.groovyExecutionTest ( '-server -e "println System.getProperty ( \'java.vm.name\' )"' , None , 'Java HotSpot(TM) Server VM' )

    def testClientVM ( self ) :
        self.groovyExecutionTest ( '-e "println System.getProperty ( \'java.vm.name\' )"' , None , 'Java HotSpot(TM) Client VM' )

    def testExitStatus ( self ) :
        self.groovyExecutionTest ( '-e "System.exit ( 123 )"' , 123 , '' )

    def testLaunchingScript ( self ) :
        #  There is a weird problem with using filenames on MSYS, assume the same is true for Windwoes.
        tmpFile = file ( 'flobadob' , 'w+' ) if supportModule.platform == 'win32' else supportModule.javaNameCompatibleTemporaryFile ( )
        self.launchScriptTest ( tmpFile.name , tmpFile )
        if supportModule.platform == 'win32' : os.remove ( tmpFile.name )

    def launchScriptTest ( self , filename , theFile , extraMessage = None ) :
        theFile.write ( 'println \'hello \' + args[ 0 ]\n' )
        theFile.flush( )
        self.groovyExecutionTest ( filename + ' world' , None , 'hello world' )
        theFile.close ( )

#  Class for all the Cygwin tests.

class CygwinGroovyTestCase ( GroovyTestCase ) :
    
    def testPathUnconverted ( self ) :
        tmpFile = supportModule.javaNameCompatibleTemporaryFile ( )
        self.launchScriptTest ( tmpFile.name , tmpFile )

    def testPathConvertedBackslash ( self ) :
        tmpFile = supportModule.javaNameCompatibleTemporaryFile ( )
        filename = os.popen ( 'cygpath -w ' + tmpFile.name ).read ( ).strip ( ).replace ( '\\' , '\\\\' )
        self.launchScriptTest ( filename , tmpFile )

    def testPathConvertedForwardSlash ( self ) :
        tmpFile = supportModule.javaNameCompatibleTemporaryFile ( )
        filename = os.popen ( 'cygpath -w ' + tmpFile.name ).read ( ).strip ( ).replace ( '\\' , '/' )
        self.launchScriptTest ( filename , tmpFile )

    def testClasspathConversion ( self ) :
        aDirectory = '/tmp'
        bDirectory = aDirectory + '/foo'
        if os.path.exists ( bDirectory ) and not os.path.isdir ( bDirectory ) : os.remove ( bDirectory )
        if not os.path.isdir ( bDirectory ) : os.mkdir ( bDirectory )
        aFile = file ( aDirectory + '/A.groovy' , 'w' )
        aFile.write ( 'class A { def getB ( ) { return new B ( ) } }' )
        aFile.flush ( )
        bFile = file ( bDirectory + '/B.groovy' , 'w' )
        bFile.write ( 'class B { def sayHello ( ) { println( "hello there" ) } }' )
        bFile.flush ( )
        self.groovyExecutionTest ( '--classpath ' + aDirectory + ':' + bDirectory + ' -e "new A ( ).b.sayHello ( )"' , None , 'hello there' )
        os.remove ( aFile.name )
        os.remove ( bFile.name )
        os.rmdir (bDirectory )

#  The entry point for SCons to use.

def runTests ( path , architecture ) :
    supportModule.executablePath = path
    supportModule.platform = architecture
    suite = unittest.makeSuite ( CygwinGroovyTestCase , 'test' ) if supportModule.platform == 'cygwin' else unittest.makeSuite ( GroovyTestCase , 'test' )
    return unittest.TextTestRunner ( ).run ( suite ).wasSuccessful ( )

if __name__ == '__main__' :
    print 'Run tests using command "scons test".'