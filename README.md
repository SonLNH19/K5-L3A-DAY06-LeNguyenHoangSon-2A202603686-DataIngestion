# Day 06 · Data Ingestion Engineering

**Lab cá nhân** · **4 giờ** · **Dữ liệu tự chọn**

Biến tài liệu thành kho tri thức có thể truy xuất cho AI agent, rồi đo xem cách chuẩn bị dữ liệu nào hiệu quả nhất.

| 📄 Dữ liệu | 🧩 Chiến lược | 🎯 Benchmark |
|---|---|---|
| Tối thiểu **30 trang nội dung** | Tối thiểu **3 cấu hình** | Tối thiểu **20 câu hỏi** |

## Bắt đầu nhanh

Dùng [starter PostgreSQL + pgvector](starter/README.md) để dựng database và hoàn thiện các hàm TODO, hoặc tự chọn vector store tương đương. Starter chỉ là khung: **bạn tự hiện thực pipeline và benchmark**.

## 1. Xây pipeline

![Đọc tài liệu, chuẩn hóa, chia chunk, tạo vector, lưu và kiểm tra](assets/ingestion-pipeline.svg)

Chọn tài liệu được phép sử dụng; giữ **ID tài liệu, nguồn, trang/vị trí** và metadata phù hợp. Dùng embedding model thật qua API hoặc chạy local; lưu và truy xuất bằng pgvector, Qdrant, Chroma hoặc một store tương đương.

## 2. So sánh và đánh giá

![Ba chiến lược được đánh giá trên cùng corpus và benchmark dev/test](assets/benchmark-workflow.svg)

Dùng cùng dữ liệu, model và câu hỏi cho cả ba cấu hình. Tách **15 câu dev / 5 câu test** trước khi chạy; chọn cấu hình trên dev, rồi đánh giá test sau khi cố định. Mỗi câu hỏi cần có đoạn bằng chứng và trang nguồn; thiết kế bộ câu hỏi và đánh giá theo [BENCHMARK.md](BENCHMARK.md).

Đánh giá theo năm khía cạnh: **độ chính xác truy xuất**, **tính mạch lạc của chunk**, **tính hữu dụng của metadata**, **chất lượng grounding** và **tác động của chiến lược dữ liệu**. Giải thích lựa chọn bằng kết quả, ví dụ lỗi và các đánh đổi.

## 3. Chuẩn bị bài nộp

1. Chạy pipeline và lưu cấu hình, kết quả top-3, trace cùng nhãn đánh giá thủ công.
2. Điền [thông tin học viên](STUDENT.md), [nhật ký thí nghiệm](artifacts/experiment_log.csv) và bản sao [mẫu báo cáo cá nhân](report/individual/MSSV_HoTen.md).
3. Kiểm tra mã nguồn, cách chạy, manifest dữ liệu và checklist trong [SUBMISSION.md](SUBMISSION.md).

## Tài liệu hướng dẫn

| Bạn cần tìm | Tài liệu |
|---|---|
| Setup baseline PostgreSQL + pgvector | [starter/README.md](starter/README.md) |
| Các bước làm và cách tính chỉ số | [GUIDE.md](GUIDE.md) |
| Tiến độ trong 4 giờ | [CHECKPOINTS.md](CHECKPOINTS.md) |
| Năm tiêu chí benchmark và bộ câu hỏi | [BENCHMARK.md](BENCHMARK.md) |
| Tiêu chí chấm điểm | [RUBRIC.md](RUBRIC.md) |
| Quy tắc sử dụng dữ liệu, AI và API | [RULES.md](RULES.md) |
| Cách nộp bài | [SUBMISSION.md](SUBMISSION.md) |

[data/format-example.json](data/format-example.json) chỉ minh họa định dạng, không phải corpus đủ điều kiện. Phần xử lý và benchmark do bạn tự hiện thực; không bắt buộc xây chatbot.

## Cách chạy bài

