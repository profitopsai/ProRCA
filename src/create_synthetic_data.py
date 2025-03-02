import numpy as np
import pandas as pd
import networkx as nx

# ------------------------------------------------------------------
# 2) DATA GENERATION: REALISTIC TRANSACTIONAL DATA
# ------------------------------------------------------------------

# For illustration, we generate "fashion-like" sales data, but the core
# financial metrics (PRICEEACH, SALES, DISCOUNT, etc.) follow the DAG above.

# Define product lines, their matching hierarchies, brands, and unique codes
product_line_hierarchy = {
    'Apparel': {
        'brands': ['Zara', 'H&M'],
        'hierarchies': [
            'Apparel.Men.Shirts.Casual',
            'Apparel.Women.Dresses.Evening',
            'Apparel.Kids.Tops.Activewear'
        ]
    },
    'Footwear': {
        'brands': ['Nike', 'Adidas'],
        'hierarchies': [
            'Footwear.Men.Sneakers.Sport',
            'Footwear.Women.Boots.Winter',
            'Footwear.Kids.Sandals.Casual'
        ]
    },
    'Accessories': {
        'brands': ['Ray-Ban', 'Michael Kors'],
        'hierarchies': [
            'Accessories.Watches.Men.Luxury',
            'Accessories.Handbags.Women.Designer',
            'Accessories.Sunglasses.Unisex.Polarized'
        ]
    },
    'Beauty & Personal Care': {
        'brands': ['Dove', 'Nivea'],
        'hierarchies': [
            'Beauty.Skincare.Moisturizers.Hydrating',
            'Beauty.Haircare.Shampoo.Volumizing',
            'PersonalCare.BodyWash.Fragranced'
        ]
    }
}

# Create a global dictionary for product_code mapping
product_code_mapping = {}
product_code_counter = 1
for category, details in product_line_hierarchy.items():
    for brand in details['brands']:
        for hierarchy in details['hierarchies']:
            product_code_mapping[(brand, hierarchy)] = f'P-{product_code_counter:04}'
            product_code_counter += 1

# Define realistic sales channels
sales_channels_realistic = [
    'RetailOutlet:Mall Store',
    'RetailOutlet:Outlet Store',
    'OnlineStore:Website',
    'OnlineStore:Mobile App',
    'B2BCustomers:Corporate Client',
    'B2BCustomers:Reseller'
]

# Promotion codes and discount logic
promo_codes = [
    'FREE10',
    'PARTY10',
    'WELCOMEBACK15',
    'WELCOMEBACK20',
    'NO_CODE',
    'THANKYOU20'
]

def calculate_discount(sales, promo_code):
    """
    Given the total sales amount and a promo_code,
    return the discount amount.
    """
    if promo_code == 'FREE10':
        return min(10, sales)
    elif promo_code == 'PARTY10':
        return sales * 0.10
    elif promo_code == 'WELCOMEBACK15':
        return sales * 0.11
    elif promo_code in ['WELCOMEBACK20', 'THANKYOU20']:
        return sales * 0.12
    else:
        return 0

