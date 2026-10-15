"""Preserve Han's notebook format from 67fb260; patch portable IO only."""
from copy import deepcopy
from pathlib import Path
import json
import pprint
import nbformat
from final_han_sections import HAN_CELLS
from portable_io_cells import PORTABLE_IO

ROOT = Path(__file__).resolve().parents[1]
cells = deepcopy(HAN_CELLS)


def replace(index, old, new):
    assert old in cells[index]['source'], (index, old[:60])
    cells[index]['source'] = cells[index]['source'].replace(old, new)


replace(0, '**Cách sử dụng:** mở file này và chọn **Restart Kernel and Run All**.',
        '''**Cách sử dụng:** đặt notebook và `airbnb_combined.csv` cùng thư mục,
mở kernel tại thư mục đó rồi chọn **Restart Kernel and Run All**.
Bộ code/data chỉ có hai file; không cần JSON, CSV manifest, src, raw hoặc model ngoài.
Notebook không tự tải mạng và không ghi file trung gian.''')
replace(1, 'Nạp từng file để kiểm số mẫu/schema, rồi thêm `city`, `day_type`, `source_file`, `source_row`.',
        'Nạp CSV gộp đã giữ đủ 20 cột gốc và bốn cột `city`, `day_type`, `source_file`, `source_row`.')
replace(1, 'CSV gộp phải khớp dữ liệu nạp lại trước khi sử dụng split đã chốt.',
        'Hash kiểm đúng snapshot đã chốt. Inventory tổng hợp từ CSV gộp; bản nộp không mở lại 20 CSV nguồn.')

replace(2, 'import json\n', '')
source = cells[2]['source']
start = source.index('# Xác định thư mục gốc của dự án')
end = source.index('# Cấu hình hiển thị pandas')
cells[2]['source'] = source[:start] + '''# Xác định thư mục chứa notebook và CSV đi kèm
ROOT = Path.cwd()
DATA_PATH = ROOT / 'airbnb_combined.csv'
if not DATA_PATH.is_file():
    raise FileNotFoundError(
        f'Thiếu airbnb_combined.csv trong {ROOT}. '
        'Đặt CSV cạnh notebook và mở kernel tại thư mục đó.'
    )

''' + source[end:]

expected_hash = json.loads((ROOT / 'config/experiment_config.json').read_text(encoding='utf-8'))['data_sha256']
cells[3]['source'] = '''# 1. Nạp CSV gộp và kiểm tra đúng dữ liệu đã chốt
expected_data_hash = ''' + repr(expected_hash) + '''
hash_now = hashlib.sha256(DATA_PATH.read_bytes().replace(b'\\r\\n', b'\\n')).hexdigest()
if hash_now != expected_data_hash:
    raise ValueError('CSV không khớp snapshot đã chốt; dùng nguyên airbnb_combined.csv đi kèm.')

df = pd.read_csv(DATA_PATH)
metadata_columns = ['city', 'day_type', 'source_file', 'source_row']
original_columns = [column for column in df.columns if column not in metadata_columns]
assert df.shape == (51707, 24)
assert len(original_columns) == 20
assert df.columns.tolist() == original_columns + metadata_columns

# Inventory theo nhóm nguồn trong CSV gộp, không đọc lại 20 CSV thô
inventory_records = []
for file_name, df_part in df.groupby('source_file', sort=True):
    city_name, day_name = Path(file_name).stem.rsplit('_', 1)
    assert day_name in ['weekdays', 'weekends']
    assert df_part.city.eq(city_name).all()
    assert df_part.day_type.eq(day_name).all()
    assert df_part.source_row.eq(df_part['Unnamed: 0']).all()
    inventory_records.append({
        'Tệp': file_name,
        'Thành phố': city_name,
        'Loại ngày': day_name,
        'Số dòng': len(df_part),
        'Số cột gốc': len(original_columns),
        'Ô khuyết': int(df_part.isna().sum().sum())
    })

inventory = pd.DataFrame(inventory_records)
assert len(inventory) == 20
assert inventory['Số dòng'].sum() == len(df)
assert df.city.nunique() == 10
assert df.groupby(['city', 'day_type']).size().shape[0] == 20

print(f"-> Đã nạp CSV gộp: {df.shape[0]:,} dòng x {df.shape[1]} cột.")
print(f"-> Số thành phố: {df.city.nunique()} | Số nhóm nguồn: {len(inventory)}")
display(inventory)
'''

# Keep dictionary layout and all functions; retain factual wording corrections.
replace(4, 'giá trị 0 là phòng studio/phòng mở', 'giá trị 0 là quan sát hợp lệ, chưa xác minh là studio')
replace(5, 'phạm vi hợp lệ của châu Âu', 'miền lat/lng hợp lệ; chưa xác minh hệ tọa độ gốc')
replace(6, 'Tọa độ địa lý ngoài phạm vi châu Âu', 'Tọa độ ngoài miền lat/lng hợp lệ')
replace(6, '(đặc tính lấy mẫu trên cùng tòa nhà/khu vực)', '(chưa xác minh nguyên nhân lặp hoặc listing ID)')
cells[6]['source'] += "\nassert quality_report['Số lượng vi phạm'].eq(0).all()\n"
replace(7, 'bởi các bất động sản cao cấp có giá lên đến hàng nghìn EUR.',
        'bởi một số quan sát giá rất cao; chưa có nhãn xác minh phân khúc cao cấp.')
