from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .profile import Profile

if TYPE_CHECKING:
    from .post import Post
    from .profile import Profile


class User(Base):
    Username: Mapped[str] = mapped_column(String(28), unique=True)

    posts: Mapped[list["Post"]] = relationship(back_populates="user")
    profile: Mapped["Profile"] = relationship(back_populates="user")

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, username={self.Username}"

    def __repr__(self):
        return str(self)
