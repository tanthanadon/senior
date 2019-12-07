from sshtunnel import SSHTunnelForwarder
import mysql.connector as db
import pandas as pd

# ssh variables
host = '10.34.2.23'
localhost = '127.0.0.1'
ssh_username = 'thanadon'
ssh_password = 'tan'


# database variables
user='thanadon'
password='tan'
database='ghtorrent'

def query(q):
    with SSHTunnelForwarder(
        (host, 22),
        ssh_username=ssh_username,
        ssh_password=ssh_password,
        remote_bind_address=(localhost, 3306)
    ) as server:
        print(server.local_bind_port)
        # open a connection to the MySQL server
        # store the connection object in the variable cnx
        conn = db.connect(host=localhost,
                               port=server.local_bind_port,
                               user=user,
                               passwd=password,
                               db=database)
        print(conn)
        df = pd.read_sql_query(q, conn)
        conn.close()
    return df

q = "SELECT * FROM projects LIMIT 5"
df = query(q)
print(df)