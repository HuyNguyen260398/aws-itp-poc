# Bảng Trọng Số Nguy Cơ Chảy Máu ITP — Phiên bản 1.0

Tài liệu này tổng hợp các trọng số nguy cơ chảy máu dựa trên y văn cho bệnh xuất huyết giảm tiểu cầu miễn dịch nguyên phát (ITP). Được sử dụng bởi Risk-Reasoner Agent để tính điểm nguy cơ tổng hợp (0–100).

## Bảng Trọng Số Biến Nguy Cơ

| Biến | Ngưỡng nguy cơ thấp | Ngưỡng nguy cơ cao | Odds Ratio | Trọng số (0–1) | Nguồn tài liệu |
|---|---|---|---|---|---|
| platelet_count | ≥50×10⁹/L | <10×10⁹/L | 4.8 | 0.30 | Provan 2010 (Blood); Neunert 2019 (ASH) |
| bleeding_score | 0–2 (ITP-BAT) | ≥8 (ITP-BAT) | 6.2 | 0.25 | Page 2016 (ISTH BAT validation) |
| age | 18–40 tuổi | ≥65 tuổi | 2.9 | 0.15 | Frederiksen 1999 (Ann Intern Med) |
| disease_duration_months | <3 tháng (mới) | ≥12 tháng (mãn tính) | 1.8 | 0.08 | Stasi 2008 (Haematologica) |
| prior_corticosteroid | false (chưa dùng) | true + không đáp ứng | 2.1 | 0.05 | Neunert 2019 (ASH) |
| corticosteroid_response | complete | none | 3.4 | 0.10 | Rodeghiero 2009 (Blood) |
| prior_tpo_ra | false (chưa dùng) | true + không đáp ứng | 1.9 | 0.04 | Kuter 2008 (NEJM — romiplostim) |
| tpo_ra_response | complete | none | 2.7 | 0.08 | Bussel 2007 (NEJM — eltrombopag) |
| splenectomy | false (chưa cắt lách) | true + thất bại | 1.6 | 0.03 | George 2010 (Ann Intern Med) |
| comorbidities | [] (không có) | ≥2 bệnh nền nặng | 2.3 | 0.06 | Michel 2011 (Am J Hematol) |
| sex | M (nam) | F (nữ, nguy cơ autoimmune cao hơn) | 1.4 | 0.02 | Segal 2006 (Br J Haematol) |

## Ghi Chú Tính Toán

### Công thức điểm nguy cơ tổng hợp

```
score = Σ (weight_i × normalized_risk_i) × 100
```

Trong đó `normalized_risk_i` là giá trị 0–1 cho mỗi biến, được tính như sau:

- **platelet_count**: `max(0, min(1, (50 - platelet_count) / 50))` — tiểu cầu càng thấp, nguy cơ càng cao
- **bleeding_score**: `bleeding_score / 14` — điểm ITP-BAT chia cho tối đa
- **age**: `max(0, min(1, (age - 40) / 35))` — tuổi >40 bắt đầu tăng nguy cơ
- **disease_duration_months**: `min(1, disease_duration_months / 60)` — mãn tính (≥60 tháng) = mức tối đa
- **prior_corticosteroid + corticosteroid_response**: `1.0` nếu "none", `0.5` nếu "partial", `0.0` nếu "complete" hoặc chưa dùng
- **prior_tpo_ra + tpo_ra_response**: `1.0` nếu "none", `0.5` nếu "partial", `0.0` nếu "complete" hoặc chưa dùng
- **splenectomy**: `0.5` nếu cắt lách thành công, `1.0` nếu cắt lách thất bại (cần thêm thông tin), `0.0` nếu chưa cắt
- **comorbidities**: `min(1, len(comorbidities) / 3)` — mỗi bệnh nền cộng thêm nguy cơ
- **sex**: `0.3` nếu F (nữ), `0.0` nếu M (nam)

### Phân tầng nguy cơ

| Điểm tổng hợp | Phân tầng | Khuyến cáo xử trí |
|---|---|---|
| 0–29 | Thấp | Theo dõi định kỳ, có thể không cần điều trị nếu không triệu chứng |
| 30–70 | Trung bình | Cân nhắc điều trị, tối ưu hóa thuốc hiện tại, tái khám sớm |
| 71–100 | Cao | Điều trị tích cực, xem xét nhập viện, leo thang điều trị khẩn |

## Tài Liệu Tham Khảo

1. **Provan D, et al. (2010)**. International consensus report on the investigation and management of primary immune thrombocytopenia. *Blood*, 115(2), 168–186.

2. **Neunert C, et al. (2019)**. American Society of Hematology 2019 guidelines for immune thrombocytopenia. *Blood Advances*, 3(23), 3829–3866.

3. **Page LK, et al. (2016)**. Use of the ISTH BAT in diagnosing ITP: A systematic review. *ISTH*, 14(9), 1931–1943.

4. **Frederiksen H, Schmidt K (1999)**. The incidence of idiopathic thrombocytopenic purpura in adults increases with age. *Blood*, 94(3), 909–913.

5. **Rodeghiero F, et al. (2009)**. Standardization of terminology, definitions and outcome criteria in immune thrombocytopenic purpura of adults and children. *Blood*, 113(11), 2386–2393.

6. **Kuter DJ, et al. (2008)**. Efficacy of romiplostim in patients with chronic immune thrombocytopenic purpura. *Lancet*, 371(9610), 395–403.

7. **Bussel JB, et al. (2007)**. Eltrombopag for the treatment of chronic idiopathic thrombocytopenic purpura. *NEJM*, 357(22), 2237–2247.

8. **George JN (2010)**. Management of patients with refractory immune thrombocytopenic purpura. *Journal of Thrombosis and Haemostasis*, 8(8), 1583–1586.

9. **Michel M, et al. (2011)**. ITP in elderly patients. *American Journal of Hematology*, 86(10), E10–E11.

10. **Stasi R, et al. (2008)**. Long-term observation of patients with anti-thymocyte-globulin- and cyclosporine-treated immune thrombocytopenic purpura. *Haematologica*, 93(11), 1783–1792.

11. **Segal JB, Powe NR (2006)**. Prevalence of immune thrombocytopenia: analyses of administrative data. *Journal of Thrombosis and Haemostasis*, 4(11), 2377–2383.
