-- 1 Выведите количество фильмов в каждой категории, отсортированное по убыванию.

SELECT name AS category_name, COUNT(film_category.film_id) AS film_count
  FROM category JOIN film_category ON category.category_id = film_category.category_id
  GROUP BY category.name
  ORDER BY film_count DESC