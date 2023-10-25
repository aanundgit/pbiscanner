from pbixray import PBIXRay
from icecream import ic

# PBIX_FILE_PATH = r"C:\git\hub\pbixray\test-data\Excalidraw.pbix"
PBIX_FILE_PATH = r"C:\git\hub\pbixray\test-data\Sales & Returns Sample v201912.pbix"
model = PBIXRay(PBIX_FILE_PATH)
ic(model.tables)
ic(model.metadata)
ic(model.power_query)
ic(model.statistics)
ic(model.dax_tables)
ic(model.dax_measures)
ic(model.size)
ic(model.schema)
ic(model.get_table("Age"))
model = PBIXRay(r"C:\git\hub\pbixray\test-data\Excalidraw.pbix")
ic(model.tables)
ic(model.metadata)
ic(model.power_query)
ic(model.statistics)
ic(model.dax_tables)
ic(model.dax_measures)
ic(model.size)
ic(model.schema)
ic(model.get_table("Fruit_RLE"))