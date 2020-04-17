from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotFound

import shapefile
from shapely.geometry import Point # Point class
from shapely.geometry import shape # shape() is a function to convert geo objects through the interface

@csrf_exempt
def gmtoffset(request):
    try:
        latitude  = request.GET["lat"]
        longitude = request.GET["lon"]
        point = (float(longitude), float(latitude))
        shp = shapefile.Reader('ne_10m_time_zones/ne_10m_time_zones.shp') #open the shapefile
        all_shapes = shp.shapes() # get all the polygons
        for i, boundary in enumerate(all_shapes):
            if Point(point).within(shape(boundary)): # make a point and see if it's in the polygon
               return HttpResponse(shp.record(i)[7])
    except Exception as e:
        print(e)
        return HttpResponseNotFound('<h1>Page not found</h1>')
