import numpy as np
import pandas as pd

# Define product lines, brands, and hierarchies
product_line_hierarchy = {
    "Apparel": {
        "brands": ["Zara", "H&M"],
        "hierarchies": [
            "Apparel.Men.Shirts.Casual",
            "Apparel.Women.Dresses.Evening",
            "Apparel.Kids.Tops.Activewear",
        ],
    },
    "Footwear": {
        "brands": ["Nike", "Adidas"],
        "hierarchies": [
            "Footwear.Men.Sneakers.Sport",
            "Footwear.Women.Boots.Winter",
            "Footwear.Kids.Sandals.Casual",
        ],
    },
    "Accessories": {
        "brands": ["Ray-Ban", "Michael Kors"],
        "hierarchies": [
            "Accessories.Watches.Men.Luxury",
            "Accessories.Handbags.Women.Designer",
            "Accessories.Sunglasses.Unisex.Polarized",
        ],
    },
    "Beauty & Personal Care": {
        "brands": ["Dove", "Nivea"],
        "hierarchies": [
            "Beauty.Skincare.Moisturizers.Hydrating",
            "Beauty.Haircare.Shampoo.Volumizing",
            "PersonalCare.BodyWash.Fragranced",
        ],
    },
}

# Create product code mapping
product_code_mapping = {}
product_code_counter = 1
for category, details in product_line_hierarchy.items():
    for brand in details["brands"]:
        for hierarchy in details["hierarchies"]:
            product_code_mapping[(brand, hierarchy)] = f"P-{product_code_counter:04}"
            product_code_counter += 1

# Define sales channels
sales_channels_realistic = [
    "RetailOutlet:Mall Store",
    "RetailOutlet:Outlet Store",
    "OnlineStore:Website",
    "OnlineStore:Mobile App",
    "B2BCustomers:Corporate Client",
    "B2BCustomers:Reseller",
]

# Define promo codes
promo_codes = [
    "FREE10",
    "PARTY10",
    "WELCOMEBACK15",
    "WELCOMEBACK20",
    "NO_CODE",
    "THANKYOU20",
]

# Define price ranges and unit cost ratios by category
price_ranges = {
    "Apparel": (10, 150),
    "Footwear": (20, 200),
    "Accessories": (50, 500),
    "Beauty & Personal Care": (5, 50),
}
unit_cost_ratios = {
    "Apparel": (0.2, 0.3),
    "Footwear": (0.25, 0.35),
    "Accessories": (0.5, 0.6),
    "Beauty & Personal Care": (0.15, 0.25),
}

# Define quantity lambdas for Poisson distribution
quantity_lambdas = {
    "Apparel": 1.5,
    "Footwear": 1.2,
    "Accessories": 1.0,
    "Beauty & Personal Care": 2.5,
}

# Define product weights for fulfillment cost
product_weights = {
    "Apparel": lambda: np.random.uniform(0.5, 2.0),
    "Footwear": lambda: np.random.uniform(1.0, 3.0),
    "Accessories": lambda: np.random.uniform(0.2, 1.0),
    "Beauty & Personal Care": lambda: np.random.uniform(0.1, 0.5),
}

# Define return rates by category
return_rates = {
    "Apparel": 0.08,
    "Footwear": 0.06,
    "Accessories": 0.03,
    "Beauty & Personal Care": 0.05,
}

# Define location mappings
country_state_city = {
    "USA": {
        "states": ["NY", "CA", "TX"],
        "cities": ["NYC", "San Francisco", "Pasadena"],
    },
    "France": {"states": ["None"], "cities": ["Paris", "Reims"]},
    "Germany": {"states": ["None"], "cities": ["Berlin"]},
    "UK": {"states": ["None"], "cities": ["London"]},
    "Italy": {"states": ["None"], "cities": ["Milan"]},
}

# Define shipping parameters
shipping_threshold = 100.0
shipping_fee_per_unit = 3.0


def calculate_discount(sales, promo_code, category, sales_channel, customer_loyalty):
    """
    Calculate discount based on promo code, adjusted by category, channel, and loyalty.
    Ensures discount doesn't exceed sales.
    """
    base_discount = {
        "FREE10": 0.10,
        "PARTY10": 0.10,
        "WELCOMEBACK15": 0.15,
        "WELCOMEBACK20": 0.20,
        "THANKYOU20": 0.20,
        "NO_CODE": 0.0,
    }
    channel_multipliers = {
        "B2BCustomers:Corporate Client": 1.2,
        "OnlineStore:Mobile App": 0.9,
    }
    category_multipliers = {"Accessories": 0.8, "Beauty & Personal Care": 1.1}
    loyalty_multipliers = {"New": 1.2, "Loyal": 0.8}
    discount_rate = (
        base_discount[promo_code]
        * channel_multipliers.get(sales_channel, 1.0)
        * category_multipliers.get(category, 1.0)
        * loyalty_multipliers.get(customer_loyalty, 1.0)
    )
    return round(min(sales * discount_rate, sales), 2)


