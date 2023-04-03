from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework.serializers import ModelSerializer

from georiviere.river.models import Stream


class StreamGeojsonSerializer(GeoFeatureModelSerializer):
    # Annotated geom field with API_SRID
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta:
        geo_field = 'api_geom'
        model = Stream
        fields = (
            'id', 'name', 'api_geom'
        )


class StreamSerializer(ModelSerializer):

    class Meta:
        model = Stream
        fields = (
            'id', 'name', 'data_source', 'source_location', 'classification_water_policy', 'flow'
        )
