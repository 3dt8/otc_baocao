import pandas as pd

def fmt(x):
    try:
        return f"{x:,.0f}"
    except:
        return x

def to_text_clean(val):
    try:
        return str(val).replace(".0", "").strip()
    except:
        return ""

def pad_customer_10(val):
    try:
        return str(int(float(val))).zfill(10)
    except:
        return ""