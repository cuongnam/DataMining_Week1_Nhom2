# Apriori — Kết quả thực nghiệm và nhận xét

Tài liệu này trình bày kết quả thực nghiệm từ lần chạy Apriori với các tham số bạn đã sử dụng, kèm nhận xét ngắn gọn để phục vụ báo cáo hoặc bài tập.

Tham số đã dùng (theo `src/apriori_experiments.py` hiện tại):

- `supports = [0.025, 0.03, 0.02]`
- `confidences = [0.2, 0.4, 0.6]`
- `lifts = [1.0, 1.5, 2.0]`

File tóm tắt kết quả: `data/processed/apriori_experiments/apriori_experiment_summary.csv`

Tóm tắt các kết quả chính (số frequent itemsets — `frequent_itemsets`, số luật sau lọc — `rules_after_filter`):

- **Support = 0.02:** `frequent_itemsets = 400`
  - confidence 0.2 → `rules_after_filter = 209`
  - confidence 0.4 → `rules_after_filter = 138`
  - confidence 0.6 → `rules_after_filter = 35`

- **Support = 0.025:** `frequent_itemsets = 230`
  - confidence 0.2 → `rules_after_filter = 86`
  - confidence 0.4 → `rules_after_filter = 65`
  - confidence 0.6 → `rules_after_filter = 23`

- **Support = 0.03:** `frequent_itemsets = 145`
  - confidence 0.2 → `rules_after_filter = 22`
  - confidence 0.4 → `rules_after_filter = 18`
  - confidence 0.6 → `rules_after_filter = 12`

Nhận xét ngắn từ kết quả này:

- Giảm `min_support` (ví dụ 0.03 → 0.02) làm số frequent itemsets tăng rất mạnh và dẫn tới số luật nhiều hơn (ví dụ confidence=0.2: 22 → 209). Điều này chứng tỏ `support` là yếu tố chính quyết định kích thước không gian tìm kiếm.
- Tăng `min_confidence` trong cùng `support` giảm số luật rõ rệt (ví dụ support=0.02: 209 → 138 → 35 khi confidence tăng 0.2→0.4→0.6), vì `confidence` loại các luật có P(consequent|antecedent) thấp.
- Trong lưới tham số đã chạy, `min_lift` (1.0 → 2.0) có ảnh hưởng rất nhỏ tới số lượng luật — điều này nghĩa là nhiều luật đã đạt `lift` >= 2 hoặc ngưỡng lift thử nghiệm không phân biệt mạnh trên bộ luật này.


