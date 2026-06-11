# AGENTS.md

## Project overview
This repository is a small Python booking bot for a barber shop.

- Telegram bot entry point: app/bot/main.py
- FastAPI health API: app/api/app.py
- Database bootstrap: app/create_db.py
- Core DB setup: app/core/database.py

## Key architecture
- app/bot/: aiogram handlers and router wiring for user/admin flows.
- app/services/: booking, availability, and service/working-hours logic.
- app/models/: SQLAlchemy models for users, workers, services, appointments, holidays, and leaves.
- app/core/: shared database session and engine configuration.

## Development notes
- Use the existing virtual environment in .venv.
- Environment variables come from .env; BOT_TOKEN and DATABASE_URL are required for runtime.
- Database access typically uses SessionLocal from app/core/database.py and should be closed in a finally block.
- When adding or changing booking logic, keep the availability rules in app/services/availability_service.py and app/services/booking_service.py consistent.
- When adding a new bot command, register it in the relevant router file under app/bot/.

## Conventions to preserve
- Keep handlers simple and focused on Telegram/FastAPI responses.
- Prefer existing service functions over duplicating SQLAlchemy queries in handlers.
- Avoid broad except blocks; use specific exceptions when handling input errors.
- Preserve the current Persian user-facing messages unless a change explicitly requires otherwise.

## Useful commands
- Run the bot: python app/bot/main.py
- Start the API: uvicorn app.api.app:app --reload
- Create/update tables: python app/create_db.py

## Validation
- Before finishing changes, run a quick Python check such as python -m compileall .
- If you add models or DB logic, make sure the relevant session/booking paths still work with the existing schema.
