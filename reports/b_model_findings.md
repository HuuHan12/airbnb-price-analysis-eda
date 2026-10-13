# T09: đa thức và Ridge của B

Đã chạy train/CV, không đánh giá hoặc dự đoán test. So sánh cùng config, manifest và folds trong T07.

- M3: chọn degree_3 theo CV MSE trung bình 79228.00, fit lại chỉ train để lưu model.
- M4: chọn alpha_0.1 theo CV MSE trung bình 79988.15, fit lại chỉ train để lưu model.

Chưa tuyên bố mô hình thắng chung: phải nhận M0/M1/M2 của A và chốt bằng CV trước T10. Mean RMSE của folds khác sqrt(mean MSE); CSV lưu rõ từng fold và mean/std.

Allowlist cố định theo metadata trước CV; không lọc predictor theo target. Bậc 2/3 chỉ trên capacity, bedrooms, dist; các nhóm city/day/room và phần numeric còn lại dùng cùng biểu diễn nền. Ridge dùng dãy alpha đã có trong kế hoạch.