def generate_fashion_data_with_brand(start_date, end_date):
    """
    Generate synthetic data with daily granularity between `start_date` and `end_date`.
    Each day, multiple transactions (orders) are generated across different products.

    Returns a pandas DataFrame that includes columns aligning with the DAG:
        PRICEEACH, UNIT_COST, QUANTITYORDERED, SALES, DISCOUNT, NET_SALES,
        FULFILLMENT_COST, MARKETING_COST, RETURN_COST, COST_OF_GOODS_SOLD,
        SHIPPING_REVENUE, PROFIT, PROFIT_MARGIN

    Along with contextual columns (e.g., ORDERDATE, STATUS, PRODUCTCODE).
    """
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    records = []

    for date in date_range:
        # Simple weekly seasonality: weekend (dayofweek 4,5) has slightly higher demand
        day_of_week = date.dayofweek
        # Base_demand adjusts number of transactions on that day
        base_demand = 10 if day_of_week in [4, 5] else 8

        # For each product, we'll generate 'base_demand' number of orders
        for (brand, hierarchy), product_code in product_code_mapping.items():
            num_orders = base_demand
            for _ in range(num_orders):
                # -----------------------
                # 1) Price & Costs
                # -----------------------
                price = round(np.random.uniform(45, 50), 2)
                # For healthy margins, the unit cost is ~35-40% of price
                unit_cost = round(price * np.random.uniform(0.35, 0.36), 2)

                # -----------------------
                # 2) Quantity
                # -----------------------
                quantity = np.random.choice([1, 2, 3], p=[0.9, 0.07, 0.03])

                # -----------------------
                # 3) Sales & Discount
                # -----------------------
                sales = round(price * quantity, 2)
                promo_code = np.random.choice(promo_codes)
                discount = round(calculate_discount(sales, promo_code), 2)
                net_sales = max(round(sales - discount, 2), 0)

                # -----------------------
                # 4) Other Cost Ratios
                # -----------------------
                # These ratios are used to compute costs from net_sales
                fulfillment_ratio = np.random.uniform(0.12, 0.13)  # e.g. higher if shipping is complex
                marketing_ratio = np.random.uniform(0.03, 0.04)
                return_ratio = np.random.uniform(0.01, 0.02)

                fulfillment_cost = round(net_sales * fulfillment_ratio, 2)
                marketing_cost = round(net_sales * marketing_ratio, 2)
                return_cost = round(net_sales * return_ratio, 2)

                # Cost of goods sold
                cost_of_goods_sold = round(unit_cost * quantity, 2)

                # Shipping revenue is some additional small fee
                shipping_revenue = round(np.random.uniform(1, 5), 2)

                # -----------------------
                # 5) Profit Calculation
                # -----------------------
                profit = round(
                    net_sales
                    - fulfillment_cost
                    - marketing_cost
                    - return_cost
                    - cost_of_goods_sold
                    + shipping_revenue,
                    2
                )
                profit_margin = round((profit / net_sales) * 100, 2) if net_sales > 0 else 0
                is_margin_negative = profit < 0

                # If margin is too extreme, do a small correction
                if profit_margin < -100:
                    profit = -net_sales
                    profit_margin = -100

                # -----------------------
                # 6) Contextual Fields
                # -----------------------
                city = np.random.choice(['NYC', 'Paris', 'Reims', 'Pasadena', 'San Francisco'])
                country = np.random.choice(['USA', 'France', 'Germany', 'UK', 'Italy'])
                state = np.random.choice(['NY', 'CA', 'TX', 'None'])
                postal_code = np.random.randint(10000, 99999)
                territory = np.random.choice(['EMEA', 'APAC', 'NA'])
                last_name = np.random.choice(['Smith', 'Doe', 'Brown', 'Lee'])
                first_name = np.random.choice(['John', 'Jane', 'Emily', 'Chris'])
                address_line1 = np.random.choice(['123 Main St', '456 Elm St', '789 Maple Ave'])
                deal_size = np.random.choice(['Small', 'Medium', 'Large'])

                # Build the transaction record
                records.append({
                    'ORDERNUMBER': np.random.randint(10000, 99999),
                    'QUANTITYORDERED': quantity,
                    'PRICEEACH': price,
                    'UNIT_COST': unit_cost,
                    'ORDERDATE': date,
                    'SALES': sales,
                    'DISCOUNT': discount,
                    'NET_SALES': net_sales,
                    'STATUS': np.random.choice(['Shipped', 'In Process', 'Cancelled'], p=[0.7, 0.2, 0.1]),
                    'QTR_ID': ((date.month - 1) // 3 + 1),
                    'MONTH_ID': date.month,
                    'YEAR_ID': date.year,
                    'CITY': city,
                    'COUNTRY': country,
                    'ADDRESSLINE1': address_line1,
                    'ADDRESSLINE2': None,
                    'STATE': state,
                    'POSTALCODE': postal_code,
                    'TERRITORY': territory,
                    'CONTACTLASTNAME': last_name,
                    'CONTACTFIRSTNAME': first_name,
                    'DEALSIZE': deal_size,
                    'PRODUCTCODE': product_code,
                    'BRAND': brand,
                    'MERCHANDISE_HIERARCHY': hierarchy,
                    'SALES_CHANNEL': np.random.choice(sales_channels_realistic),
                    'PROMO_CODE': promo_code,
                    'FULFILLMENT_COST': fulfillment_cost,
                    'MARKETING_COST': marketing_cost,
                    'RETURN_COST': return_cost,
                    'COST_OF_GOODS_SOLD': cost_of_goods_sold,
                    'SHIPPING_REVENUE': shipping_revenue,
                    'PROFIT': profit,
                    'PROFIT_MARGIN': profit_margin,
                    'IS_MARGIN_NEGATIVE': is_margin_negative,
                    'FULFILLMENT_RATIO': fulfillment_ratio,
                    'MARKETING_RATIO': marketing_ratio,
                    'RETURN_RATIO': return_ratio,
                })

    return pd.DataFrame(records)


# ------------------------------------------------------------------
# 3) ANOMALY INJECTION
# ------------------------------------------------------------------

def inject_anomalies_by_date(df, anomaly_schedule):
    """
    Inject anomalies on specific dates, each associated with a particular anomaly_type
    and severity. The impact is then recalculated and propagated downstream up to
    PROFIT_MARGIN, ensuring a clear root-cause pathway.

    Parameters:
    -----------
    df : pd.DataFrame
        The original DataFrame produced by the data-generation step.
    anomaly_schedule : dict
        Keys are dates (YYYY-MM-DD), values are (anomaly_type, severity).
        Example:
            {
                '2023-06-10': ('ExcessiveDiscount', 0.8),
                '2023-06-15': ('COGSOverstatement', 0.4),
                ...
            }

    Returns:
    --------
    pd.DataFrame
        A new DataFrame with the anomalies injected and all dependent
        calculations (NET_SALES, PROFIT, PROFIT_MARGIN, etc.) updated.
    """
    df = df.copy()  # Work on a copy to avoid altering the original
    df['ANOMALY_TYPE'] = None
    df['SEVERITY'] = None

    # For each date in anomaly_schedule, apply the specified anomaly
    for date_str, (anomaly_type, severity) in anomaly_schedule.items():
        date_mask = df['ORDERDATE'] == pd.to_datetime(date_str)

        # Example of choosing a subset of products to be affected
        # For clarity in root cause, you might limit anomalies to a smaller subset
        # or a single subset so it stands out more distinctly.
        affected_products = np.random.choice(
            df['PRODUCTCODE'].unique(),
            size=int(df['PRODUCTCODE'].nunique() * 0.3),
            replace=False
        )
        product_mask = df['PRODUCTCODE'].isin(affected_products)
        final_mask = date_mask & product_mask

        # If no rows match, continue
        if not df[final_mask].empty:
            df.loc[final_mask, 'ANOMALY_TYPE'] = anomaly_type
            df.loc[final_mask, 'SEVERITY'] = severity

            # --------------------
            # Anomaly-Specific Modifications
            # --------------------
            if anomaly_type == 'ExcessiveDiscount':
                # Overly high discount on SALES
                new_discount = (df.loc[final_mask, 'SALES'] * severity).round(2)
                # Ensure discount doesn't exceed total sales
                df.loc[final_mask, 'DISCOUNT'] = np.minimum(new_discount, df.loc[final_mask, 'SALES'])

                # Recalculate NET_SALES
                df.loc[final_mask, 'NET_SALES'] = (
                    df.loc[final_mask, 'SALES'] - df.loc[final_mask, 'DISCOUNT']
                ).round(2)

                # Dependent costs that rely on NET_SALES
                df.loc[final_mask, 'FULFILLMENT_COST'] = (
                    df.loc[final_mask, 'NET_SALES'] * df.loc[final_mask, 'FULFILLMENT_RATIO']
                ).round(2)
                df.loc[final_mask, 'MARKETING_COST'] = (
                    df.loc[final_mask, 'NET_SALES'] * df.loc[final_mask, 'MARKETING_RATIO']
                ).round(2)
                df.loc[final_mask, 'RETURN_COST'] = (
                    df.loc[final_mask, 'NET_SALES'] * df.loc[final_mask, 'RETURN_RATIO']
                ).round(2)

            elif anomaly_type == 'COGSOverstatement':
                # Inflating the UNIT_COST
                df.loc[final_mask, 'UNIT_COST'] = (
                    df.loc[final_mask, 'UNIT_COST'] * (1 + severity)
                ).round(2)

                # Recalculate COST_OF_GOODS_SOLD
                df.loc[final_mask, 'COST_OF_GOODS_SOLD'] = (
                    df.loc[final_mask, 'UNIT_COST'] * df.loc[final_mask, 'QUANTITYORDERED']
                ).round(2)

            elif anomaly_type == 'FulfillmentSpike':
                # Spike the FULFILLMENT_COST
                df.loc[final_mask, 'FULFILLMENT_COST'] = (
                    df.loc[final_mask, 'FULFILLMENT_COST'] * (1 + severity)
                ).round(2)

            elif anomaly_type == 'ShippingDisruption':
                # Disrupt shipping revenue: invert or scale down drastically
                df.loc[final_mask, 'SHIPPING_REVENUE'] = (
                    -df.loc[final_mask, 'SHIPPING_REVENUE'] * severity
                ).round(2)

            elif anomaly_type == 'ReturnSurge':
                # Surge in returns
                df.loc[final_mask, 'RETURN_COST'] = (
                    df.loc[final_mask, 'RETURN_COST'] * (1 + severity)
                ).round(2)

            # --------------------
            # Recalculate Profit & Margin
            # --------------------
            df.loc[final_mask, 'PROFIT'] = (
                df.loc[final_mask, 'NET_SALES']
                - df.loc[final_mask, 'FULFILLMENT_COST']
                - df.loc[final_mask, 'MARKETING_COST']
                - df.loc[final_mask, 'RETURN_COST']
                - df.loc[final_mask, 'COST_OF_GOODS_SOLD']
                + df.loc[final_mask, 'SHIPPING_REVENUE']
            ).round(2)

            df.loc[final_mask, 'PROFIT_MARGIN'] = np.where(
                df.loc[final_mask, 'NET_SALES'] > 0,
                (df.loc[final_mask, 'PROFIT'] / df.loc[final_mask, 'NET_SALES'] * 100).round(2),
                0
            )

            df.loc[final_mask, 'IS_MARGIN_NEGATIVE'] = (
                df.loc[final_mask, 'PROFIT'] < 0
            )

    return df