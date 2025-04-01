# Simple Social Network

A simple social network application built using Django and JavaScript. This project demonstrates the capabilities of Django for backend development and JavaScript for interactive frontend features.

## Features
- User authentication (sign up, login, logout)
- Post creation and commenting
- Friend requests and user interaction
- Real-time notifications using JavaScript

## Technologies Used
- **Django**: Backend framework
- **JavaScript**: Frontend interactions
- **HTML/CSS**: Structure and styling
- **SQLite**: Default database

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/nazmul-islam00/social-network.git
   ```
2. Navigate to the project directory:
   ```bash
   cd social-network
   ```
3. Create a virtual environment and activate it:
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run migrations to set up the database:
   ```bash
   python manage.py migrate
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```
7. Visit the application at ``http://127.0.0.1:8000/``

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push them to your forked repository.
4. Create a pull request for review.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
