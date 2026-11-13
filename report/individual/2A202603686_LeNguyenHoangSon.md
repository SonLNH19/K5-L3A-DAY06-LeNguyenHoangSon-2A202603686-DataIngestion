# Báo cáo cá nhân — Data Ingestion

## Dữ liệu và pipeline

- Chủ đề: tokenization và xử lý văn bản bằng Transformer. Corpus gồm 30 bài MDX tiếng Anh độc lập từ Hugging Face LLM Course, giấy phép Apache 2.0; nguồn, commit, hash và từng bài được ghi trong `data/manifest.json`. ID bài như `chapter6/4` là vị trí truy vết tương đương trang PDF; không nhân bản dữ liệu.
- Python đọc MDX, kiểm tra SHA-256, chuẩn hóa Unicode NFC và whitespace, giữ markup/code và ghi lỗi; không dùng OCR. Markup có thể làm nhiễu chunk. `results/ingestion_errors.json` ghi lỗi đọc.
- Model thật local Chroma ONNX `all-MiniLM-L6-v2`, 384 chiều, archive SHA-256 trong `results/ingestion_stats.json`; cùng tokenizer, mean pooling và L2 normalization cho query/document. Python 3.12.10, Chroma 1.5.9, ONNX Runtime 1.31.1, tokenizers 0.23.3; cosine, tìm kiếm HNSW xấp xỉ. Lệnh chạy xem `starter/README.md`; chi phí API 0 USD. Tokenizer cắt đầu vào tại 256 token.
- Metadata: `document_id`, `source`, `page`, `chapter` là chuỗi; `chunk_index` là số nguyên. `chapter` lấy từ đường dẫn và manifest, giúp lọc phạm vi được câu hỏi cung cấp. `page` là ID bài học, không phải trang vật lý.

## Cấu hình và benchmark

- A: cửa sổ 500 ký tự, overlap 50, không lọc. B: gộp đoạn đến 900 ký tự, đoạn quá dài chia cửa sổ overlap 50, không lọc. C: cùng chunk và index B, chỉ lọc `chapter` khi câu hỏi cung cấp.
- 20 câu có đáp án và evidence: 15 dev ở các bài chương 1–4, 5 test ở các bài chương 6–7; ba câu có filter, trong đó Q16 thuộc test. Bộ câu hỏi đã được đối chiếu evidence với nguồn sau NFC và chuẩn hóa khoảng trắng. Có thể tồn tại evidence hợp lệ chưa được nhận diện; xem `benchmark/README.md`.
- Chốt tiêu chí trước benchmark: ưu tiên Evidence Hit@3 dev, rồi Hit@1 dev, sau đó thời gian ingest và thứ tự A/B/C. Dựa trên nhãn dev, chọn C trước khi chạy test; hash benchmark/index và phương pháp ghi trong `results/selected_strategy.json`.

## Kết quả

| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk | Ingest lần đầu | Chi phí API |
|---|---|---:|---:|---:|---:|---:|
| A | dev | 6/15 | 8/15 | 1.290 | 21,049 s | 0 USD |
| B | dev | 8/15 | 11/15 | 784 | 12,494 s | 0 USD |
| C | dev | 9/15 | 12/15 | 784 | dùng chung B | 0 USD |
| A | test | 3/5 | 3/5 | 1.290 | 21,049 s | 0 USD |
| B | test | 2/5 | 2/5 | 784 | 12,494 s | 0 USD |
| C | test | 2/5 | 2/5 | 784 | dùng chung B | 0 USD |



| Strategy | Coherence /2 (n=10) | Metadata đúng/đủ (n/N) | Top-3 tuân thủ filter test | Grounding 0/1/2; trung bình /2 |
|---|---:|---:|---:|---|
| A | 1,0 | 15/15 | 0/1 | 0/2/3; 1,6 |
| B | 1,9 | 15/15 | 1/1 | 2/1/2; 1,0 |
| C | 1,9 | 15/15 | 1/1 | 2/1/2; 1,0 |

Giới hạn đánh giá coherence: Mẫu 10 vị trí ban đầu được chọn trước khi xem test nhưng rơi vào phần markup/banner MDX. Mẫu đoạn trên cùng 10 bài được chọn lại sau khi đã xem kết quả test. Việc chọn lại có thể tạo thiên lệch cho điểm coherence. Cả hai mẫu và lý do chấm từng chunk đều được lưu trong thư mục results/. Việc chọn lại mẫu audit không làm thay đổi cấu hình đã dùng để chạy benchmark nhé ạ


## Phân tích và giới hạn

- A–B: trên dev, B tốt hơn về Hit@3 và trong mẫu coherence có điểm cao hơn; test nhỏ lại cho A 3/5 so với B 2/5. A tạo 638.577 ký tự chunk và B 574.847, do cách chia và overlap khác nhau. Thời gian đo tuần tự, A chịu chi phí khởi tạo model nên không phải so sánh hiệu năng hoàn toàn công bằng.
- B–C: C thêm filter cho câu có phạm vi, cải thiện dev Hit@3 từ 11/15 lên 12/15. Trên test cả hai 2/5; câu filter Q16 có top-3 của B và C đều thuộc chapter6. Không thể kết luận filter luôn cải thiện.
- Hai lỗi ví dụ: Q16, cả ba cấu hình không tìm được đủ hai bước normalization và pre-tokenization; A còn trả một chunk từ chapter2 dù câu yêu cầu chapter6. Q17, top-3 B/C không chứa quy tắc ánh xạ ký tự chưa có sang unknown token; A có ngữ cảnh về ngoại lệ GPT-2 nhưng không đủ quy tắc. Xem ID chunk, điểm và nguồn trong `results/trace_test.json`.
- `chapter` giúp thu hẹp phạm vi và `page` truy về bài nguồn; hạn chế là tên chương chỉ lấy từ cấu trúc nguồn, không bảo đảm chunk tự đủ ngữ cảnh. Model cắt ở 256 token, corpus giữ markup và test chỉ có 5 câu. Dev/test khác file nhưng cùng chủ đề, có nguy cơ trùng khái niệm.
- Codex được sử dụng để hỗ trợ viết hàm, đề xuất câu hỏi và hỗ trợ rà soát các nhãn evidence, coherence và grounding; em xác nhận đã xem các nhãn sau test.
