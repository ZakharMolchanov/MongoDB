db = db.getSiblingDB("mongo_train");

// Очищаем коллекции
db.orders.drop();
db.assignment_1_data.drop();
db.assignment_2_data.drop();

// Данные для теста №1
db.orders.insertMany([
  { _id: "1", status: "A", amount: 100 },
  { _id: "2", status: "B", amount: 200 },
  { _id: "3", status: "A", amount: 300 }
]);

// Дополнительные данные
db.assignment_1_data.insertMany([
  { _id: "a1-1", name: "Alice",   age: 25, city: "London" },
  { _id: "a1-2", name: "Bob",     age: 30, city: "Paris"  },
  { _id: "a1-3", name: "Charlie", age: 35, city: "Berlin" }
]);

db.assignment_2_data.insertMany([
  { _id: "a2-1", product: "Laptop",   price: 1200, in_stock: true  },
  { _id: "a2-2", product: "Mouse",    price: 25,   in_stock: true  },
  { _id: "a2-3", product: "Keyboard", price: 45,   in_stock: false }
]);

print("orders count:", db.orders.countDocuments({}));
print("assignment_1_data count:", db.assignment_1_data.countDocuments({}));
print("assignment_2_data count:", db.assignment_2_data.countDocuments({}));
