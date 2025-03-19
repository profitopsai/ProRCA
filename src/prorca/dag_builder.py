def DagBuilder(cols):
    edges = [
        # PRICEEACH influences UNIT_COST and SALES
        ("PRICEEACH", "UNIT_COST"),
        ("PRICEEACH", "SALES"),
        # QUANTITYORDERED influences SALES, FULFILLMENT_COST, COST_OF_GOODS_SOLD, and SHIPPING_REVENUE
        ("QUANTITYORDERED", "SALES"),
        ("QUANTITYORDERED", "FULFILLMENT_COST"),
        ("QUANTITYORDERED", "COST_OF_GOODS_SOLD"),
        ("QUANTITYORDERED", "SHIPPING_REVENUE"),
        # SALES influences DISCOUNT, NET_SALES, and SHIPPING_REVENUE
        ("SALES", "DISCOUNT"),
        ("SALES", "NET_SALES"),
        ("SALES", "SHIPPING_REVENUE"),
        # UNIT_COST and QUANTITYORDERED combine to form COST_OF_GOODS_SOLD
        ("UNIT_COST", "COST_OF_GOODS_SOLD"),
        # DISCOUNT influences NET_SALES (net sales = sales - discount)
        ("DISCOUNT", "NET_SALES"),
        # NET_SALES is used to compute RETURN_COST, PROFIT, and later PROFIT_MARGIN
        ("NET_SALES", "RETURN_COST"),
        ("NET_SALES", "PROFIT"),
        ("NET_SALES", "PROFIT_MARGIN"),
        # The cost components feed into PROFIT
        ("FULFILLMENT_COST", "PROFIT"),
        ("MARKETING_COST", "PROFIT"),
        ("RETURN_COST", "PROFIT"),
        ("COST_OF_GOODS_SOLD", "PROFIT"),
        ("SHIPPING_REVENUE", "PROFIT"),
        # PROFIT drives PROFIT_MARGIN and IS_MARGIN_NEGATIVE
        ("PROFIT", "PROFIT_MARGIN"),
    ]

    return edges
