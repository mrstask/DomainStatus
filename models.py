from datetime import datetime
from typing import Optional

import databases
import ormar
import sqlalchemy

# from settings import PostgresConfiguration
from settings import DATABASE_URL
metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)


class Zone(ormar.Model):
    class Meta:
        tablename = 'zones'
        metadata = metadata
        database = database

    name: str = ormar.String(primary_key=True, max_length=100, allow_blank=False)
    useless: bool = ormar.Boolean(default=False)


class Domain(ormar.Model):
    class Meta:
        tablename = 'domains'
        metadata = metadata
        database = database

    pk: int = ormar.Integer(primary_key=True, allow_blank=False)
    domain_name: str = ormar.String(max_length=100, allow_blank=False)
    zone: str = ormar.ForeignKey(Zone, nullable=True)

    status_code: int = ormar.Integer(nullable=True)
    www: bool = ormar.Boolean(default=False)
    ssl: bool = ormar.Boolean(default=False)

    server: str = ormar.String(max_length=100, nullable=True)
    content_type: str = ormar.String(max_length=100, nullable=True)
    content_length: str = ormar.Integer(nullable=True)
    last_modified: datetime = ormar.DateTime(nullable=True)
    encoding: str = ormar.String(max_length=100, nullable=True)
    text: str = ormar.Text(nullable=True)
    locked: bool = ormar.Boolean(default=False)


class Task(ormar.Model):
    class Meta:
        tablename = 'tasks'
        metadata = metadata
        database = database

    pk: int = ormar.Integer(primary_key=True, allow_blank=False)
    quantity: str = ormar.String(max_length=100, allow_blank=False)
    threads: str = ormar.ForeignKey(Zone, nullable=True)
    started: datetime = ormar.DateTime()
    finished: datetime = ormar.DateTime(nullable=True)


if __name__ == '__main__':
    # engine = sqlalchemy.create_engine(PostgresConfiguration().postgres_db_path)
    engine = sqlalchemy.create_engine(DATABASE_URL)
    metadata.drop_all(engine)
    metadata.create_all(engine)



