## Xcode JSON coverage as Cobertura XML coverage to display (iOS) coverage reports in Jenkins CI

A simple lightweight script to convert a Xcode coverage file as JSON to a Cobertura XML file, to be used in Jenkins CI.

### Example Usage

0. Put _xccov-json-as-cobertura-xml.py_ somewhere where you can execute it from your CI (I've put it in my SCM).
1. After your (probably existing) build workflow, where you have built your project and did run your tests with something like `xcodebuild clean build test`:
  1. Use `xcrun xccov view --report --json {DerivedDataPath}/Logs/Test/*.xcresult > {TestReportPath}/coverage.json` to generate the Xcode coverage file.
  2. Use `python3 {CIScriptsPath}/xccov-json-as-cobertura-xml.py --json {TestReportPath}/coverage.json > {TestReportPath}/coverage.xml` to convert your Xcode coverage file to a Cobertura coverage file.
3. Configure the [Cobertura](https://wiki.jenkins.io/display/JENKINS/Cobertura+Plugin) plugin to point to your generated _coverage.xml_ file.

### Compatibility

- Requires *Python 3.0+*
- Generates an XML which validates against [Cobertura DTD Version 4](http://cobertura.sourceforge.net/xml/coverage-04.dtd)
- Tested with *Xcode 11.3* and *Jenkins Cobertura Plugin 1.15* 

### Notes

...
