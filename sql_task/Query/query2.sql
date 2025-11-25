-- 2 Выведите 10 актеров, фильмы которых были в прокате чаще всего, отсортированных по убыванию.

SELECT actor.first_name AS actor_first_name, actor.last_name AS actor_last_name, COUNT(rental.rental_id) AS rental_count
FROM actor JOIN (film_actor JOIN (inventory JOIN
    rental ON inventory.inventory_id = rental.inventory_id) ON film_actor.film_id = inventory.film_id)
     ON actor.actor_id = film_actor.actor_id
GROUP BY actor.actor_id, actor.first_name, actor.last_name
ORDER BY rental_count DESC
LIMIT 10