def calculate_fulfillment_cost(quantity, sales_channel, territory, product_weight):
    """
    Calculate fulfillment cost based on quantity, channel, territory, and weight.
    """
    channel_factors = {"OnlineStore:Mobile App": 1.2, "RetailOutlet:Mall Store": 0.8}
    territory_factors = {"NA": 1.0, "EMEA": 1.1, "APAC": 1.3}
    per_unit_cost = 2.0
    fixed_cost = 5.0
    weight_factor = max(1.0, product_weight / 5)
    return round(
        (per_unit_cost * quantity + fixed_cost)
        * channel_factors.get(sales_channel, 1.0)
        * territory_factors[territory]
        * weight_factor,
        2,
    )


def generate_fashion_data_with_brand(start_date, end_date):
    """
    Generate realistic retail transactional data based on the flowchart relationships.
    """
    # Define category mapping to handle 'Beauty' -> 'Beauty & Personal Care'
    category_mapping = {
        "Beauty": "Beauty & Personal Care",
        "Apparel": "Apparel",
        "Footwear": "Footwear",
        "Accessories": "Accessories",
        "PersonalCare": "Beauty & Personal Care",  # Handle 'PersonalCare' if needed
    }

    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    records = []
    for date in date_range:
        day_of_week = date.dayofweek
        base_demand = 10 if day_of_week in [4, 5] else 8
        for (brand, hierarchy), product_code in product_code_mapping.items():
            num_orders = base_demand
            for _ in range(num_orders):
                # Extract category from hierarchy and map it correctly
                category = hierarchy.split(".")[0]
                mapped_category = category_mapping.get(
                    category, category
                )  # Default to category if not mapped
                price_range = price_ranges[mapped_category]
                price = round(
                    np.random.lognormal(
                        mean=np.log((price_range[0] + price_range[1]) / 2), sigma=0.5
                    ),
                    2,
                )
                price = max(price_range[0], min(price, price_range[1]))
                unit_cost_ratio = np.random.uniform(*unit_cost_ratios[mapped_category])
                unit_cost = round(price * unit_cost_ratio, 2)
                quantity = max(1, np.random.poisson(quantity_lambdas[mapped_category]))
                sales = round(price * quantity, 2)
                sales_channel = np.random.choice(sales_channels_realistic)
                promo_code = np.random.choice(promo_codes)
                customer_loyalty = np.random.choice(["New", "Loyal"], p=[0.6, 0.4])
                discount = calculate_discount(
                    sales, promo_code, mapped_category, sales_channel, customer_loyalty
                )
                net_sales = max(round(sales - discount, 2), 0)
                country = np.random.choice(list(country_state_city.keys()))
                state = np.random.choice(country_state_city[country]["states"])
                city = np.random.choice(country_state_city[country]["cities"])
                territory = "NA" if country == "USA" else "EMEA"
                product_weight = product_weights[mapped_category]()
                fulfillment_cost = calculate_fulfillment_cost(
                    quantity, sales_channel, territory, product_weight
                )
                marketing_cost = round(
                    np.random.uniform(1, 5)
                    * (1.5 if mapped_category == "Beauty & Personal Care" else 1.0),
                    2,
                )
                return_cost = round(net_sales * return_rates[mapped_category], 2)
                cost_of_goods_sold = round(unit_cost * quantity, 2)
                shipping_revenue = (
                    0.0
                    if sales >= shipping_threshold
                    else round(shipping_fee_per_unit * quantity, 2)
                )
                profit = round(
                    net_sales
                    - fulfillment_cost
                    - marketing_cost
                    - return_cost
                    - cost_of_goods_sold
                    + shipping_revenue,
                    2,
                )
                profit_margin = (
                    round((profit / net_sales) * 100, 2) if net_sales > 0 else 0
                )
                is_margin_negative = profit < 0
                if profit_margin < -100:
                    profit = -net_sales
                    profit_margin = -100
                order_number = np.random.randint(10000, 99999)
                status = np.random.choice(
                    ["Shipped", "In Process", "Cancelled"], p=[0.7, 0.2, 0.1]
                )
                qtr_id = (date.month - 1) // 3 + 1
                month_id = date.month
                year_id = date.year
                postal_code = np.random.randint(10000, 99999)
                last_name = np.random.choice(["Smith", "Doe", "Brown", "Lee"])
                first_name = np.random.choice(["John", "Jane", "Emily", "Chris"])
                address_line1 = np.random.choice(
                    ["123 Main St", "456 Elm St", "789 Maple Ave"]
                )
                deal_size = np.random.choice(["Small", "Medium", "Large"])
                records.append(
                    {
                        "ORDERNUMBER": order_number,
                        "QUANTITYORDERED": quantity,
                        "PRICEEACH": price,
                        "UNIT_COST": unit_cost,
                        "ORDERDATE": date,
                        "SALES": sales,
                        "DISCOUNT": discount,
                        "NET_SALES": net_sales,
                        "STATUS": status,
                        "QTR_ID": qtr_id,
                        "MONTH_ID": month_id,
                        "YEAR_ID": year_id,
                        "CITY": city,
                        "COUNTRY": country,
                        "ADDRESSLINE1": address_line1,
                        "ADDRESSLINE2": None,
                        "STATE": state,
                        "POSTALCODE": postal_code,
                        "TERRITORY": territory,
                        "CONTACTLASTNAME": last_name,
                        "CONTACTFIRSTNAME": first_name,
                        "DEALSIZE": deal_size,
                        "PRODUCTCODE": product_code,
                        "BRAND": brand,
                        "MERCHANDISE_HIERARCHY": hierarchy,
                        "SALES_CHANNEL": sales_channel,
                        "PROMO_CODE": promo_code,
                        "FULFILLMENT_COST": fulfillment_cost,
                        "MARKETING_COST": marketing_cost,
                        "RETURN_COST": return_cost,
                        "COST_OF_GOODS_SOLD": cost_of_goods_sold,
                        "SHIPPING_REVENUE": shipping_revenue,
                        "PROFIT": profit,
                        "PROFIT_MARGIN": profit_margin,
                        "IS_MARGIN_NEGATIVE": is_margin_negative,
                        "CUSTOMER_LOYALTY": customer_loyalty,
                    }
                )
    return pd.DataFrame(records)


