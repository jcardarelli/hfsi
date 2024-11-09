from unstructured.partition.auto import partition

# Parse PDF
elements = partition("docs/2022californiapl00unse.pdf")

# Get a string representation of the parsed output
print("\n\n".join([str(el) for el in elements]))
