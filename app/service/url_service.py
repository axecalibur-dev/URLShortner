import logging
from typing import Optional
import psycopg2
from psycopg2 import errors
from app.encoders.encoder import encode_base62, deccode_base62
from app.manager.range_manager import RangeManager


class URLServiceError(Exception):
    pass


class ShortCodeCollisionError(URLServiceError):
    pass


class URLService:
    def __init__(self, db_pool, range_manager: RangeManager):
        self.db_pool = db_pool
        self.range_manager = range_manager


    def shorten_url(self, short_code: str) -> str:
        ticket_id = self.range_manager.next_id()
        short_code = encode_base62(ticket_id)


        conn = self.db_pool.get_conn()
        try:
            with conn:
                with conn.cursor() as cursor:
                    insert_query = """
                        INSERT INTO urls (short_code, ticket_id)
                        VALUES (%s, %s)
                    """

                    cursor.execute(insert_query, (short_code, ticket_id))
            return short_code

        except errors.UniqueViolation as exc:
            raise ShortCodeCollisionError("Duplicate short code error") from exc

        except psycopg2.Error as exc:
            raise URLServiceError("Error connecting to database") from exc


        finally:
            self.db_pool.put_conn(conn)


    def resolve_url(self, short_code: str):
        try:
            _ = deccode_base62(short_code)
        except ( ValueError, TypeError ):
            return None

        conn = self.db_pool.getconn()
        try:
            with conn:
                with conn.cursor() as cursor:
                    select_query = """
                    SELECT original_url from urls where short_code = %s AND is_active = TRUE
                    """
                    cursor.execute(select_query, (short_code,))
                    row = cursor.fetchone()
                    if row:
                        return row[0]
                    return None

        except psycopg2.Error as exc:
            raise URLServiceError("Error connecting to database") from exc


        finally:
            self.db_pool.putconn(conn)


    def deactivate_url(self, short_code: str):
        conn = self.db_pool.getconn()
        try:
            with conn:
                with conn.cursor() as cursor:
                    update_query = """
                    UPDATE urls SET is_active = FALSE updated_at = CURRENT_TIMESTAMP
                    WHERE short_code = %s and is_active = TRUE
                    """


                    cursor.execute(update_query, (short_code,))
                    return cursor.rowcount > 0



        except psycopg2.Error as exc:
            raise URLServiceError("Error connecting to database") from exc

        finally:
            self.db_pool.putconn(conn)