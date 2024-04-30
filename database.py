import datetime

from sqlalchemy import create_engine, String, Float, Boolean, INT
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, Session


class Base(DeclarativeBase):
    """Класс базы данных"""
    pass


class Film(Base):
    """Таблица films
        column[int] id: id фильма
        column[str] name: название фильма
        column[str] tags: слова по которым можно найти фильм (название написанное на разных языках и в разном регистре)
        column[float] rating: рейтинг фильма
        column[int] year: год производства фильма
        column[str] type: тип фильма (фильма, сериал, аниме и т.д.)
        column[str] genre: жанр фильма (если больше одного перечислены через ',')
        column[str] country: страна производства фильма(если больше одного перечислены через ',')
        """
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
        """При вызове str() переводит объект в строку Film(id=id фильма, name=название фильма)"""
        return f"Film(id={self.id!r}, name={self.name!r})"


class User(Base):
    """Таблица users
        column[int] id: id Telegram пользователя
        column[str] registration: дата регистрации пользователя
        column[bool] vip: флаг есть ли у пользователя vip
        """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    registration: Mapped[str] = mapped_column(String(30))
    vip: Mapped[bool] = mapped_column(Boolean)

    def __repr__(self):
        """При вызове str() переводит объект в строку Film(id=id фильма, name=название фильма)"""
        return f"User(id={self.id!r}, registration={self.registration!r}, vip={self.vip!r})"


def search_film(partial_title):
    """Возвращает фильм по неполному названию"""
    films = session.query(Film).where(Film.tags.ilike(f'%{partial_title}%')).first()
    return films


def add_user(user_id):
    """Добавляет пользователя в таблицу БД"""
    session.add(User(id=user_id, registration=datetime.datetime.now().strftime("%d.%m.%y %H:%M"), vip=False))

    session.commit()


def find_user(user_id):
    """Возвращает пользователя по Telegram id"""
    user = session.query(User).filter_by(id=user_id).first()
    return user


# создание сессии
engine = create_engine("sqlite:///database/telebot.db")
session = Session(bind=engine)
