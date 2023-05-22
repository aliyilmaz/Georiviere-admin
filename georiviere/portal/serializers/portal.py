from collections import OrderedDict
from georiviere.portal.serializers.map import MapBaseLayerSerializer, MapGroupLayerSerializer, MapLayerSerializer
from georiviere.portal.models import Portal

from django.conf import settings
from django.contrib.gis.geos import Polygon

from rest_framework.serializers import ModelSerializer, SerializerMethodField


class MapSerializer(ModelSerializer):
    group = MapGroupLayerSerializer(many=True, source='mapgrouplayer_set')
    base_layers = MapBaseLayerSerializer(many=True, source='map_base_layers')
    bounds = SerializerMethodField()

    class Meta:
        model = Portal
        fields = (
            'group', 'base_layers', 'bounds'
        )

    def get_bounds(self, obj):
        if obj.spatial_extent:
            return obj.spatial_extent.transform(4326, clone=True).extent
        else:
            bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
            bbox.srid = settings.SRID
            return bbox.transform(4326, clone=True).extent


class PortalSerializer(ModelSerializer):
    map = MapSerializer(many=False, source='*')

    class Meta:
        model = Portal
        fields = (
            'id', 'name', 'map'
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        layers_without_group = instance.layers.filter(group_layer__isnull=True)
        if layers_without_group.exists():
            ret['map']['group'].append(
                OrderedDict({'label': None,
                             'layers': MapLayerSerializer(
                                 layers_without_group,
                                 many=True,
                             ).data}))
        return ret
