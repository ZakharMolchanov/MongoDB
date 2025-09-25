import React from "react";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <div className="kicker">Интерактивная практика MongoDB</div>
            <h1>Пиши запросы, запускай их в реальной Mongo и получай обратную связь</h1>
            <p className="lead">
              Выбирай задание, отправляй код в формате Mongo Shell, а тренажёр выполнит его в песочнице,
              сравнит с эталоном и покажет результат. История попыток, тесты и тайминги — всё в одном месте.
            </p>

            <div style={{ display: "flex", gap: 10, marginTop: 16, flexWrap: "wrap" }}>
              <Link to="/register" className="btn primary">Начать бесплатно</Link>
              <Link to="/login" className="btn">У меня уже есть аккаунт</Link>
            </div>

            <div className="hero-card" style={{ marginTop: 18 }}>
              <div style={{ fontWeight: 700, marginBottom: 8 }}>Пример решения</div>
              <div className="kbd">
                {`db.orders
  .find({ status: 'A' })
  .sort({_id: 1});`}
              </div>
              <div style={{ marginTop: 10, color: "var(--muted)" }}>
                Поддерживаются <b>find</b> и <b>aggregate</b> (+ sort/limit). Ошибки возвращаются прямо от MongoDB — учись на реальных ответах.
              </div>
            </div>
          </div>

          <div className="hero-card">
            <div style={{ fontWeight: 700, marginBottom: 6 }}>Как это работает</div>
            <ol style={{ margin: 0, paddingLeft: 18, color: "var(--muted)", lineHeight: 1.6 }}>
              <li>Выбираешь тему и задание</li>
              <li>Пишешь команду в стиле <i>mongo shell</i></li>
              <li>Мы запускаем её в изолированной MongoDB</li>
              <li>Сравниваем результат с эталоном из Postgres</li>
              <li>Показываем проход тестов и сохраняем попытку</li>
            </ol>
            <div style={{ marginTop: 14 }}>
              <Link to="/topics" className="btn">Список тем</Link>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container grid-3">
          <div className="card">
            <h3>Безопасно</h3>
            <p>Белый список операций, таймауты и сэндбокс. Никаких модификаций коллекций.</p>
          </div>
          <div className="card">
            <h3>Похоже на боевую</h3>
            <p>Ошибки приходят прямо из MongoDB. Осваиваешь реальные сообщения и практику.</p>
          </div>
          <div className="card">
            <h3>История и метрики</h3>
            <p>Храним все попытки: текст запроса, время выполнения, размер результата и статус тестов.</p>
          </div>
        </div>
      </section>
    </>
  );
}
