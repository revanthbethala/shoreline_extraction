import ee,geemap

ee.Authenticate()
ee.Initialize(project="ee-revanthbethala")

vizag = ee.Geometry.Polygon(
    [[[83.00, 17.90],
      [83.00, 17.50],
      [83.40, 17.50],
      [83.40, 17.90]]]
)

def add_ndwi(image):
    b2 = image.select('SR_B2').multiply(0.0001)
    b4 = image.select('SR_B4').multiply(0.0001)
    ndwi = b2.subtract(b4).divide(b2.add(b4)).rename('NDWI')
    return image.addBands(ndwi)

start_year = 2010
end_year = 2011

for year in range(start_year, end_year + 1):
    start_date = f'{year}-01-01'
    end_date = f'{year}-12-31'

    collection = (ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
                  .filterBounds(vizag)
                  .filterDate(start_date, end_date)
                  .filter(ee.Filter.lt('CLOUD_COVER', 30))
                  .map(add_ndwi))

    images = collection.toList(collection.size())
    count = collection.size().getInfo()
    print(f'Year {year} - images found: {count}')

    for i in range(count):
        image = ee.Image(images.get(i))
        date_str = image.date().format('YYYYMMdd').getInfo()
        task = ee.batch.Export.image.toDrive(
            image=image,
            description=f'Vizag_NDWI_{year}_{date_str}',
            folder='Vizag_Shoreline_Project',
            fileNamePrefix=f'Vizag_NDWI_{year}_{date_str}',
            region=vizag.getInfo()['coordinates'],
            scale=30,
            maxPixels=1e9
        )
        task.start()
        print(f'Started export task for image {i+1} of year {year}')