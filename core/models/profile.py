from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import UserRelationMixin


class Profile(UserRelationMixin, Base):
    _user_id_unique = True
    _user_back_populates = "profile"
    first_name: Mapped[str | None] = mapped_column(String(32), unique=False)
    last_name: Mapped[str | None] = mapped_column(String(32), unique=False)
    bio: Mapped[str | None]

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True)
