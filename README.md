# 📦 Case Study: Phân tích độ nhạy tham số (Parameter Sensitivity)

## 👥 Thông tin Nhóm
- **Chủ đề:** Phân tích độ nhạy của `min_support` cho Apriori trên Online Retail (UCI)
- **Dataset:** Online Retail (UCI) — đã lọc UK và lưu ở `data/processed/cleaned_uk_data.csv`
- **Thành viên:** 
  - Nguyễn Nam Cường
  - Nguyễn Văn Đạt
  - Trần Việt Vinh

## 🎯 Mục tiêu
Xác định ảnh hưởng của các giá trị `min_support` khác nhau lên:
1. **Số lượng luật** được sinh ra
2. **Chất lượng luật** (phân bố support, confidence, lift)
3. **Cấu trúc cụm sản phẩm** (clusters của các sản phẩm liên kết)

Từ đó **rút ra ngưỡng `min_support` hợp lý** cho bài toán giỏ hàng.

## 1️⃣ Ý tưởng & Feynman Style

### Apriori làm gì?
Tìm những **tập sản phẩm thường xuất hiện cùng nhau** trong các đơn hàng, rồi từ đó sinh ra các **luật "A → B"** (nếu khách mua A, chắc chắn sẽ mua B với xác suất/mức độ nào đó).

### Tại sao phù hợp cho bài toán giỏ hàng?
- Bài toán giỏ hàng cần tìm **mối liên kết giữa sản phẩm**.
- Apriori hiệu quả khi dữ liệu **rời rạc** (presence/absence).
- Ta muốn lấy luật dạng **association** để dùng cho cross-sell và bundle.

### Ý tưởng thuật toán (1–2 câu)
Apriori lặp để sinh frequent itemsets từ 1-itemset lên, loại bỏ itemset hiếm (support < ngưỡng), rồi xuất các luật từ các frequent itemsets đó.

---

## 2️⃣ Quy trình Thực hiện

1. **Load & làm sạch dữ liệu** — lọc UK, xóa hóa đơn cancel, xóa quantity âm
2. **Tạo ma trận basket** — Invoice × Description → boolean (1 = sản phẩm trong đơn, 0 = không)
3. **Áp dụng Apriori với dải `min_support` khác nhau** — thử [0.015, 0.02, 0.025, 0.03, 0.04, 0.05]
4. **Sinh luật, lọc theo `min_confidence` và `min_lift`**
5. **Lưu kết quả, vẽ biểu đồ** — số luật vs support; phân bố support/confidence/lift; kích thước cụm
6. **Rút ra ngưỡng hợp lý** và đề xuất kinh doanh

---

## 3️⃣ Tiền xử lý Dữ liệu

### Những bước làm sạch:
- ❌ Loại bỏ sản phẩm rỗng / thiếu mô tả
- ❌ Loại bỏ transaction bị cancel (InvoiceNo bắt đầu bằng "C")
- ❌ Loại bỏ quantity ≤ 0 và unit price ≤ 0
- ✅ Chỉ lấy khách hàng ở UK

### Thống kê nhanh (sau tiền xử lý):
- Xem `data/processed/cleaned_uk_data.csv` để kiểm tra số giao dịch và số sản phẩm duy nhất

---

## 4️⃣ Áp dụng Apriori

### Tham số đã thử nghiệm:
```
min_supports = [0.015, 0.02, 0.025, 0.03, 0.04, 0.05]
min_confidence = 0.3 (lọc sau)
min_lift = 1.2 (lọc sau)
```

### Mẫu code:
```python
from mlxtend.frequent_patterns import apriori, association_rules

# Sinh frequent itemsets
frequent_itemsets = apriori(basket_df, min_support=0.025, use_colnames=True)

# Sinh luật
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.2)

# Sắp xếp theo chất lượng
rules = rules.sort_values(["lift", "confidence"], ascending=False)
print(rules.head(20))
```

### Script chạy sensitivity:
```bash
python src/parameter_sensitivity.py
```
Kết quả lưu ở: `data/processed/apriori_experiments/parameter_sensitivity_summary.csv`

---

## 5️⃣ Kết quả Thực nghiệm

### Bảng tóm tắt (từ parameter_sensitivity_summary.csv):

| min_support | frequent_itemsets | rules | num_clusters | largest_cluster | conf_mean | conf_median | lift_mean | lift_median |
|---|---|---|---|---|---|---|---|---|
| **0.015** | 755 | 516 | 20 | 61 | 0.499 | 0.474 | 10.27 | 8.90 |
| **0.02** | 400 | 184 | 13 | 31 | 0.495 | 0.477 | 8.97 | 7.60 |
| **0.025** | 230 | **75** | 10 | 17 | **0.536** | **0.507** | **9.13** | **7.22** |
| **0.03** | 145 | 21 | 5 | 5 | 0.587 | 0.606 | 10.05 | 7.13 |
| **0.04** | 66 | 2 | 1 | 2 | 0.541 | 0.541 | 6.31 | 6.31 |
| **0.05** | 34 | 0 | 0 | 0 | — | — | — | — |

