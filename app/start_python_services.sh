#!/bin/bash
exec python -u ./FlaskApp/app.py
#exec python -u ./FlaskApp/app.py &
#exec uvicorn FastApi.fast:app --host 0.0.0.0 --port 8000 --reload