
db = db.getSiblingDB("mongo_train");

// Идемпотентно очищаем
db.users.drop();
db.orders.drop();
db.products.drop();

// users
db.users.insertMany([
  { _id: "u1", name: "Alice",   age: 25, city: "London" },
  { _id: "u2", name: "Bob",     age: 30, city: "Paris"  },
  { _id: "u3", name: "Charlie", age: 35, city: "Berlin" },
  { _id: "u4", name: "Diana",   age: 40, city: "London" }
]);

// orders (оставляем как раньше для совместимости с тестом №1)
db.orders.insertMany([
  { _id: "1", status: "A", amount: 100 },
  { _id: "2", status: "B", amount: 200 },
  { _id: "3", status: "A", amount: 300 }
]);

// products
db.products.insertMany([
  { _id: "p1", product: "Laptop",   price: 1200, category: "Electronics", in_stock: true  },
  { _id: "p2", product: "Mouse",    price: 25,   category: "Accessories", in_stock: true  },
  { _id: "p3", product: "Keyboard", price: 45,   category: "Accessories", in_stock: false },
  { _id: "p4", product: "Monitor",  price: 300,  category: "Electronics", in_stock: true  }
]);

// индексы (необязательно)
db.users.createIndex({ city: 1 });
db.orders.createIndex({ status: 1 });
db.products.createIndex({ category: 1 });
db.products.createIndex({ price: -1 });

// echo counts
print("users:", db.users.countDocuments({}));
print("orders:", db.orders.countDocuments({}));
print("products:", db.products.countDocuments({}));
