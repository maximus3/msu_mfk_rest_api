from datetime import datetime

import dateutil.tz
import pytest

from app.utils import common


pytestmark = pytest.mark.asyncio


class TestGetDatetimeMskTzHandler:
    async def test_get_datetime_msk_tz_now(self):
        assert common.get_datetime_msk_tz() is not None

    async def test_get_datetime_msk_tz_datetime_no_tz(self):
        assert common.get_datetime_msk_tz(
            datetime(2022, 9, 29, 0, 0)
        ) == datetime(2022, 9, 29, 3, 0)

    async def test_get_datetime_msk_tz_datetime_utc_tz(self):
        assert common.get_datetime_msk_tz(
            datetime(2022, 9, 29, 0, 0, tzinfo=dateutil.tz.tzutc())
        ) == datetime(2022, 9, 29, 3, 0)

    async def test_get_datetime_msk_tz_datetime_msk_tz(self):
        assert common.get_datetime_msk_tz(
            datetime(
                2022, 9, 29, 0, 0, tzinfo=dateutil.tz.gettz('Europe/Moscow')
            )
        ) == datetime(2022, 9, 29, 0, 0)

    async def test_get_datetime_msk_tz_datetime_str_no_tz(self):
        assert common.get_datetime_msk_tz('2022-09-29T00:00:00') == datetime(
            2022, 9, 29, 3, 0
        )

    async def test_get_datetime_msk_tz_datetime_str_z_tz(self):
        assert common.get_datetime_msk_tz(
            '2022-10-21T15:00:00.000Z'
        ) == datetime(2022, 10, 21, 18, 0)

    async def test_get_datetime_msk_tz_datetime_str_utc_tz(self):
        assert common.get_datetime_msk_tz(
            '2022-10-21T15:00:00.000+00:00'
        ) == datetime(2022, 10, 21, 18, 0)

    async def test_get_datetime_msk_tz_datetime_str_msk_tz(self):
        assert common.get_datetime_msk_tz(
            '2022-10-25T20:27:19.000+03:00'
        ) == datetime(2022, 10, 25, 20, 27, 19)
