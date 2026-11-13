# Pipeline bài lab

Bài làm dùng Python 3.12, Chroma lưu cục bộ và embedding ONNX `all-MiniLM-L6-v2`. Docker Compose và script `check_setup.py` là starter pgvector tùy chọn ban đầu; pipeline hiện tại **không dùng PostgreSQL**. Corpus gồm 30 bài MDX trong [data/transformers-nlp](../data/transformers-nlp), với nguồn, commit và giấy phép tại [data/manifest.json](../data/manifest.json). Xem [data/README.md](../data/README.md) để xác minh và tái tạo dữ liệu.

Các module trong `src/`:

- `models.py`: kiểu dữ liệu của metadata và chunk.
- `ingestion.py`: đọc 30 bài MDX, kiểm tra SHA-256, chuẩn hóa và ghi lỗi.
- `chunking.py`: chia fixed-size A và theo đoạn B; C dùng chung chunk B.
- `embeddings.py`: tải và chạy model ONNX thật cho văn bản và query.
- `store.py`: lưu Chroma bền vững, nạp lại không trùng và tìm kiếm có filter.
- `evaluation.py`: đối chiếu evidence chính xác và tổng hợp chỉ số tự động; evidence tương đương vẫn cần audit.
- `run.py`: kết nối các bước, chạy dev và khóa test cho tới khi lựa chọn được rà soát.

Từ PowerShell tại `starter/` trong bản clone sạch, kiểm tra `python --version` là **3.12** và xác nhận chưa có `.venv`. Nếu chưa có Python 3.12, cài từ [python.org](https://www.python.org/downloads/release/python-31210/). Nếu `python` trỏ tới phiên bản khác nhưng Python Launcher có 3.12, thay lệnh tạo môi trường bằng `py -3.12 -m venv .venv`; nếu không có launcher, dùng đường dẫn đầy đủ tới `python.exe` 3.12. Không tạo đè môi trường cũ bằng phiên bản Python khác.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements-chroma.txt
.\.venv\Scripts\python.exe -m src.run
```

Phiên bản `.venv` phải là 3.12 trước khi cài thư viện. Model khoảng 79 MiB được tải lần đầu và kiểm tra hash; lỗi model/backend được báo thay vì chuyển sang vector giả. Model lưu tại `starter/.models/`, index Chroma tại `starter/.chroma-lab/`. Chạy lại lệnh ingest không có `--rebuild` để kiểm tra không nhân đôi. Lệnh ingest ghi thống kê vào `results/`, nên dùng bản clone riêng nếu muốn giữ nguyên kết quả đã nộp. Nếu corpus hoặc cấu hình index thay đổi, `python -m src.run --rebuild` xóa hai collection lab và tạo lại.

Xem [results/README.md](../results/README.md) và [benchmark/README.md](../benchmark/README.md) để phân biệt kết quả khớp evidence tự động, nhãn có AI hỗ trợ và các giới hạn đánh giá. Test đã được chạy sau khi chọn C trên dev; không dùng test để chỉnh cấu hình rồi trình bày như holdout độc lập.

Tùy chọn trên bản clone kiểm tra: `.\.venv\Scripts\python.exe -m src.run --split dev` và `.\.venv\Scripts\python.exe -m src.run --split test`. Chúng ghi đè trace và metric tương ứng. Kết quả in ra là khớp evidence chính xác tự động; chỉ số dev trong báo cáo còn tính evidence tương đương đã được rà soát trong `results/metrics_dev_reviewed.json`.
