from django.core import mail
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from unittest import mock
from geotrek.common.utils.testdata import get_dummy_uploaded_image, get_dummy_uploaded_file

from georiviere.contribution.models import (Contribution, ContributionQuality, ContributionLandscapeElements,
                                            ContributionQuantity, ContributionFaunaFlora, ContributionPotentialDamage,)
from georiviere.contribution.tests.factories import (ContributionFactory, ContributionQuantityFactory,
                                                     NaturePollutionFactory, SeverityTypeTypeFactory,
                                                     CustomContributionTypeFactory,
                                                     CustomContributionTypeStringFieldFactory,
                                                     CustomContributionTypeBooleanFieldFactory,
                                                     CustomContributionFactory,
                                                     CustomContributionTypeFloatFieldFactory, )
from georiviere.main.models import Attachment
from georiviere.observations.tests.factories import StationFactory
from georiviere.portal.tests.factories import PortalFactory

from rest_framework.test import APITestCase
from rest_framework.test import APIClient


class ContributionViewPostTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.portal = PortalFactory.create()
        cls.nature_pollution = NaturePollutionFactory.create(label="Baz")
        cls.severity = SeverityTypeTypeFactory.create(label="Boo")

    def test_contribution_structure(self):
        url = reverse('api_portal:contributions-json_schema',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertSetEqual(set(response.json().keys()), {'type', 'required', 'properties', 'allOf'})

    def test_contribution_landscape_element(self):
        self.assertEqual(len(mail.outbox), 0)
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.post(url, data={"geom": "POINT(0 0)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "Contribution Élément Paysagers",'
                                                             '"type": "Doline"}'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContributionLandscapeElements.objects.count(), 1)
        contribution = Contribution.objects.first()
        landscape_element = contribution.landscape_element
        self.assertEqual(contribution.email_author, 'x@x.x')
        self.assertEqual(landscape_element.get_type_display(), 'Doline')
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(MANAGERS=[("Fake", "fake@fake.fake"), ])
    def test_contribution_create_send_manager_contributor(self):
        self.assertEqual(len(mail.outbox), 0)
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        self.client.post(url, data={"geom": "POINT(0 0)",
                                    "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                  '"category": "Contribution Élément Paysagers",'
                                                  '"type": "Doline"}'})
        self.assertEqual(len(mail.outbox), 2)

    def test_contribution_quality(self):
        self.assertEqual(len(mail.outbox), 0)
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.post(url, data={"geom": "POINT(0 0)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "Contribution Qualité",'
                                                             '"type": "Pollution",'
                                                             '"nature_pollution": "Baz"}'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContributionQuality.objects.count(), 1)
        contribution = Contribution.objects.first()
        quality = contribution.quality
        self.assertEqual(quality.nature_pollution.label, 'Baz')
        self.assertEqual(contribution.email_author, 'x@x.x')
        self.assertEqual(quality.get_type_display(), 'Pollution')
        self.assertEqual(len(mail.outbox), 1)

    def test_contribution_quantity(self):
        self.assertEqual(len(mail.outbox), 0)
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr', 'format': 'json'})
        response = self.client.post(url, data={"geom": "POINT(0 0)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "Contribution Quantité",'
                                                             '"type": "A sec"}'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContributionQuantity.objects.count(), 1)
        contribution = Contribution.objects.first()
        quantity = contribution.quantity
        self.assertEqual(contribution.email_author, 'x@x.x')
        self.assertEqual(quantity.get_type_display(), 'A sec')
        self.assertEqual(len(mail.outbox), 1)

    def test_contribution_faunaflora(self):
        self.assertEqual(len(mail.outbox), 0)
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr', 'format': 'json'})
        response = self.client.post(url, data={"geom": "POINT(4 43.5)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "Contribution Faune-Flore",'
                                                             '"type": "Espèce invasive",'
                                                             '"description": "test",'
                                                             '"severity": "Boo"}'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContributionFaunaFlora.objects.count(), 1)
        contribution = Contribution.objects.first()
        fauna_flora = contribution.fauna_flora
        self.assertEqual(contribution.email_author, 'x@x.x')
        self.assertEqual(fauna_flora.get_type_display(), 'Espèce invasive')
        self.assertEqual(len(mail.outbox), 1)

    def test_contribution_potential_damages(self):
        self.assertEqual(len(mail.outbox), 0)
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr', 'format': 'json'})
        response = self.client.post(url, data={"geom": "POINT(4 42.5)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "Contribution Dégâts Potentiels",'
                                                             '"type": "Éboulements"}'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContributionPotentialDamage.objects.count(), 1)
        contribution = Contribution.objects.first()
        potential_damage = contribution.potential_damage
        self.assertEqual(contribution.email_author, 'x@x.x')
        self.assertEqual(potential_damage.get_type_display(), 'Éboulements')
        self.assertEqual(len(mail.outbox), 1)

    def test_contribution_category_does_not_exist(self):
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.post(url, data={"geom": "POINT(0 0)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "Foo"}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'properties': ["'Foo' is not one of "
                                                          "['Contribution Quantité', "
                                                          "'Contribution Qualité', "
                                                          "'Contribution Faune-Flore', "
                                                          "'Contribution Élément Paysagers', "
                                                          "'Contribution Dégâts Potentiels']"]})

    @mock.patch('georiviere.contribution.schema.get_contribution_properties')
    def test_contribution_category_model_does_not_exist(self, mocked):
        def json_property():
            json_schema_properties = {'name_author': {
                'type': "string",
                'title': "Name author",
                "maxLength": 128
            }, 'first_name_author': {
                'type': "string",
                'title': "First name author",
                "maxLength": 128
            }, 'email_author': {
                'type': "string",
                'title': "Email",
                'format': "email"
            }, 'date_observation': {
                'type': "string",
                'title': "Observation's date",
                'format': 'date'
            }, 'description': {
                'type': "string",
                'title': 'Description'
            }, 'category': {
                "type": "string",
                "title": "Category",
                "enum": [
                    'foo',
                ],
            }
            }
            return json_schema_properties

        mocked.side_effect = json_property
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.post(url, data={"geom": "POINT(0 0)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "foo"}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'Error': "La catégorie n'est pas valide"})

    @mock.patch('georiviere.contribution.schema.get_contribution_allOf')
    def test_contribution_category_model_other_error(self, mocked):
        def json_property():
            json_schema_all_of = [{'if': {'properties': {'category': {'const': 'Contribution Quantité'}}},
                                   'then': {'properties': {'type': {'type': 'string', 'title': 'Type',
                                                                    'enum': ['Landing', ]}}}}]
            return json_schema_all_of

        mocked.side_effect = json_property
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.post(url, data={"geom": "POINT(0 0)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "Contribution Quantité",'
                                                             '"type": "Landing"}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'Error': "KeyError 'Landing'"})

    def test_contribution_attachments(self):
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr', 'format': 'json'})
        image_1 = get_dummy_uploaded_image()
        image_2 = get_dummy_uploaded_image()
        client = APIClient()
        data = {"geom": "POINT(0 0)",
                "image_1": image_1,
                "image_2": image_2,
                "properties": '{"email_author": "x@x.x", "date_observation": "2022-08-16", '
                              '"category": "Contribution Élément Paysagers", "type": "Doline"}',
                }
        response = client.post(url, data=data,)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContributionLandscapeElements.objects.count(), 1)
        contribution = Contribution.objects.first()
        landscape_element = contribution.landscape_element
        self.assertEqual(contribution.email_author, 'x@x.x')
        self.assertEqual(landscape_element.get_type_display(), 'Doline')
        self.assertEqual(Attachment.objects.count(), 2)
        self.assertEqual(contribution.attachments.count(), 2)

    def test_contribution_attachments_fail(self):
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr', 'format': 'json'})
        file_1 = get_dummy_uploaded_file()
        data = {"geom": "POINT(0 0)",
                "image_1": file_1,
                "properties": '{"email_author": "x@x.x", "date_observation": "2022-08-16", '
                              '"category": "Contribution Élément Paysagers", "type": "Doline"}',
                }
        response = self.client.post(url, data=data,)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContributionLandscapeElements.objects.count(), 1)
        contribution = Contribution.objects.first()
        landscape_element = contribution.landscape_element
        self.assertEqual(contribution.email_author, 'x@x.x')
        self.assertEqual(landscape_element.get_type_display(), 'Doline')
        self.assertEqual(Attachment.objects.count(), 0)

    @mock.patch('georiviere.main.models.Attachment.full_clean')
    def test_contribution_attachments_not_allowed(self, mocked):
        mocked.side_effect = ValidationError('Problem attachment')
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr', 'format': 'json'})
        file_1 = SimpleUploadedFile('x', b'', content_type='application/json')
        data = {"geom": "POINT(0 0)",
                "image_1": file_1,
                "properties": '{"email_author": "x@x.x", "date_observation": "2022-08-16", '
                              '"category": "Contribution Élément Paysagers", "type": "Doline"}',
                }
        response = self.client.post(url, data=data,)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContributionLandscapeElements.objects.count(), 1)
        contribution = Contribution.objects.first()
        landscape_element = contribution.landscape_element
        self.assertEqual(contribution.email_author, 'x@x.x')
        self.assertEqual(landscape_element.get_type_display(), 'Doline')
        self.assertEqual(Attachment.objects.count(), 0)


class ContributionViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.portal = PortalFactory.create()
        cls.contribution_without_category = ContributionFactory.create(published=True, portal=cls.portal,
                                                                       description="x")
        cls.contribution = ContributionFactory.create(published=True, portal=cls.portal, description="foo")
        cls.contribution_other_portal = ContributionFactory.create(published=True)
        cls.contribution_not_published = ContributionFactory.create(published=False, portal=cls.portal)
        cls.contribution_quantity = ContributionQuantityFactory.create(contribution=cls.contribution)
        cls.other_contribution_quantity = ContributionQuantityFactory.create(
            contribution=cls.contribution_not_published)
        cls.other_contribution_quantity_2 = ContributionQuantityFactory.create(
            contribution=cls.contribution_other_portal)

    def test_contribution_list(self):
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertDictEqual(response.json()[0], {'id': self.contribution.pk,
                                                  'category': 'Contribution Quantité',
                                                  'description': 'foo', 'type': 'A sec',
                                                  'attachments': []})

    def test_contribution_detail(self):
        url = reverse('api_portal:contributions-detail',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr', 'pk': self.contribution.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(set(response.json()), {'id', 'category', 'description', 'type', 'attachments'})

    def test_contribution_geojson_list(self):
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr',
                              'format': 'geojson'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertSetEqual(set(response.json().keys()), {'features', 'type'})

    def test_contribution_geojson_detail(self):
        url = reverse('api_portal:contributions-detail',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr', 'pk': self.contribution.pk,
                              'format': 'geojson'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertSetEqual(set(response.json().keys()), {'id', 'type', 'geometry', 'properties'})
        self.assertSetEqual(set(response.json()['properties']), {'category', })


class CustomContributionTypeVIewSetAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.portal = PortalFactory.create()
        cls.station = StationFactory()
        cls.custom_contribution_type = CustomContributionTypeFactory()
        cls.custom_contribution_type.stations.add(cls.station)
        cls.string_field = CustomContributionTypeStringFieldFactory(
            custom_type=cls.custom_contribution_type,
            label="Field string",
        )
        cls.string_field_blank = CustomContributionTypeStringFieldFactory(
            custom_type=cls.custom_contribution_type,
            label="Field string empty",
        )
        CustomContributionTypeBooleanFieldFactory(
            custom_type=cls.custom_contribution_type,
            label="Field boolean",
        )
        CustomContributionTypeFloatFieldFactory(
            custom_type=cls.custom_contribution_type,
            label="Field float",
        )
        cls.contribution_validated = CustomContributionFactory(custom_type=cls.custom_contribution_type,
                                                               station=cls.station, validated=True, portal=cls.portal)
        cls.contribution_unvalidated = CustomContributionFactory(custom_type=cls.custom_contribution_type,
                                                                 station=cls.station, validated=False, portal=cls.portal)

    def get_list_url(self):
        return reverse('api_portal:custom_contribution_types-list',
                       kwargs={'portal_pk': self.portal.pk, 'lang': 'fr', })

    def get_contribution_url(self):
        return reverse('api_portal:custom_contribution_types-custom-contributions',
                       kwargs={'portal_pk': self.portal.pk, 'lang': 'fr', 'pk': self.custom_contribution_type.pk})

    def get_detail_url(self, pk):
        return reverse('api_portal:custom_contribution_types-detail',
                       kwargs={'portal_pk': self.portal.pk, 'lang': 'fr', 'pk': pk, })

    def test_list(self):
        response = self.client.get(self.get_list_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_detail(self):
        response = self.client.get(self.get_detail_url(self.custom_contribution_type.pk))
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        data = {
            "station": self.station.pk,
            "field_string": "string",
            "field_boolean": True,
            "contributed_at": "2020-01-01T00:00"
        }
        response = self.client.post(self.get_contribution_url(), data=data, format='json')
        data = response.json()
        self.assertEqual(response.status_code, 201, data)

    def test_no_values_on_not_required(self):
        """Null and empty values should be accepted on non required fields"""
        data = {
            "station": self.station.pk,
            self.string_field.key: "",
            self.string_field_blank.key: "",
            "field_boolean": "",
            "field_float": 1.1,
            "contributed_at": "2020-01-01T00:00"
        }
        response = self.client.post(self.get_contribution_url(), data=data, format='json')
        data = response.json()
        self.assertEqual(response.status_code, 201, data)
        self.assertEqual(data['field_float'], 1.1)

    def test_validated_not_in_list(self):
        response = self.client.get(self.get_contribution_url())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(self.contribution_validated.pk, [c['id'] for c in data])

    def test_unvalidated_not_in_list(self):
        response = self.client.get(self.get_contribution_url())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertNotIn(self.contribution_unvalidated.pk, [c['id'] for c in data])
