from pbixray import PBIXRay

# PBIX_FILE_PATH = r"C:\git\hub\pbixray\test-data\Excalidraw.pbix"
PBIX_FILE_PATH = r"C:\git\hub\pbixray\test-data\Sales & Returns Sample v201912.pbix"
model = PBIXRay(PBIX_FILE_PATH)
print(model)