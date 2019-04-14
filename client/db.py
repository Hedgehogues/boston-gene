import os
import sqlite3


class SQLiteClient:
    __sql_create_db = '''
    create table expression (
      gene_id text,
      expression float,
      project_id text,
      case_id text
    );'''


    __sql_insert = '''
    insert into expression (gene_id, expression, project_id, case_id)
    values (?, ?, ?, ?);
    '''

    __sql_delete = '''
    DELETE FROM expression WHERE project_id=? and case_id=?;
    '''

    __sql_select = '''
    select expression from expression where gene_id=? and project_id=?
    '''

    def __create_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute(self.__sql_create_db)
        conn.commit()
        conn.close()

    def __init__(self, db_path, hard=False):
        self.db_path = db_path
        if hard or not os.path.exists(db_path):
            self.__create_db()

    def insert_with_repl(self, df):
        conn = sqlite3.connect(self.db_path)
        conn.execute(self.__sql_delete, (df["project_id"].values[0], df["case_id"].values[0]))
        for row in df.values:
            values = (row[0], row[1], row[2], row[3])
            conn.execute(self.__sql_insert, values)
        conn.commit()
        conn.close()

    def select_genes(self, gene_id, project_id):
        conn = sqlite3.connect(self.db_path)
        resp = conn.execute(self.__sql_select, (gene_id, project_id))
        genes = [item[0] for item in resp.fetchall()]
        conn.close()
        return genes

