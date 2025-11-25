import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import (col, count, desc, sum as _sum, lit, when, lower, dense_rank, unix_timestamp)
from pyspark.sql.window import Window
from tabulate import tabulate
from dotenv import load_dotenv

load_dotenv()

driver_name = os.getenv("SPARK_DRIVER_JAR", "postgresql-42.7.3.jar")

if not os.path.exists(f"jars/{driver_name}"):
    if os.path.exists("jars"):
        files = os.listdir("jars")
        if files: driver_name = files[0]

driver_path = f"jars/{driver_name}"
results_dir = "results"

if not os.path.exists(results_dir):
    os.makedirs(results_dir)

spark = SparkSession.builder \
    .appName("Pagila Full Tasks") \
    .config("spark.jars", driver_path) \
    .config("spark.driver.extraClassPath", driver_path) \
    .getOrCreate()

jdbc_url = os.getenv("DB_URL")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_driver = os.getenv("DB_DRIVER", "org.postgresql.Driver")

if not all([jdbc_url, db_user, db_password]):
    raise EnvironmentError("Не найдены настройки БД в файле .env!")

db_props = {
    "user": db_user,
    "password": db_password,
    "driver": db_driver
}

def load(table):
    return spark.read.jdbc(url=jdbc_url, table=table, properties=db_props)

def save_result(df, filename, header_text):
    path = os.path.join(results_dir, filename)
    
    pdf = df.toPandas()
    
    pretty_table = tabulate(pdf, headers='keys', tablefmt='grid', showindex=False)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{header_text}\n")
        f.write("=" * len(header_text) + "\n\n")
        f.write(pretty_table)
        f.write("\n") 
    print(f"Сохранено: {filename}")

print("загрузка данных")
category = load("category")
film_category = load("film_category")
film = load("film")
actor = load("actor")
film_actor = load("film_actor")
inventory = load("inventory")
rental = load("rental")
payment = load("payment")
customer = load("customer")
address = load("address")
city = load("city")

try:
    print("\n1. Считаем категории")
    res1 = category.join(film_category, "category_id") \
        .groupBy("name") \
        .agg(count("film_id").alias("count")) \
        .orderBy(desc("count"))
    save_result(res1, "1_categories.txt", "Количество фильмов в категориях")

    print("2. Ищем популярных актеров")
    res2 = rental.join(inventory, "inventory_id") \
        .join(film_actor, "film_id") \
        .join(actor, "actor_id") \
        .groupBy("first_name", "last_name") \
        .agg(count("rental_id").alias("rentals")) \
        .orderBy(desc("rentals")) \
        .limit(10)
    save_result(res2, "2_top_actors.txt", "Топ-10 актеров по аренде")

    print("3. Ищем самую прибыльную категорию")
    res3 = payment.join(rental, "rental_id") \
        .join(inventory, "inventory_id") \
        .join(film_category, "film_id") \
        .join(category, "category_id") \
        .groupBy("name") \
        .agg(_sum("amount").alias("total_money")) \
        .orderBy(desc("total_money")) \
        .limit(1)
    save_result(res3, "3_rich_category.txt", "Категория с макс. выручкой")

    print("4. Ищем фильмы которых нет в инвентаре")
    res4 = film.join(inventory, "film_id", "left_anti") \
        .select("title") \
        .orderBy("title")
    save_result(res4, "4_not_in_stock.txt", "Фильмы, которых нет в инвентаре")

    print("5. Ищем детских актеров")
    children_id = category.filter(category.name == "Children").select("category_id")
    actors_counts = film_category.join(children_id, "category_id") \
        .join(film_actor, "film_id") \
        .join(actor, "actor_id") \
        .groupBy("first_name", "last_name") \
        .agg(count("film_id").alias("cnt"))
    
    windowSpec = Window.orderBy(desc("cnt"))
    
    res5 = actors_counts.withColumn("rank", dense_rank().over(windowSpec)) \
        .filter(col("rank") <= 3) \
        .select("first_name", "last_name", "cnt", "rank")
    save_result(res5, "5_children_actors.txt", "Топ-3 актеров в категории 'Children'")

    print("6. Анализируем города")
    res6 = customer.join(address, "address_id") \
        .join(city, "city_id") \
        .groupBy("city") \
        .agg(
            _sum(when(col("active") == 1, 1).otherwise(0)).alias("active"), 
            _sum(when(col("active") == 0, 1).otherwise(0)).alias("inactive")
        ) \
        .orderBy(desc("inactive"))
    save_result(res6, "6_cities_stats.txt", "Статистика клиентов по городам")

    print("7. Считаем часы аренды")
    
    df_rentals = rental.join(inventory, "inventory_id") \
        .join(film_category, "film_id") \
        .join(category, "category_id") \
        .join(customer, "customer_id") \
        .join(address, "address_id") \
        .join(city, "city_id") \
        .withColumn("hours", 
                    (unix_timestamp(col("return_date")) - unix_timestamp(col("rental_date"))) / 3600)

    res7_a = df_rentals.filter(lower(col("city")).startswith("a")) \
        .groupBy("name") \
        .agg(_sum("hours").alias("hours")) \
        .orderBy(desc("hours")) \
        .limit(1)
    
    res7_dash = df_rentals.filter(col("city").contains("-")) \
        .groupBy("name") \
        .agg(_sum("hours").alias("hours")) \
        .orderBy(desc("hours")) \
        .limit(1)

    path7 = os.path.join(results_dir, "7_rental_hours.txt")
    pdf_a = res7_a.toPandas()
    pdf_dash = res7_dash.toPandas()
    
    with open(path7, "w", encoding="utf-8") as f:
        f.write("Категория с макс. часами (Города на 'A')\n")
        f.write(tabulate(pdf_a, headers='keys', tablefmt='grid', showindex=False))
        f.write("\n\n")
        f.write("Категория с макс. часами (Города с '-')\n")
        f.write(tabulate(pdf_dash, headers='keys', tablefmt='grid', showindex=False))
    print("Сохранено: 7_rental_hours.txt")

except Exception as e:
    print(f"\nОШИБКА: {e}")

finally:
    spark.stop()