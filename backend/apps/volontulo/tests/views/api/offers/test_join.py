# -*- coding: utf-8 -*-

"""
.. module:: test_join
"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.volontulo.tests.views.offers.commons import TestOffersCommons


class TestAuthenticatedUserJoinOffer(TestOffersCommons, APITestCase):

    """Tests for REST API's join offer view for authenticated user."""

    def setUp(self):
        """Set up each test."""
        super(TestAuthenticatedUserJoinOffer, self).setUp()
        self.client.login(username='admin@example.com', password='123admin')

    def test_user_join_offer_authenticated(self):
        """Test offer's created status for admin user."""
        response = self.client.post('/api/offers/1/join/')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_join_not_existing_offer(self):
        """Test offer's 404 status for non existing offer."""
        response = self.client.post('/api/offers/1999999999999/join/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestNotAuthenticatedUserJoinOffer(TestOffersCommons, APITestCase):

    """Tests for REST API's join offer view for not authenitcated user"""

    def test_user_join_offer_not_authenticated(self):
        """Test offer's forbidden status for not logged in user."""
        response = self.client.post('/api/offers/1/join/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
