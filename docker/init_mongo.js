// Use the same DB name as configured in docker-compose MONGO_URI
db = db.getSiblingDB("mongo_train");

db.orders.insertMany([
  { _id: 1, status: "A", amount: 100 },
  { _id: 2, status: "B", amount: 200 },
  { _id: 3, status: "A", amount: 300 }
]);

db.users.insertMany([
  { _id: 1, name: "Alice", age: 25, city: "Moscow" },
  { _id: 2, name: "Bob", age: 35, city: "Kazan" },
  { _id: 3, name: "Charlie", age: 40, city: "SPB" }
]);

db.products.insertMany([
  { _id: 1, product: "Phone", price: 1000 },
  { _id: 2, product: "TV", price: 2000 },
  { _id: 3, product: "Laptop", price: 3000 }
]);
