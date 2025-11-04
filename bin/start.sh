#!/bin/bash

# Start frontend (npm) in background
cd ./frontend
npm run start &

# Start backend (python manage.py)
cd ../backend
source venv/bin/activate
python ./manage.py