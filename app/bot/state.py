from dataclasses import dataclass
from typing import Optional


@dataclass
class BookingState:
    service_id: Optional[int] = None
    worker_id: Optional[int] = None
    date: Optional[str] = None  # Jalali string for UI

USER_STATE = {}
ADMIN_STATE = {}
