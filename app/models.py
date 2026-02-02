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

    # TVMaze person id
    id = Column(Integer, primary_key=True, index=True)

    # which show this person belongs to
    show_id = Column(Integer, ForeignKey("shows.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False)
    birthday = Column(String, nullable=True)  # store as ISO date string: "YYYY-MM-DD"

    show = relationship("Show", back_populates="cast")

    __table_args__ = (
        # same person can appear in multiple shows, so uniqueness is (person_id, show_id)
        UniqueConstraint("id", "show_id", name="uq_cast_person_show"),
        Index("ix_cast_show_id", "show_id"),
    )
