import typer

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.entity import Provider
from core.config import pg, settings


DATABASE_URL = f'postgresql+psycopg2://{pg.user}:{pg.password}@{pg.host}:{pg.port}/{pg.db}'


engine = create_engine(DATABASE_URL, echo=settings.echo_var, future=True)
session_maker = sessionmaker(
    engine, expire_on_commit=False
)
session = session_maker()


def create_providers():
    providers = ['auth', 'yandex', 'google', 'vk']
    for provider in providers:
        obj = Provider(name=provider)
        session.add(obj)
        session.commit()
    typer.echo('Providers created successfully')


if __name__ == '__main__':
    typer.run(create_providers)
