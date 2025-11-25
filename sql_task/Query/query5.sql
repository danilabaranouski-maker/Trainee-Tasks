-- Выведите тройку актёров, которые чаще всего снимались в фильмах категории «Дети». 
-- Если у нескольких актёров одинаковое количество фильмов, выведите их всех.

WITH RankedActors AS (
  SELECT actor.first_name, 
         actor.last_name, 
         COUNT(film_actor.film_id) AS film_count,
         DENSE_RANK() OVER (ORDER BY COUNT(film_actor.film_id) DESC) AS rnk
    FROM actor JOIN film_actor ON actor.actor_id = film_actor.actor_id
               JOIN film_category ON film_actor.film_id = film_category.film_id
               JOIN category ON film_category.category_id = category.category_id
    WHERE category.name = 'Children'
    GROUP BY actor.actor_id, actor.first_name, actor.last_name
)
SELECT first_name, last_name, film_count
  FROM RankedActors 
  WHERE rnk <= 3
  ORDER BY film_count DESC, first_name;