Bài làm sử dụng corpus [Transformer NLP](data/transformers-nlp) và [manifest](data/manifest.json), Python 3.12, Chroma local và embedding ONNX `all-MiniLM-L6-v2`. Chi tiết cài đặt và giới hạn nằm trong [starter/README.md](starter/README.md).

### 1. Kiểm tra Python

Trên Windows PowerShell, mở **thư mục gốc repo vừa clone** và kiểm tra:

```powershell
python --version
```

Dùng Python **3.12** như môi trường đã ghi trong báo cáo. Nếu `python` hiện phiên bản khác, thử `py -3.12 --version` để kiểm tra bản 3.12 đã cài. Nếu chưa có Python 3.12, tải và cài [Python 3.12.10 từ python.org](https://www.python.org/downloads/release/python-31210/), chọn bản Windows phù hợp với máy. Sau đó mở terminal mới và kiểm tra lại.

### 2. Tạo môi trường và chạy pipeline

Trong bản clone sạch, khi `python --version` hiện 3.12 và `starter/.venv` chưa tồn tại, chạy lần lượt:

```powershell
cd starter
python -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements-chroma.txt
.\.venv\Scripts\python.exe -m src.run
```

Nếu `python` không phải 3.12 nhưng `py -3.12 --version` hoạt động, thay riêng lệnh tạo môi trường bằng `py -3.12 -m venv .venv`. Nếu không có `py`, thay bằng `& "<đường-dẫn-Python-3.12>\python.exe" -m venv .venv`, sau khi thay phần trong dấu `<...>` bằng đường dẫn thật.

Nếu đang đứng sẵn trong `starter`, bỏ qua lệnh `cd starter`. Trước khi cài thư viện, dòng kiểm tra `.venv` phải hiện Python 3.12. Không tạo đè `.venv` cũ bằng phiên bản Python khác; dùng bản clone sạch hoặc một môi trường mới. Nếu đã có môi trường Python 3.12 hoạt động ở nơi khác, dùng đường dẫn `python.exe` của môi trường đó cho các lệnh cài và chạy.

Lần đầu cần mạng để tải thư viện và model khoảng 79 MiB; model được kiểm tra hash và index lưu tại `starter/.chroma-lab/`. Lệnh ingest ghi thống kê vào `results/`; nên chạy trong bản clone riêng nếu muốn giữ nguyên kết quả đã nộp.

### 3. Kiểm tra dữ liệu và trace

Từ thư mục `starter`, chạy:

```powershell
.\.venv\Scripts\python.exe ..\data\verify_submission.py
```

Kết quả mong đợi bắt đầu bằng `OK: 30 source files and hashes; 20 evidence passages; dev/test top-3 trace provenance.` Kiểm tra này không thay thế việc đọc và đánh giá nhãn audit.

Xem [benchmark](benchmark/README.md), [kết quả và phương pháp audit](results/README.md), [hướng dẫn xác minh nguồn dữ liệu](data/README.md) và [báo cáo cá nhân](report/individual/2A202603686_LeNguyenHoangSon.md). Tập test đã được chạy; chạy lại benchmark có thể ghi đè kết quả đã lưu, và không dùng kết quả test để chỉnh cấu hình rồi báo như holdout độc lập.

Để chạy lại retrieval trên bản clone dùng kiểm tra, từ `starter` có thể dùng `.\.venv\Scripts\python.exe -m src.run --split dev` và sau đó `.\.venv\Scripts\python.exe -m src.run --split test`. Hai lệnh ghi đè trace và metric tương ứng trong `results/`; test yêu cầu file chọn cấu hình đã chốt và hash benchmark/index khớp.

Điểm được in khi chạy lại là kết quả **khớp chính xác tự động** trong `metrics_dev.json` / `metrics_test.json`. Điểm dev trong báo cáo dùng `metrics_dev_reviewed.json`, có tính thêm evidence tương đương đã được rà soát; vì vậy hai số có thể khác nhau. Xem [results/README.md](results/README.md) để đối chiếu từng nhãn.
