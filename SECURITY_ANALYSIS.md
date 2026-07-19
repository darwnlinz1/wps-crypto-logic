# Phân tích cơ chế mã hóa phía client — WPS Office

**Loại tài liệu:** Báo cáo nghiên cứu bảo mật (Security Research Write-up)
**Tác giả:** darwnlinz1
**Trạng thái:** Công khai, đã ẩn thông tin nhạy cảm

## 1. Tóm tắt (Executive Summary)

Nghiên cứu này phân tích cách ứng dụng WPS Office mã hóa mật khẩu người dùng ở phía client (trên máy người dùng) trước khi gửi lên máy chủ. Kết quả cho thấy ứng dụng dùng thuật toán **RSA với padding PKCS#1 v1.5** và một cơ chế "thử nhiều dạng payload" khá bất thường: nó lần lượt thử mật khẩu ở dạng thô, rồi các dạng băm (hash) MD5/SHA-256 cho đến khi vừa với giới hạn kích thước khóa RSA. Cách làm này lộ ra vài điểm yếu về thiết kế mật mã (padding lỗi thời, thiếu xác thực toàn vẹn, logic không nhất quán). Báo cáo mô tả phương pháp phân tích, đánh giá rủi ro và đề xuất cách khắc phục theo chuẩn hiện đại.

## 2. Phạm vi & Đạo đức (Scope & Ethics)

- Toàn bộ phân tích được thực hiện trên phần mềm **do tôi tự cài đặt hợp pháp trên máy của mình**, phục vụ mục đích học tập và nghiên cứu bảo mật.
- **Không có hệ thống nào bị tấn công.** Không truy cập trái phép vào máy chủ WPS hay tài khoản của bất kỳ ai.
- Báo cáo **không công bố khóa thật, không kèm mã khai thác (exploit), không hỗ trợ vượt bản quyền**. Mọi khóa trong ví dụ đều là khóa giả (`dummy`) dùng để minh họa.
- Mục tiêu: chứng minh khả năng đọc hiểu và đánh giá một sơ đồ mật mã đóng, đồng thời đề xuất hướng vá lỗi.

## 3. Phương pháp (Methodology)

- **Môi trường:** máy Windows cá nhân, cô lập, không ảnh hưởng hệ thống khác.
- **Cách tiếp cận:**
  1. Quan sát luồng đăng nhập để xác định thời điểm mật khẩu được xử lý trước khi rời khỏi client.
  2. Phân tích logic mã hóa để xác định thuật toán, kiểu padding và cách chọn payload.
  3. Tái hiện độc lập cơ chế bằng một module Python riêng (dùng thư viện `cryptography`) để kiểm chứng hiểu biết — chạy được với **khóa công khai giả**, không dùng khóa thật của WPS.
- **Tiêu chí "hiểu đúng":** module tự dựng lại được đúng định dạng payload mà ứng dụng gốc tạo ra, không cần dùng lại binary gốc.

## 4. Phát hiện kỹ thuật (Technical Findings)

**Thuật toán:** RSA, padding **PKCS#1 v1.5**.

**Cách chọn payload (điểm đáng chú ý nhất):** thay vì luôn mã hóa mật khẩu thô, ứng dụng tính giới hạn kích thước cho phép của khóa RSA — với PKCS#1 v1.5 là `(kích_thước_khóa_byte − 11)` — rồi lần lượt thử các dạng sau và chọn dạng đầu tiên vừa khít:

1. Mật khẩu thô (UTF-8)
2. SHA-256 (bytes)
3. SHA-256 (chuỗi hex)
4. MD5 (bytes)
5. MD5 (chuỗi hex)

**Luồng dữ liệu (mô tả):**

```
[Mật khẩu người dùng]
        │
        ▼
[Chọn dạng payload phù hợp kích thước khóa]  ← thử thô → SHA-256 → MD5
        │
        ▼
[Mã hóa RSA / PKCS#1 v1.5 bằng khóa công khai]
        │
        ▼
[Mã hóa Base64] ──► gửi lên API
```

**Xử lý khóa/IV:** dùng khóa công khai RSA (khóa thật đã ẩn — `[REDACTED]`). RSA không dùng IV. Không phát hiện lớp mã hóa đối xứng hay kiểm tra toàn vẹn nào đi kèm.

## 5. Đánh giá bảo mật (Security Assessment)

- **Padding PKCS#1 v1.5 đã lỗi thời.** Kiểu padding này có tiền sử dính các lỗi dạng *padding oracle* (Bleichenbacher). Chuẩn hiện đại là **RSA-OAEP**.
- **Logic "thử nhiều dạng payload" là dấu hiệu thiết kế lỏng lẻo.** Việc chấp nhận nhiều định dạng khiến hệ thống khó kiểm soát và dễ có hành vi ngoài ý muốn; một sơ đồ mật mã tốt phải có **một** định dạng payload xác định.
- **Còn dùng MD5.** MD5 đã bị coi là hỏng về mặt mật mã; sự hiện diện của nó (dù chỉ là fallback) cho thấy thiết kế chưa được cập nhật.
- **Thiếu xác thực/toàn vẹn.** RSA mã hóa đơn thuần chỉ đảm bảo bí mật, **không** chứng thực dữ liệu không bị sửa. Cần cơ chế xác thực (authenticated encryption).
- **Rủi ro nếu khóa nhỏ.** Nếu khóa thật ở mức 512–1024 bit thì độ an toàn rất thấp (512-bit RSA có thể bị phá). Khuyến nghị tối thiểu 2048-bit.
- **Ghi chú bối cảnh:** kênh truyền thường đã được TLS bảo vệ, nên lớp RSA phía client này chủ yếu là phòng thủ bổ sung; nếu tự làm không chuẩn, nó dễ trở thành *security theater* (trông có vẻ an toàn nhưng không tăng an toàn thực chất).

## 6. Khuyến nghị (Recommendations)

Nếu đây là ứng dụng của tôi, tôi sẽ:

1. **Thay PKCS#1 v1.5 bằng RSA-OAEP (SHA-256).**
2. **Dùng một định dạng payload duy nhất, cố định** — bỏ hoàn toàn cơ chế thử nhiều dạng.
3. **Loại bỏ MD5.** Nếu cần băm, dùng SHA-256 trở lên.
4. **Với dữ liệu lớn, dùng mã hóa lai (hybrid):** AES-256-GCM cho dữ liệu + RSA-OAEP để bọc khóa AES — vừa bí mật vừa toàn vẹn.
5. **Không xác thực mật khẩu bằng cách mã hóa trực tiếp.** Nên dùng giao thức chuẩn (ví dụ băm phía server bằng Argon2/bcrypt, hoặc cơ chế như SRP) để server không bao giờ thấy mật khẩu thô.
6. **Khóa RSA ≥ 2048-bit** và có quy trình luân chuyển khóa.

## 7. Kết luận & Bài học (Conclusion & What I Learned)

Qua bài này tôi luyện được: xác định thuật toán và padding trong một sơ đồ mật mã đóng, hiểu vì sao PKCS#1 v1.5 và MD5 bị xem là rủi ro, và tái hiện độc lập một cơ chế để kiểm chứng hiểu biết mà không cần chạm vào hệ thống của bên khác. Quan trọng nhất: phân biệt được giữa "mã hóa cho có" và mã hóa thật sự an toàn — cùng cách viết lại nó cho đúng chuẩn hiện đại.

> *Tuyên bố miễn trừ: Tài liệu chỉ phục vụ mục đích giáo dục và nghiên cứu bảo mật. Không kèm mã khai thác, không công bố khóa thật, không hỗ trợ vi phạm bản quyền.*