def inject_anomalies_by_date(df, anomaly_schedule):
    """
    Inject anomalies into the data with specific scopes and recalculate all downstream metrics,
    ensuring clear pathways for anomaly detection and root cause analysis.
    """
    df = df.copy()
    df["ANOMALY_TYPE"] = None
    df["SEVERITY"] = None
    df["ROOT_CAUSE"] = None

    for date_str, (
        anomaly_type,
        severity,
        root_cause,
        scope,
    ) in anomaly_schedule.items():
        date_mask = df["ORDERDATE"] == pd.to_datetime(date_str)
        if scope in sales_channels_realistic:
            mask = date_mask & (df["SALES_CHANNEL"] == scope)
        else:
            mask = date_mask & df["MERCHANDISE_HIERARCHY"].str.startswith(scope)

        if not df[mask].empty:
            df.loc[mask, "ANOMALY_TYPE"] = anomaly_type
            df.loc[mask, "SEVERITY"] = severity
            df.loc[mask, "ROOT_CAUSE"] = root_cause

            if anomaly_type == "ExcessiveDiscount":
                new_discount = (df.loc[mask, "SALES"] * severity).round(2)
                df.loc[mask, "DISCOUNT"] = np.minimum(
                    new_discount, df.loc[mask, "SALES"]
                )
                df.loc[mask, "NET_SALES"] = (
                    df.loc[mask, "SALES"] - df.loc[mask, "DISCOUNT"]
                ).round(2)
                category = (
                    scope
                    if scope in price_ranges
                    else df.loc[mask, "MERCHANDISE_HIERARCHY"]
                    .str.split(".")
                    .str[0]
                    .iloc[0]
                )
                df.loc[mask, "RETURN_COST"] = (
                    df.loc[mask, "NET_SALES"] * return_rates[category]
                ).round(2)

            elif anomaly_type == "COGSOverstatement":
                df.loc[mask, "UNIT_COST"] = (
                    df.loc[mask, "UNIT_COST"] * (1 + severity)
                ).round(2)
                df.loc[mask, "COST_OF_GOODS_SOLD"] = (
                    df.loc[mask, "UNIT_COST"] * df.loc[mask, "QUANTITYORDERED"]
                ).round(2)

            elif anomaly_type == "FulfillmentSpike":
                df.loc[mask, "FULFILLMENT_COST"] = (
                    df.loc[mask, "FULFILLMENT_COST"] * (1 + severity)
                ).round(2)

            elif anomaly_type == "ShippingDisruption":
                df.loc[mask, "SHIPPING_REVENUE"] = (
                    -df.loc[mask, "SHIPPING_REVENUE"] * severity
                ).round(2)

            elif anomaly_type == "ReturnSurge":
                df.loc[mask, "RETURN_COST"] = (
                    df.loc[mask, "RETURN_COST"] * (1 + severity)
                ).round(2)

            # Recalculate PROFIT and PROFIT_MARGIN for all affected rows
            df.loc[mask, "PROFIT"] = (
                df.loc[mask, "NET_SALES"]
                - df.loc[mask, "FULFILLMENT_COST"]
                - df.loc[mask, "MARKETING_COST"]
                - df.loc[mask, "RETURN_COST"]
                - df.loc[mask, "COST_OF_GOODS_SOLD"]
                + df.loc[mask, "SHIPPING_REVENUE"]
            ).round(2)
            df.loc[mask, "PROFIT_MARGIN"] = np.where(
                df.loc[mask, "NET_SALES"] > 0,
                (df.loc[mask, "PROFIT"] / df.loc[mask, "NET_SALES"] * 100).round(2),
                0,
            )
            df.loc[mask, "IS_MARGIN_NEGATIVE"] = df.loc[mask, "PROFIT"] < 0

    return df
