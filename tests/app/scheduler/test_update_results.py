import pytest

from app.scheduler import update_results


pytestmark = pytest.mark.asyncio


class TestJob:
    @pytest.mark.usefixtures('migrated_postgres')
    async def test_ok(self):
        # arrange

        # act
        await update_results.job()

        # assert
