## InventoryX API
InventoryX is an inventory management web application backend API.

## User and App End Points
https://api.inventoryx.me/user/
<img src="https://res.cloudinary.com/dkezlmzn1/image/upload/v1679642026/Screenshot_2023-03-24_at_7.52.25_AM_t6k6qg.png"/>

https://api.inventoryx.me/app/
<img src="https://res.cloudinary.com/dkezlmzn1/image/upload/v1679642026/Screenshot_2023-03-24_at_7.52.30_AM_ltofck.png"/>

## Tools
* Django
* Django REST Framework
* Postgres
* Python Decouple
* PyJWT
* Postman
* Psycopg2
* Docker

pip install -r requirements.txt

## Virtual Environment
* python3 -m venv inventoryx_env
* source inventoryx_env/bin/activate


**
USER ROUTES

Method: POST /user/create-user - FUNCTIONALITY - Create user - ACCESS - Superuser
Method: POST /user/login - FUNCTIONALITY - Login user - ACCESS - All users
Method: POST /user/update-password - FUNCTIONALITY - Update user password - ACCESS - All users
Method: POST /user/me -
Method: POST /user/activities-log - FUNCTIONALITY - View users activities log - ACCESS - Superuser
Method: POST /user/users - FUNCTIONALITY - View all users - ACCESS - Superuser
=====
/app/inventory
app/inventory-csv
/app/shop
/app/summary
/app/purchase-summary
/app/sales-by-shop
/app/group
/app/top-selling
/app/invoice