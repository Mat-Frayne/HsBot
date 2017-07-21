"""."""

from sqlalchemy import Column, Integer, MetaData, String, Table, UniqueConstraint, DateTime, Boolean


class Model:
    """."""

    def __init__(self, engine):
        """."""
        self.metadata = MetaData()
        self.stats = Table(
            'Stats', self.metadata,
            #    Column('id', Integer, primary_key=True),
            Column('Stat', String, nullable=True),
            Column('Value', Integer),
            UniqueConstraint('Stat')
        )
        self.commands = Table(
            "Commands", self.metadata,
            Column("Command", String, nullable=True),
            Column("Created_at", DateTime),
            Column("Created_by", Integer),
            Column("Result", String),
            Column("Global", Boolean, default=False),
            Column("Channel", Integer),
            UniqueConstraint('Command')

        )
        self.metadata.create_all(engine)

# class Channels(Base):
#     """."""
#     __tablename__ = 'channels'
