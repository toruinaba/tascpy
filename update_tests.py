import re

with open("tests/unit/operations/load_displacement/test_load_displacement_analysis.py", "r") as f:
    content = f.read()

# Update slopes
content = content.replace('expected_column = "slope_load_displacement"', 'expected_column = "slope_displacement"')
content = content.replace('expected_column = "slope_force_disp"', 'expected_column = "slope_disp"')

# Find yield point updates
content = re.sub(r'result_prefix="[^"]*",?\s*', '', content)
content = re.sub(r'result_prefix=custom_prefix,?\s*', '', content)
content = content.replace('assert "yield_displacement" in result.columns', 'assert "yield_point" in result.results')
content = content.replace('assert "yield_load" in result.columns', '')
content = content.replace('yield_disp = result["yield_displacement"].values[0]', 'yield_disp = result.results["yield_point"].x')
content = content.replace('yield_load = result["yield_load"].values[0]', 'yield_load = result.results["yield_point"].y')

content = content.replace('assert f"{custom_prefix}_displacement" in result.columns', 'assert "yield_point" in result.results')
content = content.replace('assert f"{custom_prefix}_load" in result.columns', '')
content = content.replace('yield_disp = result[f"{custom_prefix}_displacement"].values[0]', 'yield_disp = result.results["yield_point"].x')
content = content.replace('yield_load = result[f"{custom_prefix}_load"].values[0]', 'yield_load = result.results["yield_point"].y')

content = content.replace('assert "analysis" in result.metadata', 'assert "yield_point" in result.results')
content = content.replace('assert "yield_point" in result.metadata["analysis"]', 'assert "method" in result.results["yield_point"].metadata')
content = content.replace('yield_data = result.metadata["analysis"]["yield_point"]', 'yield_data = result.results["yield_point"].metadata')

# Write back
with open("tests/unit/operations/load_displacement/test_load_displacement_analysis.py", "w") as f:
    f.write(content)

