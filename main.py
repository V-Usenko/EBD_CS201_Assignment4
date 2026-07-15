import csv
import json

def clean_number(value, number_type=float):
    if value is None:
        return number_type(0)
    value = str(value).strip()
    if value == "" or value.upper() == "N/A":
        return number_type(0)
    return number_type(value)

sales = []
with open("global_sales.csv", "r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)

    for row in reader:
        row["quantity"] = clean_number(row["quantity"], int)
        row["revenue"] = clean_number(row["revenue"], float)
        sales.append(row)

with open("regional_tariffs.json", "r", encoding="utf-8") as json_file:
    tariffs = json.load(json_file)

for region, tariff in tariffs.items():
    tariffs[region] = clean_number(tariff, float)


for transaction in sales:
    region = transaction["region"]
    revenue = transaction["revenue"]

    tariff = tariffs.get(region, 0)
    net_profit = revenue - (revenue * (tariff / 100))
    transaction["net_profit"] = round(net_profit, 2)

if sales:
    column_names = list(sales[0].keys())

    with open("cleaned_sales_updated.csv", "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=column_names)
        writer.writeheader()
        writer.writerows(sales)


category_profits = {}

for transaction in sales:
    category = transaction["product_category"]
    net_profit = transaction["net_profit"]

    if category not in category_profits:
        category_profits[category] = 0

    category_profits[category] += net_profit

if category_profits:
    average_profit = sum(category_profits.values()) / len(category_profits)
else:
    average_profit = 0



filtered_categories = filter(lambda item: item[1] > average_profit, category_profits.items())
sorted_categories = sorted(filtered_categories, key=lambda item: item[1], reverse=True)
top_categories = {category: round(profit, 2) for category, profit in sorted_categories}
with open("top_categories.json", "w", encoding="utf-8") as json_file:
    json.dump(top_categories, json_file, ensure_ascii=False, indent=4)
