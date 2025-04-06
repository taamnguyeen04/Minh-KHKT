import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Đọc dữ liệu từ file CSV
df = pd.read_csv("similarity_results.csv")  # Thay bằng đường dẫn file của bạn

print(df.describe())
