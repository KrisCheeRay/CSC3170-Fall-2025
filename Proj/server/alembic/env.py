from __future__ import annotations
import os
import sys
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool

THIS_DIR = os.path.dirname(os.path.abspath(__file__))   
SERVER_DIR = os.path.dirname(THIS_DIR)                  
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)


from app.database import SQLALCHEMY_DATABASE_URL, Base   
from app import models                                    

config = context.config
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL) 

if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata  

def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True,  
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=True,  
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