---

## 6️⃣ Insight từ Kết quả

### **Insight #1: Tác động của min_support lên số lượng luật**
- Khi `min_support` giảm → **số frequent itemsets tăng mạnh** (755 ở 0.015 → 34 ở 0.05)
- Số luật **giảm theo hàm mũ**: 516 → 184 → 75 → 21 → 2 → 0
- Threshold quá thấp → luật quá nhiều (khó hành động); quá cao → luật quá ít (mất tín hiệu)

### **Insight #2: Chất lượng luật (Confidence & Lift)**
- Ở `min_support = 0.015` (thấp): median confidence 0.47, median lift 8.90
- Ở `min_support = 0.025` (vừa): median confidence 0.51, median lift 7.22 → **vẫn đạt chất lượng tốt**
- Ở `min_support = 0.03` (cao): median confidence 0.61, median lift 7.13 → confidence cao nhưng số luật rất ít (21)
- **Kết luận**: Confidence tăng chút ít khi support tăng, nhưng trade-off với số luật mạnh hơn

### **Insight #3: Cấu trúc cụm sản phẩm**
- `min_support = 0.015`: 20 clusters, **largest = 61** → một cluster khổng lồ (nhiễu, khó hiểu)
- `min_support = 0.025`: 10 clusters, **largest = 17** → cấu trúc rõ ràng, dễ diễn giải
- `min_support = 0.03`: 5 clusters, **largest = 5** → quá nhỏ, mất nhiều luật
- **Kết luận**: Cluster lớn ở support thấp; support trung bình cho cluster hợp lý

### **Insight #4: Điểm cân bằng**
- `min_support = 0.025` là **ngưỡng tối ưu** cho dataset này:
  - 75 luật (vừa phải, dễ quản lý)
  - Median confidence 0.51, median lift 7.22 (chất lượng tốt)
  - 10 clusters với largest = 17 (cấu trúc rõ ràng)

### **Insight #5: Lọc thêm để tăng độ ổn định**
- Dùng `min_confidence >= 0.5` và `min_lift >= 1.5` có thể lọc sâu hơn
- Giảm luật nhưng tăng độ tin cậy của các luật còn lại (actionable insights)

---

## 7️⃣ Kết luận & Đề xuất Kinh doanh

### **Ngưỡng Đề Xuất**
```
✅ min_support = 0.025 (2.5%)
✅ min_confidence >= 0.5 (thêm lọc)
✅ min_lift >= 1.5 (thêm lọc)
```

### **Gợi ý Cross-Sell**
- Thực hiện chiến dịch **bundle/gợi ý kèm** cho các cặp sản phẩm có lift cao (≥ 7)
- Ví dụ: "Khách mua A → 7x khả năng mua B" → tập trung marketing vào B khi A được bán

### **Gợi ý Sắp Xếp Kệ Hàng**
- Các sản phẩm trong **cùng cluster** (10 clusters) nên **đặt gần nhau**
- Dễ giúp khách phát hiện (offline: kệ cạnh nhau; online: trang sản phẩm liên kết)

### **Gợi ý Khuyến Mãi**
- Dùng sản phẩm **mồi** (antecedent có high lift) để **khuyến khích mua** consequent
- Ví dụ: Giảm giá sản phẩm A → khách mua A + gợi ý B → tăng doanh số B

### **Gợi ý Tối ưu Tồn Kho**
- Các cặp sản phẩm có lift cao nên **tồn kho song song** (không bao giờ hết một trong hai)
- Giảm risk khách không mua được bộ sản phẩm do hết hàng

---

## 8️⃣ File & Kết quả

### **Script thực hiện:**
- 📄 [src/parameter_sensitivity.py](src/parameter_sensitivity.py) — chạy sensitivity analysis
- 📄 [src/apriori_library.py](src/apriori_library.py) — thư viện Apriori + visualization
- 📄 [src/apriori_experiments.py](src/apriori_experiments.py) — script experiments gốc

### **Dữ liệu & Kết quả:**
- 📊 [data/processed/cleaned_uk_data.csv](data/processed/cleaned_uk_data.csv) — dữ liệu đã làm sạch
- 📊 [data/processed/apriori_experiments/parameter_sensitivity_summary.csv](data/processed/apriori_experiments/parameter_sensitivity_summary.csv) — bảng tóm tắt sensitivity
- 📊 [data/processed/apriori_experiments/rules/](data/processed/apriori_experiments/rules/) — folder top rules cho từng `min_support`
  - `top_rules_s0p015.csv` (516 luật)
  - `top_rules_s0p02.csv` (184 luật)
  - `top_rules_s0p025.csv` (75 luật) ← **Recommend**
  - `top_rules_s0p03.csv` (21 luật)
  - …

### **Chạy lại thực nghiệm:**
```bash
cd d:\KHMT_16-01\Data Mining\Projects\shopping_cart_analysis
python src\parameter_sensitivity.py
```

---

## 9️⃣ Slide Trình Bày
- Link Slide: *(thêm sau khi tạo)*

---

