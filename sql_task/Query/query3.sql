-- 3 Выведите категорию фильмов, на которые было потрачено больше всего денег.

SELECT category.name AS category_name, SUM(payment.amount) AS total_spent
FROM payment JOIN 
  (rental JOIN
    (inventory JOIN 
	  (film_category JOIN category ON film_category.category_id = category.category_id) 
	ON inventory.film_id = film_category.film_id) 
  ON rental.inventory_id = inventory.inventory_id) 
ON payment.rental_id = rental.rental_id
GROUP BY category.name
ORDER BY total_spent DESC
LIMIT 1