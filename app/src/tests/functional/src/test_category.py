from http import HTTPStatus

import pytest


class TestOutgoingCategory:
    def setup_method(self):
        self.endpoint = "/api/v1/categories/outgoing/"

    @pytest.mark.asyncio
    async def test_all_films(self, access_token_admin, client):
        response = await client.get(self.endpoint, headers=access_token_admin)
        assert response.status_code == HTTPStatus.OK
