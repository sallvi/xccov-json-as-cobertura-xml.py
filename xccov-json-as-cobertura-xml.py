import argparse
import os
import time
import json
import xml.etree.ElementTree as ElementTree

###
### Arguments
###
def get_arguments():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-j", "--json", help="the relative path to the JSON file that contains the xcode coverage report", required=True)
    argument_parser.add_argument("--xcode-project-directory", help="the relative path within the workspace that contains the xcode source files (will be used to try to simplify packages by stripping it from the start of the filename)", required=False)
    return argument_parser.parse_args()

###
### JSON
###

def get_json_data(json_filename):
    with open(json_filename) as json_file:
        return json.load(json_file)
 
###
### XML
###

def get_xml_data(json_data, cwd, xcode_project_directory):
    element_coverage = ElementTree.Element('coverage')
    element_coverage.set('line-rate', str(json_data['lineCoverage']))
    element_coverage.set('branch-rate', '1.0')
    element_coverage.set('lines-covered', str(json_data['coveredLines']))
    element_coverage.set('lines-valid', str(json_data['executableLines']))
    element_coverage.set('branches-covered', '1.0')
    element_coverage.set('branches-valid', '1.0')
    element_coverage.set('complexity', '0.0')
    element_coverage.set('version', '0.1')
    element_coverage.set('timestamp', str(int(time.time())))
    
    element_sources = ElementTree.SubElement(element_coverage, 'sources')
    for source in [cwd, os.path.realpath(__file__)]:
        element_source = ElementTree.SubElement(element_sources, 'source')
        element_source.text = source
    
    element_packages = ElementTree.SubElement(element_coverage, 'packages')
    for target in json_data['targets']:
        current_package_name = None
        current_package_coverage = None
        files = sorted(target['files'], key=lambda x: x['path'])
        for file in files:
            class_filename = file['path'].replace(cwd + "/", "") # Relative path to file
            
            package_name = target['name'] + "." + (os.path.split(class_filename)[0]).replace("/", ".")
            if xcode_project_directory is not None and class_filename.startswith(xcode_project_directory):
                package_name = package_name.replace(xcode_project_directory + ".", "", 1)
            if package_name != current_package_name:
                element_package = ElementTree.SubElement(element_packages, 'package')
                element_package.set('name', package_name)
                element_package.set('branch-rate', '1.0')
                element_package.set('complexity', '0.0')
                element_classes = ElementTree.SubElement(element_package, 'classes')
                
                current_package_name = package_name
                current_package_coverage = (0, 0)
            
            current_package_coverage = (current_package_coverage[0] + 1, current_package_coverage[1] + file['lineCoverage'])
            element_package.set('line-rate', str((current_package_coverage[1] / current_package_coverage[0])))
            
            element_class = ElementTree.SubElement(element_classes, 'class')
            element_class.set('name', os.path.splitext(os.path.basename(file['name']))[0])
            element_class.set('filename', class_filename)
            element_class.set('line-rate', str(file['lineCoverage']))
            element_class.set('branch-rate', '1.0')
            element_class.set('complexity', '0.0')
            
            element_methods = ElementTree.SubElement(element_class, 'methods')
            
            lines = {} # Contains a key for every number with the value being the execution count
            for function in file['functions']:
                for line in range(0, function['executableLines']):
                    number = function['lineNumber'] + line
                    hits = function['executionCount'] if line < function['coveredLines'] else 0
                    lines[number] = min(lines.get(number, hits), hits) # In case of duplicate line numbers, the lower execution count value is being used (this leads to a more realistic overall coverage report in Cobertura when handling completion blocks within functions)

            element_lines = ElementTree.SubElement(element_class, 'lines')
            for number, hits in lines.items():
                element_line = ElementTree.SubElement(element_lines, 'line')
                element_line.set('number', str(number))
                element_line.set('hits', str(hits))
                element_line.set('branch', "false")
    
    return element_coverage

###
### XML: Printing
###

def print_xml(xml_data):
    print("""<!--DOCTYPE coverage SYSTEM "http://cobertura.sourceforge.net/xml/coverage-04.dtd"-->""")
    ElementTree.dump(xml_data)

###
### Main
###
arguments = get_arguments()

json_data = get_json_data(arguments.json)
xml_data = get_xml_data(json_data, os.getcwd(), arguments.xcode_project_directory)
print_xml(xml_data)
