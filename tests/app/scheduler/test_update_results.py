import pytest

from app.scheduler import update_results


pytestmark = pytest.mark.asyncio


@pytest.mark.usefixtures('migrated_postgres')
class TestJob:
    async def test_run(self):
        # arrange
        # act
        await update_results.job()
        # assert

    async def test_ok(  # pylint: disable=too-many-arguments,unused-argument  # TODO
        self,
        created_course,
        created_student,
        student_course,
        created_contest,
        mock_make_request_to_yandex_contest_v2,
    ):
        # arrange
        _ = mock_make_request_to_yandex_contest_v2(
            {
                f'contests/{created_contest.yandex_contest_id}/'
                f'submissions?page=1&pageSize=100': {
                    'status_code': 200,
                    'json': {},
                },
                f'contests/{created_contest.yandex_contest_id}/'
                f'submissions/multiple?runIds={123}': {  # TODO
                    'status_code': 200,
                    'json': {},
                },
            }
        )

        # act
        await update_results.job()
        # assert
