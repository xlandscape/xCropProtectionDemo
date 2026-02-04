"""
Script for documenting the Landscape Model schematic-100x100 scenario.
"""
import os
import base.documentation

root_folder = os.path.abspath(os.path.join(os.path.dirname(base.__file__), ".."))
base.documentation.document_scenario(
    os.path.join(root_folder, "..", "..", "scenario", "schematic-100x100", "scenario.xproject"),
    os.path.join(root_folder, "..", "..", "scenario", "schematic-100x100", "README.md")
)
base.documentation.write_scenario_changelog(
    os.path.join(root_folder, "..", "..", "scenario", "schematic-100x100", "scenario.xproject"),
    os.path.join(root_folder, "..", "..", "scenario", "schematic-100x100", "CHANGELOG.md")
)
base.documentation.write_contribution_notes(
    os.path.join(root_folder, "..", "..", "scenario", "schematic-100x100", "CONTRIBUTING.md"))
