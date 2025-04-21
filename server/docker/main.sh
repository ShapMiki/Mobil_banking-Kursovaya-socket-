#!/bin/bash

alembic upgrade head
echo "⏳ Ждём PostgreSQL..."
sleep 10
python main.py