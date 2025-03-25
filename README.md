# All-in-One Ticket Booking System

The All-in-One Ticket Booking System is a comprehensive web application that allows users to book tickets for flights, trains, and buses. It provides an easy-to-use interface for customers and a management system for admins to create and manage trips.

## Features

- **User-friendly Interface**: A clean and intuitive design for customers to easily book tickets for various modes of transportation.

- **Trip Management**: Admins can create, update, and delete trips for buses, trains, and flights through the administration panel.

- **Email Notifications**: Users receive email notifications upon successful ticket bookings, providing details of their reservation.

## Technologies Used

- **Python**: Backend logic and server-side scripting.
- **Django**: High-level Python web framework for building web applications.

- **HTML, CSS, Bootstrap**: Frontend technologies for creating responsive and visually appealing user interfaces.

- **jQuery**: JavaScript library for simplified DOM manipulation and AJAX.

- **Poetry**: Dependency manager for Python projects.

## Project Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Rajeshkumar-14/ticket-booking-system.git
   ```

2. **Create and Activate Conda Environment:**

   - Create a new Conda environment:

     ```bash
     conda create --name ticket-booking-system python=3.13
     ```

   - Activate the Conda environment:

     ```bash
     conda activate ticket-booking-system
     ```

3. **Create .env file:**

   - Create a `.env` file in the main directory for mail sending purpose using [mailtrap.io](https://mailtrap.io/).

     ```env
     EMAIL_HOST='sandbox.smtp.mailtrap.io'
     EMAIL_PORT='2525'
     EMAIL_HOST_USER='your_username'
     EMAIL_HOST_PASSWORD='your_password'
     ```

   - Remove spaces between the variable and equals and the value to avoid errors while copying from the website.
   - Refer the `.env.example` file.

4. **Create media/proof folder:**

   - Create a `media/proof` directory in the main directory for storing the media files.

     ```
     /ticket-booking-system (BASE DIRECTORY | FOLDER)
     ├── ticket_system_project
     ├── media
     │   └── proof/
     ├── manage.py
     ```

   - Make sure to create this directory structure to avoid errors.

5. **Install Dependencies:**

   - Install Poetry:

     ```bash
     pip install poetry
     ```

   - Run this command after installing Poetry:

     ```bash
     poetry install
     ```

6. **Database Setup:**

   - Run these commands to migrate models:

     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```

   - If the above commands don't work, try:

     ```bash
     python manage.py makemigrations authentication
     python manage.py makemigrations core
     python manage.py makemigrations bus
     python manage.py makemigrations flight
     python manage.py makemigrations train
     python manage.py makemigrations support
     python manage.py migrate
     ```

7. **Create Superuser:**

   ```bash
   python manage.py createsuperuser
   ```

8. **Run Server:**

  ```bash
  python manage.py runserver
  ```

## Usage

### Admin Panel:

- Visit the admin panel at [http://localhost:8000/admin/](http://localhost:8000/admin/) and log in with your superuser credentials.

- Create groups with the exact names **Administration** and **User** and assign appropriate **Permissions**.

- In the Admin panel, add a user to the Administration group to access the Administration Interface.

⚠️ **Note:** Before registering users, ensure that you have created the necessary groups.

### Administration Interface:

- Visit the admin panel at [http://localhost:8000/administration/](http://localhost:8000/administration/) and log in with your superuser credentials.

- Create, update, and delete trips for buses, trains, and flights.

### User Interface:

Users can access the booking system at [http://localhost:8000/](http://localhost:8000/) to:

- Select a mode of transportation.
- Browse available trips.
- Reserve tickets with confirmation details.
- Receive email notifications for successful bookings.
- Payment options will be added in the upcoming commits.

## Contributing

- Contributions are welcome! If you have any suggestions, bug reports, or feature requests, feel free to open an issue or submit a pull request.
