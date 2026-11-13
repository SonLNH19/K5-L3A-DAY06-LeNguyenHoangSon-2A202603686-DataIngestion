# Nguồn dữ liệu và cách xác minh

## Nguồn và quyền sử dụng

- **Nguồn:** Hugging Face, [The Hugging Face Course](https://github.com/huggingface/course), commit `8b893f0ede6c781045692a7f892f25a0c92b4805`.
- **Giấy phép:** [Apache License 2.0](transformers-nlp/LICENSE). Tài liệu khóa học [công bố cho phép tái sử dụng](https://github.com/huggingface/course/blob/8b893f0ede6c781045692a7f892f25a0c92b4805/chapters/en/chapter1/1.mdx): ghi nguồn, kèm giấy phép và nêu thay đổi. Cần tôn trọng thông báo bản quyền hoặc quyền của bên thứ ba áp dụng riêng nếu có; các URL, hình ảnh, model và tài nguyên ngoài repo không tự động có cùng giấy phép.
- **Dữ liệu của bài:** chọn 30 file MDX tiếng Anh từ nguồn trên, không tự tạo hoặc nhân bản nội dung nguồn. Danh sách, URL từng file, số ký tự và SHA-256 có tại [manifest.json](manifest.json). Windows Git đã chuyển kết thúc dòng LF thành CRLF trong snapshot; nội dung khác được giữ theo snapshot đã chọn. Pipeline chuẩn hóa Unicode và whitespace, sau đó tạo chunk và trace phục vụ thí nghiệm. Không có dữ liệu cá nhân hoặc tài liệu nội bộ được cố ý đưa vào corpus.
- **Benchmark:** bộ 20 câu, câu trả lời, phân chia và evidence do học viên xây dựng với công cụ AI hỗ trợ, lưu trong [benchmark/questions.json](../benchmark/questions.json). Mỗi `gold_page` là ID bài MDX, không phải số trang PDF.

Các file MDX được nộp cùng [LICENSE](transformers-nlp/LICENSE), nên người chấm có thể đọc trực tiếp. Trace chứa trích đoạn được truy từ các file này, không phải bản sao tự động của các hình ảnh/tài nguyên bên ngoài được liên kết. Giữ nguyên giấy phép và thông báo nguồn khi chia sẻ. `.gitattributes` giữ nguyên byte của file MDX trong Git để hash không thay đổi theo hệ điều hành.

## Cách người chấm xác minh

Tại thư mục gốc repo, dùng Python 3.12:

```powershell
python data\verify_submission.py
```

Script kiểm tra hash của 30 file, evidence của 20 câu và nguồn/metadata của top-3 trong trace dev/test. Script không chứng minh đáp án đúng hoặc thay thế chấm audit thủ công. Nếu muốn đối chiếu một câu bằng mắt: tra `gold_page` trong `benchmark/questions.json`, tìm file tương ứng và `source_url` trong manifest, rồi so `evidence_quote` với nội dung file và top-3 trong `results/trace_dev.json` hoặc `results/trace_test.json`.

Nếu một file corpus không được kèm theo, có thể tải lại những file thiếu từ commit đã chốt:

```powershell
python data\recreate_corpus.py
python data\verify_submission.py
```

Script tải từ `raw.githubusercontent.com`, chỉ ghi file còn thiếu và đối chiếu SHA-256 trước khi ghi; không ghi đè file hiện có. Khi cần, script thử chuyển LF sang CRLF để khôi phục đúng snapshot; nếu hash vẫn khác, script báo lỗi. Nếu thiếu `data/transformers-nlp/LICENSE`, lấy nguyên file LICENSE tại commit nguồn và giữ cùng corpus. Lệnh tái tạo cần mạng; lệnh xác minh không cần mạng khi dữ liệu đã có.

Hướng dẫn cài và chạy pipeline nằm ở [starter/README.md](../starter/README.md). Các kết quả thí nghiệm và phương pháp chấm nằm trong [results/README.md](../results/README.md). Lần chạy lại có thể khác thời gian hoặc thứ tự khi điểm gần nhau do HNSW.
