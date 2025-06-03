#!/bin/bash
export $(cat .env.example | grep -v ^# | xargs)
uvicorn app:app --reload --host 0.0.0.0 --port 8080
