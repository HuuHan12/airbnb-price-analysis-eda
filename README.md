# 🏠 Airbnb Price Analysis & EDA: Phân Tích & Trực Quan Hóa Dữ Liệu Giá Thuê Airbnb Châu Âu

> **Đồ án môn học:** Phân tích và Trực quan hóa dữ liệu  
> **Khoa / Ngành:** Khoa Mạng máy tính và Truyền thông / Công nghệ Thông tin – Trường Đại học Công nghệ Thông tin (UIT – ĐHQG-HCM)  
> **Định hướng phát triển:** Nghiên cứu và xây dựng module định giá phòng phục vụ Chuyên đề tốt nghiệp *"Hệ thống du lịch thông minh và gợi ý khách sạn"*.

---

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458.svg?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-1.7%2B-green.svg)](https://xgboost.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 1. Giới thiệu (Introduction)

Trong lĩnh vực du lịch và lưu trú trực tuyến, bài toán định giá phòng tối ưu đóng vai trò then chốt trong việc hỗ trợ du khách đưa ra quyết định đặt phòng hợp lý và nâng cao hiệu quả kinh doanh của các đơn vị lưu trú. Đồ án tập trung giải quyết bài toán hồi quy (regression problem) nhằm dự đoán giá thuê phòng Airbnb (`realSum`) dựa trên các nhóm đặc trưng về vị trí địa lý, quy mô tiện ích phòng ốc, mức độ thuận tiện giao thông công cộng và các chỉ số đánh giá mức độ hài lòng của khách hàng. 

Dự án được xây dựng với mục tiêu kép:
1. **Mục tiêu học thuật:** Hoàn thành đồ án môn học *"Phân tích và Trực quan hóa dữ liệu"*, áp dụng toàn diện quy trình khoa học dữ liệu từ tiền xử lý, phân tích khám phá (EDA) đến xây dựng và đánh giá mô hình học máy.
2. **Mục tiêu ứng dụng thực tiễn:** Tạo tiền đề thực nghiệm vững chắc để đóng gói thành **Module Định giá phòng (Price Estimation Module)**, tích hợp trực tiếp vào Chuyên đề tốt nghiệp: *"Hệ thống du lịch thông minh và gợi ý khách sạn"*.

---

## 2. Về bộ dữ liệu (Dataset)

Dự án sử dụng bộ dữ liệu chuẩn hóa công khai về giá niêm yết phòng Airbnb tại các thành phố du lịch lớn của châu Âu.

| Thuộc tính | Chi tiết |
| :--- | :--- |
| **Tên bộ dữ liệu** | Airbnb Prices in European Cities |
| **Nguồn dữ liệu** | Kaggle |
| **Đường dẫn liên kết** | [Kaggle Dataset: airbnb-prices-in-european-cities](https://www.kaggle.com/datasets/thedevastator/airbnb-prices-in-european-cities) |
| **Cấu trúc lưu trữ** | 20 tệp CSV (tương ứng với 10 thành phố châu Âu × 2 loại thời điểm: ngày thường `weekdays` và cuối tuần `weekends`) |
| **Quy mô tập dữ liệu** | Mỗi tệp chứa từ 1.100 đến 5.500 dòng, 15–20 cột thuộc tính; Tổng hợp toàn bộ đạt quy mô **hơn 50.000 dòng dữ liệu** |
| **Biến mục tiêu (Target)** | `realSum`: Tổng giá thuê niêm yết cho 2 người trong kỳ lưu trú 2 đêm (Đơn vị: **EUR**) |

### Danh mục các đặc trưng dữ liệu (Features)

* **Nhóm đặc trưng định lượng (Numerical Features):**
  * `person_capacity`: Sức chứa tối đa của listing (số lượng khách).
  * `bedrooms`: Số lượng phòng ngủ.
  * `dist`: Khoảng cách thực tế từ căn hộ đến trung tâm thành phố (km).
  * `metro_dist`: Khoảng cách từ căn hộ đến trạm tàu điện ngầm (metro) gần nhất (km).
  * `cleanliness_rating`: Điểm đánh giá mức độ vệ sinh và sạch sẽ của phòng.
  * `guest_satisfaction_overall`: Điểm đánh giá mức độ hài lòng chung từ khách lưu trú.
  * `lat`, `lng`: Tọa độ địa lý vĩ độ (Latitude) và kinh độ (Longitude) của phòng.
  * `attr_index`: Chỉ số định lượng về mức độ hấp dẫn du lịch của khu vực xung quanh.
  * `rest_index`: Chỉ số định lượng về mật độ và chất lượng nhà hàng/ẩm thực xung quanh.

* **Nhóm đặc trưng phân loại và logic (Categorical / Boolean Features):**
  * `room_type`: Loại hình chỗ ở (vd: Entire home/apt, Private room, Shared room).
  * `room_shared`: Biến logic xác định phòng ở dạng dùng chung (Shared room: `True`/`False`).
  * `room_private`: Biến logic xác định có phòng ngủ riêng biệt (Private room: `True`/`False`).
  * `host_is_superhost`: Trạng thái chủ nhà đạt danh hiệu Superhost (`True`/`False`).
  * `multi`: Biến nhị phân chỉ định chủ nhà sở hữu nhiều phòng niêm yết trên nền tảng.
  * `biz`: Biến nhị phân chỉ định chỗ ở phục vụ mục đích kinh doanh/công tác chuyên nghiệp.

---

## 3. Mục tiêu phân tích (Objectives)

Dự án triển khai theo quy trình phân tích và học máy có cấu trúc bao gồm các nhiệm vụ cốt lõi:

* **Tiền xử lý dữ liệu (Data Preprocessing):**
  * Kiểm tra tính toàn vẹn của dữ liệu, xử lý giá trị khuyết thiếu (missing values).
  * Nhận diện và xử lý các giá trị ngoại lai (outliers) đối với biến mục tiêu `realSum` và các thuộc tính khoảng cách.
  * Chuẩn hóa tỉ lệ (feature scaling) đối với các đặc trưng số và mã hóa phù hợp đối với các đặc trưng phân loại.
* **Trực quan hóa khám phá dữ liệu (Exploratory Data Analysis - EDA):**
  * Khảo sát phân phối giá thuê theo từng thành phố và so sánh biến động giá giữa ngày trong tuần và cuối tuần.
  * Phân tích ma trận hệ số tương quan (correlation matrix) giữa các biến định lượng và biến giá mục tiêu.
  * Phân tích trực quan tác động của vị trí địa lý (khoảng cách trung tâm, khoảng cách trạm metro), tiện ích phòng và chỉ số danh tiếng tới giá phòng.
* **Xây dựng mô hình hồi quy (Regression Modeling):**
  * Thiết lập mô hình cơ sở: **Linear Regression** (Hồi quy tuyến tính).
  * Huấn luyện mô hình phi tuyến dạng cây quyết định: **Random Forest Regressor**.
  * Tối ưu hóa mô hình tăng cường độ dốc tiên tiến: **XGBoost Regressor**.
* **Đánh giá mô hình (Model Evaluation):**
  * So sánh hiệu năng dự đoán giữa các mô hình thông qua các thước đo tiêu chuẩn: **RMSE** (Root Mean Squared Error), **MAE** (Mean Absolute Error), và **R² Score** (Hệ số xác định).
* **Phân tích phần dư phát hiện bất thường (Residual Analysis):**
  * Ứng dụng phân tích độ lệch giữa giá thực tế và giá dự đoán từ mô hình để nhận diện các phòng bị định giá bất thường (hiện tượng định giá ảo, phòng quá đắt hoặc quá rẻ so với giá trị thực tế của vị trí và tiện ích).

---

## 4. Cấu trúc thư mục (Project Structure)

Dự án được bố trí theo cấu trúc chuẩn của một dự án Khoa học dữ liệu / Machine Learning:

```text
airbnb-price-analysis-eda/
│
├── data/
│   ├── raw/                  # 20 file CSV tải về trực tiếp từ Kaggle
│   └── processed/            # Dữ liệu sau khi làm sạch, gộp thành phố và chuẩn hóa
│
├── notebooks/
│   ├── 01_data_preprocessing.ipynb    # Tiền xử lý, xử lý null, outlier, làm sạch
│   ├── 02_exploratory_data_analysis.ipynb # Trực quan hóa EDA chi tiết
│   ├── 03_regression_modeling.ipynb    # Huấn luyện mô hình Linear Regression, RF, XGBoost
│   └── 04_residual_analysis.ipynb     # Phân tích phần dư, phát hiện listing định giá ảo
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py        # Hàm đọc, gộp và kiểm tra tính toàn vẹn 20 file CSV
│   ├── preprocess.py         # Pipeline làm sạch dữ liệu, mã hóa và co giãn đặc trưng
│   ├── visualization.py      # Các hàm vẽ biểu đồ phân phối, tương quan, bản đồ
│   └── evaluate.py           # Tính toán RMSE, MAE, R2 và xuất biểu đồ phần dư
│
├── visualizations/           # Lưu trữ các biểu đồ EDA và biểu đồ đánh giá mô hình (.png)
├── models/                   # Lưu trữ trọng số mô hình đã huấn luyện (.pkl, .joblib)
├── requirements.txt          # Danh sách thư viện và phiên bản phụ thuộc
└── README.md                 # Tài liệu giới thiệu và hướng dẫn tổng thể dự án
```

---

## 5. Công nghệ sử dụng (Tech Stack)

| Phân loại | Công nghệ / Thư viện | Mục đích sử dụng |
| :--- | :--- | :--- |
| **Ngôn ngữ cốt lõi** | `Python (>= 3.9)` | Môi trường lập trình chính |
| **Xử lý & Thao tác dữ liệu** | `Pandas`, `NumPy` | Thao tác trên DataFrame, tính toán ma trận và biến đổi đặc trưng |
| **Trực quan hóa dữ liệu** | `Matplotlib`, `Seaborn` | Xây dựng đồ thị tĩnh, biểu đồ phân phối, biểu đồ tương quan |
| **Trực quan hóa tương tác** | `Plotly` | Xây dựng biểu đồ tương tác và trực quan hóa phân bố không gian địa lý |
| **Học máy & Mô hình hóa** | `Scikit-learn` | Huấn luyện Linear Regression, Random Forest, tiền xử lý và đánh giá độ đo |
| **Gradient Boosting** | `XGBoost` | Xây dựng mô hình hồi quy độ dốc nâng cao nhằm tối ưu hóa độ chính xác |
| **Môi trường thực thi** | `Jupyter Notebook / Lab` | Môi trường thử nghiệm và trình bày trực quan từng giai đoạn phân tích |

---

## 6. Hướng dẫn cài đặt và chạy (Installation & Usage)

Thực hiện các bước sau để thiết lập môi trường và chạy thử nghiệm đồ án:

### Bước 1: Sao chép repository về máy cục bộ

```bash
git clone https://github.com/HuuHan12/airbnb-price-analysis-eda.git
cd airbnb-price-analysis-eda
```

### Bước 2: Khởi tạo và kích hoạt môi trường ảo

* **Trên Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **Trên Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Bước 3: Cài đặt các gói phụ thuộc

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Bước 4: Tải và thiết lập bộ dữ liệu

1. Truy cập [Kaggle Dataset: Airbnb Prices in European Cities](https://www.kaggle.com/datasets/thedevastator/airbnb-prices-in-european-cities).
2. Tải toàn bộ tệp nén hoặc sử dụng Kaggle API:
   ```bash
   kaggle datasets download -d thedevastator/airbnb-prices-in-european-cities -p data/raw/
   ```
3. Giải nén tất cả các file CSV vào thư mục `data/raw/` sao cho đường dẫn có dạng:
   ```text
   data/raw/amsterdam_weekdays.csv
   data/raw/amsterdam_weekends.csv
   ...
   ```

### Bước 5: Thực thi các Notebook phân tích

Khởi động Jupyter Notebook và mở các notebook theo trình tự:

```bash
jupyter notebook
```

* Chạy lần lượt từ `01_data_preprocessing.ipynb` đến `04_residual_analysis.ipynb`.

---

## 7. Kết quả chính (Key Findings)

### 7.1. Hiệu năng so sánh giữa các mô hình hồi quy
> *[Sẽ cập nhật sau khi hoàn thành phân tích]*

| Mô hình | RMSE (EUR) | MAE (EUR) | R² Score | Ghi chú |
| :--- | :---: | :---: | :---: | :--- |
| **Linear Regression** | *[Sẽ cập nhật]* | *[Sẽ cập nhật]* | *[Sẽ cập nhật]* | Baseline model |
| **Random Forest Regressor** | *[Sẽ cập nhật]* | *[Sẽ cập nhật]* | *[Sẽ cập nhật]* | Phi tuyến, tương tác đa đặc trưng |
| **XGBoost Regressor** | *[Sẽ cập nhật]* | *[Sẽ cập nhật]* | *[Sẽ cập nhật]* | Mô hình tối ưu chính |

### 7.2. Các yếu tố tác động mạnh nhất đến giá thuê (Feature Importance)
> *[Sẽ cập nhật sau khi hoàn thành phân tích]*

### 7.3. Kết quả phân tích định giá bất thường (Residual Analysis)
> *[Sẽ cập nhật sau khi hoàn thành phân tích]*

---

## 8. Hướng phát triển tiếp theo (Future Work)

Sau khi hoàn thành phạm vi đồ án môn học, các kết quả nghiên cứu sẽ tiếp tục được mở rộng và phát triển theo các hướng sau:

1. **Tích hợp vào Chuyên đề tốt nghiệp:** Đóng gói mô hình hồi quy dự đoán giá thành một RESTful API microservice (sử dụng FastAPI) để tích hợp trực tiếp vào đồ án tốt nghiệp: *"Hệ thống du lịch thông minh và gợi ý khách sạn"*.
2. **Mở rộng dữ liệu thực tế tại Việt Nam:** Thu thập, làm sạch và chuẩn hóa tập dữ liệu phòng khách sạn và homestay tại các trung tâm du lịch lớn ở Việt Nam (Đà Lạt, Đà Nẵng, Phú Quốc, Nha Trang, TP.HCM, Hà Nội) nhằm kiểm định khả năng thích ứng của mô hình trên thị trường nội địa.
3. **Xây dựng điểm tương thích ngân sách (Budget Compatibility Score):** Phát triển chỉ số tính toán mức độ hợp lý giữa mức giá niêm yết của phòng và giá trị thực tế dự đoán từ mô hình, kết hợp với công cụ gợi ý (Recommendation System) nhằm ưu tiên đề xuất các điểm lưu trú có tỷ lệ "chất lượng vượt mức giá" (Best Value for Money) cho du khách.

---

## 9. Tác giả (Author)

* **Sinh viên thực hiện:** [Họ và tên sinh viên] (GitHub: [@HuuHan12](https://github.com/HuuHan12))
* **Mã số sinh viên (MSSV):** [Điền MSSV]
* **Lớp:** [Điền tên lớp sinh hoạt]
* **Khoa / Ngành:** Công nghệ Thông tin – Trường Đại học Công nghệ Thông tin (UIT), Đại học Quốc gia TP.HCM
* **Giảng viên hướng dẫn môn học:** [Họ và tên Giảng viên]
* **Liên hệ:** [Email sinh viên]@uit.edu.vn

---

*Dự án phục vụ mục đích học tập và nghiên cứu khoa học tại Trường Đại học Công nghệ Thông tin (ĐHQG-HCM).*
