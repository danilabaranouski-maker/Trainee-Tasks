-- Выведите названия фильмов, которых нет в инвентаре. Составьте запрос без оператора IN.

SELECT film.title
FROM film
WHERE
  NOT EXISTS (
    SELECT 1
      FROM inventory
      WHERE inventory.film_id = film.film_id
  )