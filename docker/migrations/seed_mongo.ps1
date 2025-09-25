# Run from project root PowerShell to seed MongoDB collections when the container is already running
Write-Output "Seeding MongoDB (mongo_train) with sample collections..."

# Use mongosh or mongo client available in the container. This will execute JS to insert sample documents
docker-compose exec mongo bash -lc "mongosh --eval \"db = db.getSiblingDB('mongo_train'); if (db.orders.count() == 0) { db.orders.insertMany([{ _id: 1, status: 'A', amount: 100 }, { _id: 2, status: 'B', amount: 200 }, { _id: 3, status: 'A', amount: 300 }]); } if (db.users.count() == 0) { db.users.insertMany([{ _id: 1, name: 'Alice', age: 25, city: 'Moscow' }, { _id: 2, name: 'Bob', age: 35, city: 'Kazan' }, { _id: 3, name: 'Charlie', age: 40, city: 'SPB' }]); } if (db.products.count() == 0) { db.products.insertMany([{ _id: 1, product: 'Phone', price: 1000 }, { _id: 2, product: 'TV', price: 2000 }, { _id: 3, product: 'Laptop', price: 3000 }]); }\""

Write-Output "MongoDB seeding finished."
