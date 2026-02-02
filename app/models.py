from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from .db import Base

class Show(Base):
    __tablename__ = "shows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # relationship: Show -> many CastMembers
    cast = relationship("CastMember", back_populates="show", cascade="all, delete-orphan")


class CastMember(Base):
    __tablename__ = "cast_members"

    # person id from TVMaze (NOT unique globally in our table)
    person_id = Column(Integer, primary_key=True)

    # show id (part of composite PK)
    show_id = Column(Integer, ForeignKey("shows.id", ondelete="CASCADE"), primary_key=True)

    name = Column(String, nullable=False)
    birthday = Column(String, nullable=True)

    show = relationship("Show", back_populates="cast")

    __table_args__ = (
        Index("ix_cast_show_id", "show_id"),
    )

