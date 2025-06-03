# 🧠 Mentor Connect

> A smart and intuitive mentorship platform built with **Flask**, **Socket.IO**, and **SQLite**, designed to connect mentees with mentors based on skills, availability, and interests.

[![Website](https://img.shields.io/badge/Visit%20Live%20Site-blue?style=for-the-badge&logo=google-chrome)](https://harshitnagar.epizy.com)
[![License](https://img.shields.io/github/license/harshitnagarjaora/Mentor-Connect?style=for-the-badge)](./LICENSE)
[![Stars](https://img.shields.io/github/stars/harshitnagarjaora/Mentor-Connect?style=for-the-badge)](https://github.com/harshitnagarjaora/Mentor-Connect/stargazers)
[![Issues](https://img.shields.io/github/issues/harshitnagarjaora/Mentor-Connect?style=for-the-badge)](https://github.com/harshitnagarjaora/Mentor-Connect/issues)

---

## 🚀 Features

- 🧑‍🏫 **Mentor Matching**: Intelligent matching of mentees to mentors based on keywords and expertise.
- 📅 **Scheduling**: Request-based session booking with mentor approval (accept, reject, or reschedule).
- 🔴 **Live Chat & Video Call**: Real-time messaging and embedded video conferencing using Jitsi/Daily.co.
- 📥 **Resource Sharing**: Share text, links, and files during live sessions.
- 📨 **Email Notifications**: Auto-email triggers for meeting confirmations and status updates.
- 🗃️ **Role-Based Access**: Separate dashboards and permissions for mentors and mentees.
- 🔐 **Authentication**: Secure login system using Flask-Login.

---

## 📁 Project Structure

Mentor-Connect/
│
├── static/ # CSS, JS, images
├── templates/ # HTML templates (dashboard, chat, admin)
├── app.py # Main Flask application
├── models.py # Database models
├── database.db # SQLite DB
├── utils/ # Helper functions
└── README.md # Project documentation

---

## 🛠️ Tech Stack

| Category       | Tech Used                                       |
|----------------|-------------------------------------------------|
| Backend        | Flask, Flask-SocketIO, SQLite                   |
| Frontend       | HTML, CSS, JavaScript                           |
| Real-time Comm | Socket.IO, Jitsi / Daily.co                     |
| Authentication | Flask-Login                                     |
| Scheduling     | Python datetime, Flask Mail                     |
| Deployment     | Render / Heroku / Localhost                     |

---

## 📸 Screenshots

| Mentee Dashboard | Chat Interface | Mentor Request View |
|------------------|----------------|----------------------|
| ![mentee](https://dummyimage.com/300x200/ccc/000&text=Mentee+Dashboard) | ![chat](https://dummyimage.com/300x200/ccc/000&text=Chat+UI) | ![mentor](https://dummyimage.com/300x200/ccc/000&text=Mentor+Request+Page) |

_(Replace with real screenshots)_

---

## 🧑‍💻 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/harshitnagarjaora/Mentor-Connect.git
cd Mentor-Connect
