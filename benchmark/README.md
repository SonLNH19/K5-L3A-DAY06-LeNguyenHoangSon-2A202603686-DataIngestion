# Benchmark trước thử nghiệm

`questions.json` gồm 20 câu hỏi tiếng Anh được xây từ snapshot corpus trong `data/manifest.json`. Không chạy truy xuất để xây bộ này. Dev có Q01–Q15, test có Q16–Q20. Mỗi `gold_page` là ID file bài học MDX, không phải số trang PDF. `gold_source_id` trỏ tới corpus; đường dẫn và URL từng bài có trong manifest.

Tập dev lấy nguồn từ chương 1–4; tập test lấy từ chương 6–7, không dùng chung file. Cách chia này giảm trùng tài liệu, nhưng không loại bỏ rò rỉ chủ đề: cả hai tập đều nói về Transformer, tokenization và fine-tuning. Test chỉ có 5 câu nên không đại diện đầy đủ cho mọi loại câu hỏi hoặc bài học. Các câu kiểm tra filter là Q03, Q08 và Q16; chương cần lọc được nêu trong câu hỏi trước khi tìm kiếm. Các câu khác dùng `filter: null`; cấu hình C không lọc các câu đó.

Evidence được đối chiếu với file nguồn sau chuẩn hóa NFC và gộp khoảng trắng. `create_questions.py` tạo file câu hỏi và kiểm tra sự hiện diện của từng evidence, tính duy nhất ID, số câu và filter. Chạy từ thư mục gốc repo:

```powershell
starter\.venv\Scripts\python.exe benchmark\create_questions.py
```

Các trích dẫn trong file là evidence chính đã xác định, không khẳng định đã liệt kê hết các đoạn tương đương ở nơi khác. Khi chấm, nếu một kết quả khác thực sự đủ hỗ trợ đáp án, người chấm cần đối chiếu nguồn, lưu đoạn và vị trí thay thế cùng lý do trong audit, và chấp nhận bằng chứng tương đương. Không tự động kết luận sai chỉ vì ID nguồn khác. Việc kiểm tra evidence xuất hiện trong nguồn không thay thế việc người học tự đọc, xác nhận evidence đủ chứng minh đáp án và rà soát nhãn.

Giữ nguyên câu hỏi và nhãn giữa A/B/C. Truy vấn chỉ gồm `question` và filter được cung cấp; không đưa `expected_answer`, `gold_source_id`, `gold_page` hoặc `evidence_quote` vào query/filter. Với Hit@1 và Evidence Hit@3, cần cùng nguồn/vị trí gold và đủ evidence, hoặc evidence tương đương đã được xác nhận. Lưu cả tử số và mẫu số. Việc tiền xử lý pipeline phải giữ đủ nội dung evidence để đối chiếu; nếu văn bản bị cắt qua nhiều chunk, ghi lỗi theo định nghĩa chính của GUIDE.

Tiêu chí chọn chiến lược được chốt trước khi chạy benchmark: ưu tiên Evidence Hit@3 trên dev, hòa thì ưu tiên Hit@1 trên dev, sau đó ưu tiên thời gian ingest thấp hơn. Nếu vẫn hòa, chọn cấu hình theo thứ tự A, B, C; ghi đầy đủ số đo và trường hợp hòa. Chỉ chạy và phân tích test sau khi cố định lựa chọn; nếu sửa dựa trên test, công bố việc đó và không trình bày test là holdout độc lập. Sau khi chốt tập, không sửa test dựa trên kết quả.
