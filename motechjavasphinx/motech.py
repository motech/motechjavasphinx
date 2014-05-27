# Copyright (c) 2014 Grameen Foundation

from collections import namedtuple
from javasphinx import apidoc
import javalang
import os
import shutil
import xml.etree.ElementTree as xml

def expand_package_wildcard(dirpath, package):
    """ If an export package ends in a wildcard we need to look at the filesystem to
    expand the wildcard
    """

    package_elements = package.split(".")[:-1]

    path_prefix = dirpath + '/' + '/'.join(['src','main', 'java']) 
    path = path_prefix + "/" + '/'.join(package_elements)

    return [x[len(path_prefix) + 1:].replace("/", ".") for x in  [x[0] for x in os.walk(path)]]

def extract_export_packages(input_path):
    """ Search through all the poms building a list of the packages that are exported
    """
    ns = "http://maven.apache.org/POM/4.0.0"
    export_packages = []

    input_path = os.path.normpath(os.path.abspath(input_path))

    for dirpath, dirnames, filenames in os.walk(input_path):
        if "archetypes" in dirpath or "src/test/java" in dirpath:
            continue

        for filename in filenames:
            if filename == "pom.xml":
                plugins = []

                pom = xml.parse(os.path.join(dirpath, filename))

                buildNode = pom.getroot().find("{%s}build" % ns)

                if buildNode is not None:
                    pluginsNode = buildNode.find("{%s}plugins" % ns)          

                if pluginsNode is not None:
                    plugins = pluginsNode.findall("{%s}plugin" % ns)

                for plugin in plugins:
                    if plugin.find("{%s}artifactId" % ns).text == 'maven-bundle-plugin':
                        export_node = plugin.find("{%s}configuration" % ns).find("{%s}instructions" % ns).find("{%s}Export-Package" % ns)
                        if export_node is not None:
                            export_str = export_node.text

                            for str in export_str.split(","):
                                package = str.strip().split(";")[0]

                                if str.startswith("!"):
                                    continue

                                # If the include is a wildcard find all the actual packages
                                if package.endswith(".*"):
                                    packages = expand_package_wildcard(dirpath, package)

                                    for package in packages:
                                        export_packages.append(package)

                                else:
                                    export_packages.append(package)

    return export_packages

def find_source_files(input_path, export_packages):
    """ Get a recursive list of filenames for all Java source files within the given
    directory.  Only include files in packages that are exported
    """

    java_files = []

    input_path = os.path.normpath(os.path.abspath(input_path))

    for dirpath, dirnames, filenames in os.walk(input_path):
        for filename in filenames:
            if filename.endswith(".java"):
                if "archetypes" in dirpath or "src/test/java" in dirpath or "/test/" in dirpath or "/testing/" in dirpath or "-test-" in dirpath:
                    continue

                full_filename = os.path.join(dirpath, filename)

                package = get_package(full_filename)

                if package in export_packages:
                    java_files.append(full_filename)


    return java_files

def get_package(source_file):
    """ Get the java package that a source file belongs to
    """
    package = None

    f = open(source_file)
    source = f.read()
    f.close()

    try:
        ast = javalang.parse.parse(source)
        package = ast.package.name
    except javalang.parser.JavaSyntaxError, e:
        print('Syntax error in %s: %s' % source_file, format_syntax_error(e))
    except Exception:
        print('Unexpected exception while parsing %s' % source_file)

    return package

def find_input_path():
    """ Walks backwards (two levels) until it locates the root pom.xml.  This allows the 
    module to run from multiple folder depths within the docs tree
    """
    if os.path.exists("../pom.xml"):
        return "../"

    if os.path.exists("../../pom.xml"):
        return "../../"

def get_dest_dir():
    """ When run via the makefile we run one directory below conf.py so our destdir will
    be 'source/' however when run from read the docs we are executed in the source dir so
    our dest dir is './'
    """

    if os.path.exists("conf.py"):
        return "./"

    if os.path.exists("source/conf.py"):
        return "source/"

def execute_javasphinx(app):
    """ Clean the existing sphinx source files, collect the java source files that
    should be documented and run javasphinx on them.
    """
    Options = namedtuple('Options', ['suffix', 'destdir', 'force', 'update'])
    opts = Options(suffix = "rst", destdir = get_dest_dir(),
                   force = False, update = False)

    input_path = find_input_path()

    filename = "%spackages.%s" % (opts.destdir, opts.suffix)
    if os.path.exists(filename):
        os.remove(filename)

    filename = "%sorg" % opts.destdir
    if os.path.exists(filename):
        shutil.rmtree(filename)

    export_packages = extract_export_packages(input_path)

    # Functions from javasphinx
    source_files = []

    source_files.extend(find_source_files(input_path, export_packages))

    packages, documents, sources = apidoc.generate_documents(source_files, None, 
                                                             False,
                                                             True)

    apidoc.write_documents(documents, sources, opts)
    apidoc.write_toc(packages, opts)

