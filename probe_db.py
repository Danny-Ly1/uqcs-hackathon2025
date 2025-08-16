import psycopg2

HOST="10.89.76.206"; DB="postgres"; USER="postgres"; PWD="1234"; PORT=5432

with psycopg2.connect(host=HOST, dbname=DB, user=USER, password=PWD, port=PORT) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE SCHEMA IF NOT EXISTS sussyballs;
            CREATE TABLE IF NOT EXISTS sussyballs.pings(
              id bigserial PRIMARY KEY,
              from_user text NOT NULL,
              client inet,
              message text,
              created_at timestamptz NOT NULL DEFAULT now()
            );
        """)
        cur.execute("""
            INSERT INTO sussyballs.pings(from_user, client, message)
            VALUES (current_user, inet_client_addr(), 'probe via python')
            RETURNING id, created_at;
        """)
        print("Inserted:", cur.fetchone())
