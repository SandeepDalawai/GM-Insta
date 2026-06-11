from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import mysql
from models import db
from app import app
import os

def dump_schema():
    with app.app_context():
        # Set database URI to a dummy one just so we can initialize the engine if needed
        # We can also just compile against the mysql dialect directly
        engine = db.engine
        
        with open('schema.sql', 'w') as f:
            for table in db.metadata.sorted_tables:
                create_expr = CreateTable(table).compile(dialect=mysql.dialect())
                f.write(str(create_expr).strip() + ";\n\n")
        print("Schema dumped to schema.sql")

if __name__ == "__main__":
    dump_schema()
