from app.visualizer import plot_histogram
from lxml import etree

# Test matplotlib functionality
plt = plot_histogram([1, 2, 3, 4, 5], title="Test Plot")
plt.savefig("plot.png")

# Test lxml parsing
xml_content = "<root><item>123</item></root>"
root = etree.fromstring(xml_content)
print("XML Parsed:", root[0].text)
