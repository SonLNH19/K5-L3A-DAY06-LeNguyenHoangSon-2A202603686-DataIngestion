# Kết quả và phương pháp audit

- `trace_dev.json` và `trace_test.json` lưu top-3, điểm cosine, metadata và nhãn khớp evidence chính xác. `metrics_dev.json` và `metrics_test.json` chứa chỉ số tự động, chưa tính bằng chứng tương đương.
-`metrics_dev_reviewed.json` cộng thêm các trường hợp này và được dùng để chọn C trước khi chạy test.
- `selected_strategy.json` lưu lựa chọn, hash benchmark/index và phương pháp đánh giá. Nhãn dev có Codex hỗ trợ rà soát và được học viên xác nhận sau khi đã xem test.
- `metadata_audit_test.csv` lưu kết quả đối chiếu tự động 45 bản ghi metadata với manifest và nguồn; học viên xác nhận đã xem sau test. Việc đối chiếu ban đầu là tự động.
- `grounding_audit_test.csv` chứa 15 nhãn grounding 0–2 từ top-3, có Codex hỗ trợ chấm kèm lý do và được học viên xác nhận sau test. Grounding không phải độ chính xác câu trả lời LLM.
- `coherence_positions.json` lưu mẫu ban đầu, nhưng vị trí rơi vào banner MDX. `coherence_positions_corrected.json` lưu mẫu đoạn văn trên cùng 10 bài, được chọn lại sau khi xem test. `coherence_audit.csv` chứa 30 nhãn có Codex hỗ trợ chấm. Cả hai mẫu được giữ để thể hiện giới hạn và nguy cơ thiên lệch.
- `ingestion_stats.json`, `ingestion_stats_reload.json` và `ingestion_errors.json` lưu thống kê ingest ban đầu, nạp lại và lỗi đọc. Thời gian giữa các lần chạy có thể khác.


Tập test nhỏ, kết quả không đại diện cho mọi corpus hay nhiệm vụ.
