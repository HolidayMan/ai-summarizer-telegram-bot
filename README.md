# AI Summarizer Telegram Bot

This Telegram bot records all messages in group chats and provides daily summaries using LLM API. The bot uses aiogram for Telegram interactions, and uses SQLAlchemy with PostgreSQL for data storage.

## Features

- Records all messages in group chats with timestamps
- Generates daily summaries using LLM API
- Sends summaries to all chats at the end of the day
- Parallel processing for efficient summary distribution
- Containerized with Docker and docker-compose

## Setup

1. Clone the repository
2. Create a `.env` file based on `.env.example`
3. Run with Docker Compose:
4. 