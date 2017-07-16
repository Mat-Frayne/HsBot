"""."""

from sqlalchemy import Column, Integer, MetaData, String, Table, UniqueConstraint


class Model:
    """."""

    def __init__(self, engine):
        """."""
        self.metadata = MetaData()
        self.stats = Table('Stats', self.metadata,
                           #    Column('id', Integer, primary_key=True),
                           Column('Stat', String, nullable=True),
                           Column('Value', Integer),
                           UniqueConstraint('Stat')
                          )

        self.metadata.create_all(engine)

# class Channels(Base):
#     """."""
#     __tablename__ = 'channels'
