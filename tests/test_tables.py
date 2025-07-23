from sqlalchemy import create_engine, inspect

engine = create_engine("postgresql+psycopg2://postgres:pgsql@db:5432/secrets")
inspector = inspect(engine)
print(inspector.get_table_names())