replace(7, 'Lý do: trong lĩnh vực lưu trú và du lịch, các căn hộ hạng sang có giá thuê cao là thực tế kinh doanh khách quan, không phải do lỗi nhập liệu. Việc loại bỏ nhân tạo sẽ làm sai lệch bản chất thị trường.',
        'Lý do: chưa có bằng chứng xác minh các giá cao là lỗi nhập liệu. IQR là cờ mô tả, không tự động là lý do loại mẫu; giao thức giữ nguyên giá cho mọi mô hình.')
replace(9, 'để tránh rò rỉ dữ liệu hoặc đa cộng tuyến.',
        'theo giao thức đã chốt: price_tier dẫn xuất từ target; dist_bin được bỏ do biểu diễn dư thừa của khoảng cách.')
replace(11, '(các phòng khác nhau trong cùng một tòa nhà hoặc khu phức hợp).',
        '(chưa xác minh nguyên nhân lặp hoặc listing ID).')

# Reconstruct the exact reviewed split in memory, without JSON/manifest files.
full_config = json.loads((ROOT / 'config/experiment_config.json').read_text(encoding='utf-8'))
config = {key: full_config[key] for key in [
    'protocol_id', 'target', 'trace_keys', 'predictors', 'slr_feature',
    'polynomial_features', 'polynomial_degrees', 'ridge_alphas']}
cells[13]['source'] = 'config = ' + pprint.pformat(config, width=100, sort_dicts=False) + '\n\n' + PORTABLE_IO[13]
replace(15, '# Các bảng của notebook cuối ghi riêng; không ghi đè sản phẩm bàn giao cũ.',
        '# Các bảng giữ trong bộ nhớ; không ghi file trung gian.\ntables = {}')
replace(15, "    path = FINAL_DIR / name\n    frame.to_csv(path, index=False, encoding='utf-8-sig')\n    return path",
        '    tables[name] = frame.copy()\n    return name')
replace(16, "pd.read_csv(FINAL_DIR / 'eda_day_comparison_by_room.csv')", "tables['eda_day_comparison_by_room.csv']")
replace(33, "raw_case = pd.read_csv(ROOT / 'data/raw' / case.source_file)\nraw_case = raw_case.loc[raw_case['Unnamed: 0'].eq(case.source_row)]",
        "raw_case = df.loc[df.source_file.eq(case.source_file) & df.source_row.eq(case.source_row)]")
replace(33, 'display(raw_case)', "display(raw_case)\nprint('Đối chiếu case trong CSV gộp qua file/dòng; không mở lại CSV nguồn trong bản nộp.')")

replace(35, '- **Môi trường yêu cầu:** Python phiên bản 3.10 trở lên.',
        '- **Môi trường đã kiểm:** Python 3.12; numpy 2.5.4, pandas 3.0.6, scipy 1.18.1, scikit-learn 1.9.1, matplotlib 3.11.2, seaborn 0.13.2, ipykernel 7.4.0.')
replace(35, 'Đảm bảo cấu trúc thư mục chứa đầy đủ `data/raw/` (20 tệp CSV) và `config/experiment_config.json`.',
        'Đặt `airbnb_combined.csv` cùng thư mục với notebook; thư mục làm việc của kernel phải là thư mục này.')
replace(35, 'Quá trình tính toán chạy tuần tự từ Cell 0 đến Cell cuối cùng trong khoảng 2–3 phút mà không yêu cầu thêm bất kỳ thao tác thủ công nào.',
        'Chạy tuần tự đến cell cuối với môi trường có đủ thư viện; thời gian tùy máy. Không cần JSON, manifest, thư mục repo hoặc file trung gian. Nếu thiếu thư viện, cài bằng `%pip install numpy==2.5.4 pandas==3.0.6 scipy==1.18.1 scikit-learn==1.9.1 matplotlib==3.11.2 seaborn==0.13.2 ipykernel==7.4.0` rồi restart kernel.')
replace(35, 'kiểm tra độc lập trên 10.342 mẫu Test', 'kiểm tra trên holdout 10.342 dòng; chưa xác minh độc lập theo listing')
replace(36, '{len(raw_csv_files)} tệp CSV thô', '{len(inventory)} nhóm nguồn trong CSV gộp')
replace(36, 'Hiệu năng kiểm tra độc lập trên tập Holdout Test', 'Hiệu năng trên tập Holdout Test tách theo dòng')

nb = nbformat.v4.new_notebook(cells=[nbformat.from_dict({**cell, 'metadata': {},
    **({'outputs': [], 'execution_count': None} if cell['cell_type'] == 'code' else {})}) for cell in cells],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
              'language_info': {'name': 'python'},
              'ie313': {'base_commit': '67fb260', 'format': 'Han original cells and layout',
                        'generated_by': 'scripts/build_final_notebook.py'}})
path = ROOT / 'notebooks/IE313_Airbnb_Final.ipynb'
nbformat.write(nb, path)
print(path, len(cells), 'cells; Han baseline preserved')
