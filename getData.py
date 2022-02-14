from bs4 import BeautifulSoup
import psycopg2 as db
import pandas.io.sql as sqlio

def getDataAtDB(select_mun, select_dp, select_crime):
    onn = db.connect(host='ec2-54-235-98-1.compute-1.amazonaws.com', database='d1q1uf1agi5jm9', 
                        user='qyvehyzhrsbxuk', password='7a9e0bdf8f04e97859eeee9bccf4c57e7a9390d0707882f60e7f95d8892a9f54', port='5432')


    
    if select_dp == "Todos":
        sql_command = """
            SELECT o.datas, SUM(o.ocorrencia)
            FROM crime_ocorrencia o, crime_localizacao l
            WHERE o.id = l.id and l.municipio = '{}' and l.tipo = '{}'
            GROUP BY o.datas ORDER BY o.datas;
         """.format(select_mun, select_crime)
    else:
        sql_command = """
            SELECT o.datas, o.ocorrencia 
            FROM crime_ocorrencia o, crime_localizacao l 
            WHERE o.id = l.id and l.municipio = '{}' 
            and l.delegacia = '{}' and l.tipo = '{}'
        """.format(select_mun, select_dp, select_crime)
    dat = sqlio.read_sql_query(sql_command, conn)

    return dat

def getDataAno(select_dp, select_ano):
    onn = db.connect(host='ec2-54-235-98-1.compute-1.amazonaws.com', database='d1q1uf1agi5jm9', 
                        user='qyvehyzhrsbxuk', password='7a9e0bdf8f04e97859eeee9bccf4c57e7a9390d0707882f60e7f95d8892a9f54', port='5432')



    if select_ano <= 2021:
        sql_command = """
            SELECT l.tipo, SUM(o.ocorrencia) as ocorrencias
            FROM crime_localizacao l, crime_ocorrencia o
            WHERE l.id = o.id AND l.delegacia = '{}' and EXTRACT(YEAR from o.datas) = '{}'
            GROUP BY l.tipo;
        """.format(select_dp, select_ano)
        dat = sqlio.read_sql_query(sql_command, conn)
    else:
        sql_command = """
            SELECT l.tipo, o.datas, o.ocorrencia
            FROM crime_localizacao l, crime_ocorrencia o
            WHERE l.id = o.id AND l.delegacia = '{}'
            
        """.format(select_dp, select_ano)
        dat = sqlio.read_sql_query(sql_command, conn)

    return dat