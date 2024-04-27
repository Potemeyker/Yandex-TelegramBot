import datetime

from sqlalchemy import create_engine, String, Float, Boolean, INT
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


class Film(Base):
    __tablename__ = "films"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    tags: Mapped[str] = mapped_column(String(100))
    rating: Mapped[float] = mapped_column(Float)
    year: Mapped[int] = mapped_column(INT)
    type: Mapped[str] = mapped_column(String(30))
    genre: Mapped[str] = mapped_column(String(30))
    country: Mapped[str] = mapped_column(String(30))

    def __repr__(self):
        return f"Film(id={self.id!r}, name={self.name!r})"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    registration: Mapped[str] = mapped_column(String(30))
    vip: Mapped[bool] = mapped_column(Boolean)

    def __repr__(self):
        return f"User(id={self.id!r}, registration={self.registration!r}, vip={self.vip!r})"


# Функция для поиска фильма по неполному названию
def search_film(partial_title):
    films = session.query(Film).where(Film.tags.ilike(f'%{partial_title}%')).first()
    return films


def add_user(user_id):
    session.add(User(id=user_id, registration=datetime.datetime.now().strftime("%d.%m.%y %H:%M"), vip=False))

    session.commit()


def find_user(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    return user


engine = create_engine("sqlite:///database/telebot.db")
session = Session(bind=engine)
