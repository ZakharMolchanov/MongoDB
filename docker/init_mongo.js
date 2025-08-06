db = db.getSiblingDB('trainerdb');

db.tasks.insertMany([
  {
    question: "Найди всех пользователей старше 25 лет",
    collection: "users",
    query: { "age": { "$gt": 25 } }
  },
  {
    question: "Найди все книги с жанром 'sci-fi'",
    collection: "books",
    query: { "genre": "sci-fi" }
  }
]);
