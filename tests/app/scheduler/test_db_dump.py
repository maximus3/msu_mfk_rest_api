from app.database import models
from app.scheduler import db_dump


class TestAllTablesDump:
    def test_all_tables_dump(self):
        """Test that all tables are dumping."""
        table_names = [
            model.__tablename__ for model in models.BaseModel.__subclasses__()
        ] + ['alembic_version']
        assert set(db_dump.TABLE_NAMES) == set(table_names)
