import threading
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RangeExhaustedException(Exception):
    pass

class RangeManager:
    def __init__(self, db_pool , instance_id:str):
        self.db_pool = db_pool
        self.instance_id = instance_id



        self.current_id : Optional[int] = None
        self.range_end:Optional[int] = None


        self._lock = threading.Lock()
        self._fetch_next_range()



    def _fetch_next_range(self):
        conn = self.db_pool.connection()
        try:
            with conn:
                with conn.cursor() as cursor:
                    claim_query = """
                        SELECT id, range_start , range_end
                        FROM ticket_ranges
                        where is_exhausted = FALSE
                        ORDER BY id ASC
                        LIMIT 1
                        FOR UPDATE SKIP LOCKED
                    
                    """

                    cursor.execute(claim_query)
                    row = cursor.fetchone()

                    if not row:
                        raise RangeExhaustedException(
                            "Error : All ticket ranges are exhausted."
                        )
                    range_db_id , r_start, r_end = row


                    update_query = """
                        UPDATE ticket_ranges
                        SET is_exhausted = TRUE
                        claimed_by = %s, 
                        updated_at = NOW()
                        where id = %s
                    """


                    cursor.execute(update_query, (self.instance_id, range_db_id))

            self.current_id = r_start
            self.range_end = r_end

            logger.info(
                f"Range claimed: [{self.current_id} - {self.range_end}] "
                f"(Capacity: {self.range_end - self.current_id + 1:,} IDs)"
            )

        finally:
            self.db_pool.putconn(conn)

    def next_id(self):
        with self._lock:
            if self.current_id is None or self.current_id > self.range_end:
                self._fetch_next_range()
            ticket_id = self.current_id
            self.current_id += 1
            return ticket_id
