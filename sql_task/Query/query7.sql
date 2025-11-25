-- Выведите категорию фильмов с наибольшим общим количеством часов проката в городе 
-- (customer.address_id в этом городе), начинающихся на букву «a». Сделайте то же самое для городов, 
-- в названиях которых есть «-». Запишите все в один запрос

WITH grouped_data AS (
    SELECT 
        c.name AS category_name,
        CASE 
            WHEN ci.city LIKE 'a%' THEN 'Starts with a'
            WHEN ci.city LIKE '%-%' THEN 'Contains hyphen'
        END AS city_group,
        SUM(f.length) / 60 AS total_hours
    FROM category c
    JOIN film_category fc ON c.category_id = fc.category_id
    JOIN film f           ON fc.film_id = f.film_id
    JOIN inventory i      ON f.film_id = i.film_id
    JOIN rental r         ON i.inventory_id = r.inventory_id
    JOIN customer cu      ON r.customer_id = cu.customer_id
    JOIN address a        ON cu.address_id = a.address_id
    JOIN city ci          ON a.city_id = ci.city_id
    WHERE ci.city LIKE 'a%' 
       OR ci.city LIKE '%-%'
    GROUP BY city_group, category_name
), 
ranked_data AS (
    SELECT 
        city_group, 
        category_name, 
        total_hours, 
        DENSE_RANK() OVER (
            PARTITION BY city_group 
            ORDER BY total_hours DESC
        ) AS rnk
    FROM grouped_data
)
SELECT 
    city_group, 
    category_name, 
    total_hours
FROM ranked_data
WHERE rnk = 1
ORDER BY city_group;