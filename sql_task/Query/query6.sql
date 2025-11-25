-- Вывести города с количеством активных и неактивных клиентов
-- (active - customer.active = 1). Сортировать по количеству неактивных клиентов в порядке убывания.

SELECT 
  city.city, 
  COUNT(CASE WHEN customer.active = 1 THEN 1 END) AS active_clients,
  COUNT(CASE WHEN customer.active = 0 THEN 1 END) AS inactive_clients
FROM city JOIN (address JOIN customer ON address.address_id = customer.address_id) 
  ON city.city_id = address.city_id
GROUP BY city.city
ORDER BY inactive_clients DESC