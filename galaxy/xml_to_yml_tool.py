# coding: utf-8

import xml.etree.ElementTree as ET

tree = ET.parse('shed_tool_conf.xml')

root = tree.getroot()
tools = {}
section = ""
tool_shed = ""
for elem in root.iter():
  if elem.tag == "section":
     section = "  tool_panel_section_id: '"+elem.attrib['id']+"'"
  if elem.tag == "repository_name":
     print("- name: '" + elem.text + "'")
     print(tool_shed)
     print(section)
  if elem.tag == "tool_shed":
     tool_shed = "  tool_shed_url: https://" + elem.text
  if elem.tag == "repository_owner":
     print("  owner: '" + elem.text + "'")
  if elem.tag == "installed_changeset_revision":
    print("  revisions:\n  - " + elem.text)
