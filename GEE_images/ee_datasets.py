import os
import ee
import ee.mapclient

# ee.Authenticate()
ee.Initialize()


def maskL8sr(image):
    """
    Masks out clouds within the images
    """
    # Bits 3 and 5 are cloud shadow and cloud
    cloudShadowBitMask = (1 << 3)
    cloudsBitMask = (1 << 5)
    # Get pixel QA band
    qa = image.select('BQA')
    # Both flags should be zero, indicating clear conditions
    mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(
        qa.bitwiseAnd(cloudsBitMask).eq(0)
    )

    return image.updateMask(mask)


def maskSentinel(image):
    cloudShadowBitMask = (1 << 10)
    cloudsBitMask = (1 << 11)

    qa = image.select('QA60')

    mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(
        qa.bitwiseAnd(cloudsBitMask).eq(0)
    )

    return image.updateMask(mask)


def getSentinelCollection():
    bnSen = ['B2', 'B3', 'B4', 'B8', 'B11', 'B12', 'QA60']
    bns = ['Blue', 'Green', 'Red', 'NIR', 'Swir1', 'Swir2']

    sen = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").select(bnSen, bns)

    return (sen)


def getLandsatCollection():
    """
    merge landsat 5, 7, 8 collection 1
    tier 1 SR imageCollections and standardize band names
    """
    # standardize band names
    bn8 = ['B2', 'B3', 'B4', 'B5', 'B6',  'B7', 'pixel_qa']
    bn7 = ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa']
    bn5 = ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa']
    bns = ['Blue', 'Green', 'Red', 'NIR', 'Swir1', 'Swir2', 'BQA']

    # create a merged collection from landsat 5, 7, and 8
    ls5 = ee.ImageCollection("LANDSAT/LT05/C01/T1_SR").select(bn5, bns)

    ls7 = (ee.ImageCollection("LANDSAT/LE07/C01/T1_SR")
           .filterDate('1999-04-15', '2003-05-30')
           .select(bn7, bns))

    ls8 = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR").select(bn8, bns)

    merged = ls5.merge(ls7).merge(ls8)

    return(merged)

def getLandsatTOACollection():
    """
    merge landsat 7, 8 collection 1
    tier 1 TOA imageCollections and standardize band names
    """
    # standardize band names
    bn8 = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'QA_PIXEL']
    bn7 = ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'B8', 'QA_PIXEL']
    bns = ['Blue', 'Green', 'Red', 'NIR', 'Swir1', 'Swir2', 'Panchromatic', 'BQA']

    # create a merged collection from landsat 5, 7, and 8
    ls7 = (
        ee.ImageCollection(
            "LANDSAT/LE07/C02/T1_TOA"
        ).filterDate(
            '1999-06-29', '2013-03-18'
        ).select(bn7, bns)
    )

    ls8 = ee.ImageCollection(
        "LANDSAT/LC08/C02/T1_TOA"
    ).select(bn8, bns)

    merged = ls7.merge(ls8)

    return(merged)


def get_image(year, polygon, dataset='landsatSR'):
    """
    Set up server-side image object
    """
    # Get begining and end
    begin = str(year) + '-01' + '-01'
    end = str(year) + '-12' + '-31'

    band_names = ['Blue', 'Green', 'Red', 'NIR', 'Swir1', 'Swir2']
    TOA_band_names = ['Blue', 'Green', 'Red', 'NIR', 'Swir1', 'Swir2', 'Panchromatic']

    if dataset == 'landsatSR':
        allLandsat = getLandsatCollection()
        image = allLandsat.map(
            maskL8sr
        ).filterDate(
            begin, end
        ).median().clip(
            polygon
        ).select(band_names)
    elif dataset == 'landsatTOA':
        landsatTOA = getLandsatTOACollection()
        image = landsatTOA.map(
            maskL8sr
        ).filterDate(
            begin, end
        ).median().clip(
            polygon
        ).select(TOA_band_names)
    elif dataset == 'sentinel':
        sentinel2 = getSentinelCollection()
        image = sentinel2.map(
            maskSentinel
        ).filterDate(
            begin, end
        ).median().clip(
            polygon
        ).select(band_names)

    return image


def get_image_period(year, start, end, polygon, dataset='landsatSR'):
    begin = str(year) + '-' + start
    end = str(year) + '-' + end

    band_names = ['Blue', 'Green', 'Red', 'NIR', 'Swir1', 'Swir2']
    TOA_band_names = ['Blue', 'Green', 'Red', 'NIR', 'Swir1', 'Swir2', 'Panchromatic']

    images = ee.List([])
    if dataset == 'landsatSR':
        allLandsat = getLandsatCollection()
        images = images.add(allLandsat.map(
            maskL8sr
        ).filterDate(
            begin, end
        ).median().clip(
            polygon
        ).select(band_names))
    elif dataset == 'landsatTOA':
        landsatTOA = getLandsatTOACollection()
        images = images.add(landsatTOA.map(
            maskL8sr
        ).filterDate(
            begin, end
        ).median().clip(
            polygon
        ).select(TOA_band_names))
    elif dataset == 'sentinel':
        sentinel2 = getSentinelCollection()
        images = images.add(sentinel2.map(
            maskSentinel 
        ).filterDate(
            begin, end
        ).median().clip(
            polygon
        ).select(band_names))

    return ee.ImageCollection(
        images
    ).median().clip(
        polygon
    )


def request_params(filename, scale, image):
    filename = os.path.abspath(filename)
    basename = os.path.basename(filename)
    name = os.path.splitext(basename)[0]

    params = {"name": name, "filePerBand": False}
    params["scale"] = scale
    region = image.geometry()
    params["region"] = region

    return params
