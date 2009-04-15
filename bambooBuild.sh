#! /bin/sh

#  Bamboo filddles somewhat with the list of execiutables on the standard path so sometimes have to force
#  things by using absolute paths.  In particular wget, curl and unzip are available but not on the stnadrd
#  path.
 
groovyVersion=1.6.0
groovyZipName=groovy-binary-$groovyVersion.zip
groovyInstallPath=groovy-$groovyVersion

/usr/bin/wget http://dist.codehaus.org/groovy/distributions/$groovyZipName
/usr/bin/unzip $groovyZipName

export GROOVY_HOME=$groovyInstallPath

#  Remove any inherited values in JAVA_OPTS since they shouldn't be there.

__JLAUNCHER_DEBUG=true JAVA_OPTS=  scons test

echo "Which libjvms are there?"
find $JAVA_HOME -name "*libjvm*"
