## Prompts used to build the web app

You are a senior python developer who writes clean, well-commented code.
Note: Below are the tables, respective column and data types  I created in superbase. We will  be using them along.

users table: listings, payments, waiting_list.

Follow my prompt.
Let's start!
Using HTML, CSS  and Flask framework build  a  modern and mobile responsive dashboard  where a farmer list their items.


### Header Prompt s
First create a header  with space for a logo and 'Food Bridge' as name. Add space for the logged in  user name to appear (e.g., "Welcome, [Supplier Name]!"). 
Add logged out bouton. 

### Farmer Dashboard prompts

secondly, in the main dashboard  create two section: 
"Create a New Listing" and "My Current Listings." section . 
Add a simple buttons to switch between the two sections.


#### `Create a New Listing Section PROMTS`

Thirdly,
In the "Create a New Listing" section,  build a form that allows the supplier to add a new item to the database. It should be designed to minimize effort.
The form must have the following fields: 'Item Name' and 'Quantity'. 
Add  a toggle  to indicate if the item is "Available Now" or "Coming Soon." This toggle links directly to the `is_available` column in your `listings` table.


### BUYER DASHBOARD PROMPTS

Nice job! The earlier output came nicely.

Next
Add a 'price' field  with a **dropdown menu** for the currencies  code (e.g.,  "USD", "EUR", "CAD", "GHS") next to it to the 'Create New listings' form.
I have added a 'price' (data type is numeric) and 'currency'(data type is Text) column in the listings table.

On the 'My listed Items' display the the price beside each listed items.

From this line let's focus on the buyer dashboard ONLY!
The buyer dashboard's primary function is to help users find what they need. The interface should be clean and easy to navigate

Build a prominent search bar at the in the main dashboard. This allows a user to type in a specific food item (e.g., "tomatoes," "cabbage") and filter the listings.

Add to the main dashboard, a dynamic list (with option to change the view into grid) of all available food items posted by the farmer. 
Each item in the list will pull data directly from the **`listings tables`** table in Supabase, showing only those items where `is_available` is set to `TRUE`.

 Each listing should display 'the item name', 'quantity', and the 'farmer's name' and 'price'.

Add a clear 'Place an Order' button. Clicking this button will initiate the order process and payment.
Will integrate payment gateway such as  'Paystack'