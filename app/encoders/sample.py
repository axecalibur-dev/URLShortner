"""
url_service.py - Service layer coordinating Ticket ID allocation,
Base62 encoding/decoding, and persistence against PostgreSQL.
"""

import logging
from typing import Optional
import psycopg2
from psycopg2 import errors

from app.manager.range_manager import RangeManager
# Direct imports matching your exact encoder definitions
from encoder import encode_base62, deccode_base62

logger = logging.getLogger(__name__)


class URLServiceError(Exception):
    """Base exception for service layer operations."""
    pass


class ShortCodeCollisionError(URLServiceError):
    """Raised if an insert hits a primary key conflict on short_code."""
    pass


class URLService:
    def __init__(self, db_pool, range_manager: RangeManager):
        """
        Args:
            db_pool: Thread-safe PostgreSQL connection pool.
            range_manager: Initialized RangeManager instance.
        """
        self.db_pool = db_pool
        self.range_manager = range_manager

    def shorten_url(self, original_url: str) -> str:
        """
        Generates a unique short code and stores the mapping in `urls`.

        Steps:
          1. Allocates an integer ID atomically in memory via RangeManager.
          2. Encodes integer ID into a Base62 token using encode_base62.
          3. Persists (short_code, original_url) to the urls table.
        """
        # Step 1: Thread-safe in-memory ticket assignment
        ticket_id = self.range_manager.next_id()

        # Step 2: Encode using your Base62 logic
        short_code = encode_base62(ticket_id)

        # Step 3: Insert into migrated `urls` table
        conn = self.db_pool.getconn()
        try:
            with conn:
                with conn.cursor() as cursor:
                    insert_query = """
                        INSERT INTO urls (short_code, original_url)
                        VALUES (%s, %s);
                    """
                    cursor.execute(insert_query, (short_code, original_url))

            logger.info("Created short code '%s' for ID %d", short_code, ticket_id)
            return short_code

        except errors.UniqueViolation as exc:
            logger.error("Primary key conflict on short_code '%s': %s", short_code, exc)
            raise ShortCodeCollisionError(f"Duplicate code encountered: {short_code}") from exc

        except psycopg2.Error as exc:
            logger.error("Database write error for code '%s': %s", short_code, exc)
            raise URLServiceError("Failed to store URL record.") from exc

        finally:
            self.db_pool.putconn(conn)

    def resolve_url(self, short_code: str) -> Optional[str]:
        """
        Retrieves the original URL for an active short code.

        Validates the short_code structure via deccode_base62 before querying the DB,
        then performs a primary key lookup on `short_code`.
        """
        # Fast input validation: ensure short_code adheres to alphabet/encoding
        try:
            _ = deccode_base62(short_code)
        except (ValueError, TypeError):
            # Not a valid Base62 string produced by this system
            return None

        conn = self.db_pool.getconn()
        try:
            with conn:
                with conn.cursor() as cursor:
                    select_query = """
                        SELECT original_url
                        FROM urls
                        WHERE short_code = %s AND is_active = TRUE;
                    """
                    cursor.execute(select_query, (short_code,))
                    row = cursor.fetchone()

                    if row:
                        return row[0]
                    return None

        except psycopg2.Error as exc:
            logger.error("Database lookup error for code '%s': %s", short_code, exc)
            raise URLServiceError(f"Error fetching URL for '{short_code}'") from exc

        finally:
            self.db_pool.putconn(conn)

    def deactivate_url(self, short_code: str) -> bool:
        """
        Soft-deletes a link by setting `is_active = FALSE`.
        """
        conn = self.db_pool.getconn()
        try:
            with conn:
                with conn.cursor() as cursor:
                    update_query = """
                        UPDATE urls
                        SET is_active = FALSE,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE short_code = %s AND is_active = TRUE;
                    """
                    cursor.execute(update_query, (short_code,))
                    return cursor.rowcount > 0

        except psycopg2.Error as exc:
            logger.error("Failed deactivating short code '%s': %s", short_code, exc)
            raise URLServiceError(f"Error deactivating '{short_code}'") from exc

        finally:
            self.db_pool.putconn(conn)