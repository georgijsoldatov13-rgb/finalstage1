# 🤖 Backdoor Educator (Gemini Flash 2.5)

Интеллектуальная система для генерации учебных тестов на лету. Приложение использует Google Gemini API для создания уникальных вопросов и анализа ответов студента в реальном времени.

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)

---

## ✨ Основные функции

* **Smart AI Generation**: Автоматический подбор рабочей модели ИИ (v1/v1beta).
* **Динамические тесты**: Генерация по предметам (Математика, Программирование, Английский) и уровням сложности.
* **AI Mentor**: Персонализированная обратная связь после прохождения теста.
* **Live Analytics**: Панель статистики преподавателя с расчетом среднего балла.
* **Glassmorphism UI**: Современный футуристичный интерфейс на Tailwind CSS.

---

## 🚀 Быстрый запуск

### 1. Подготовка API Ключа
Получите бесплатный ключ в [Google AI Studio](https://aistudio.google.com/). 

> **Важно:** Никогда не выкладывайте свой API ключ в публичный доступ на GitHub!

### 2. Установка зависимостей
Убедитесь, что у вас установлен Python 3.9+.
```bash
pip install fastapi uvicorn httpx jinja2

Технический стек
Backend: FastAPI (Python) — асинхронная обработка запросов.

Frontend: HTML5, Tailwind CSS, Vanilla JavaScript.

AI Engine: Google Gemini API (модели семейства Flash).

Communication: HTTPX для асинхронных запросов к Google Cloud.