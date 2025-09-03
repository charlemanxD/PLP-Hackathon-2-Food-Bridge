# PLP-Hackathon-2-Food-Bridge

Bridging Food Suppliers and Communities 
This project is a marketplace platform that connects food suppliers (like farms and local markets) with charities, individuals, and communities in need, ensuring excess produce finds its way to those who need it most. Our goal is to reduce food insecurity, food waste, and build a more sustainable local food ecosystem.

<img width="1416" height="984" alt="# PLP-Hackathon-2-Food-Bridge - visual selection" src="https://github.com/user-attachments/assets/065e230e-ff5c-4783-837e-3f26f5733174" />

🚀 The Tech Stack
We've built this application using a modern, scalable, and high-performance tech stack. This app was "vibe-coded" on Replit, a collaborative and fast-paced development environment.

- Frontend: HTML, CSS, JavaScript

- Backend: Python(Flask)

- Database: Supabase

- Payment gateway: Paystack


## User Interface (UI) 🚀

- **Authentication Pages:** a simple sign-up and login pages. 
    
- **Supplier Dashboard:** The  interface for farmers and producers. It's divided into two sections. Section one consists of a form that allows them to create a new listing easily. 
    
- **Buyer Dashboard:** This is the main page for NGOs, charities, and individuals. It features a prominent search bar and a list of all currently available items from the farmers/producers.
-
- **Payments:** Next to each item, the "Place an Order"  button helps  the buyer  proceed with paying for the desired item. Once a buyer places an order, they will be directed  to the Paystack payment gateway.


### Login interface

<img width="1669" height="790" alt="Screenshot 2025-09-02 075628" src="https://github.com/user-attachments/assets/bf098161-c763-47a9-a7ca-8d84e2c0edfe" />


### Farmer/Producer dashboard

<img width="1182" height="902" alt="Screenshot 2025-09-02 064009" src="https://github.com/user-attachments/assets/d33c9a85-ef35-4995-bea9-1b4b15a3bdd8" />


### NGOs/Individuals dashboard

<img width="1256" height="919" alt="Screenshot 2025-09-02 064140" src="https://github.com/user-attachments/assets/7dfe389a-192d-4625-92c7-21f86cd7f6fe" />


🛠️ Getting Started
To run this project locally, follow these steps:

Clone the repository:
git clone https://github.com/charlemanxD/PLP-Hackathon-2-Food-Bridge.git

Install dependencies:
pip install -r requirements.txt

Set up environment variables:
Create a .env file with your Supabase and Paystack credentials.
SUPABASE_URL
PAYSTACK_SECRET_KEY
PAYSTACK_PRUBLIC_KEY

Run the Flask server:
flask run

Open in your browser:
Navigate to http://127.0.0.1:5000
