## RANKING 

#### For development

```py

from ranking import TFRanking

title = 'VCBS: Vẫn còn dư địa giảm cả lãi suất huy động và cho vay'
brief_content = 'VCBS kỳ vọng NHNN sẽ điều hành chính sách tiền tệ theo hướng chủ động, linh hoạt và duy trì thanh khoản hệ thống dồi dào.'
content = """
Trong báo cáo thị trường trái phiếu tháng 2/2021 mới được công bố, Chứng khoán Vietcombank (VCBS) nhận định thời điểm hiện tại, vẫn còn dư địa giảm với cả lãi suất huy động và cho vay. Cụ thể về mặt chính sách điều hành, VCBS kỳ vọng Ngân hàng Nhà nước sẽ điều hành theo hướng chủ động, linh hoạt và duy trì thanh khoản hệ thống dồi dào. Mặt bằng lãi suất cho vay sẽ còn dư địa giảm thêm trong bối cảnh lãi suất huy động đã giảm khá trong khoảng 1 năm trở lại đây. Thực tế, trong tháng vừa qua, nhiều ngân hàng thương mại đã đưa ra nhiều gói hỗ trợ về lãi suất cho vay nhằm đồng hành với doanh nghiệp, vượt qua dịch bệnh. Trên thị trường liên ngân hàng, mặc dù ghi nhận áp lực tăng nhanh vào mạnh trước thời điểm Tết Nguyên đán, lãi suất liên ngân hàng đã giảm trở lại nhờ thanh khoản dồi dào. "Vào thời điểm sát Tết Nguyên đán, thanh khoản hệ thống thường ghi nhận những áp lực nhất định. Tuy nhiên, chúng tôi đánh giá áp lực này chỉ mang tính chất mùa vụ", VCBS cho hay. Cụ thể, ngay sau nghỉ lễ, thanh khoản dồi dào trở lại, kéo theo xu hướng giảm của lãi suất liên ngân hàng. Trong bối cảnh lo ngại diễn biến dịch bệnh, kỳ vọng và nhu cầu tín dụng khó có khả năng được đẩy mạnh. Hơn nữa, dòng vốn đầu tư vẫn tiếp tục tìm đến địa điểm lý tưởng như Việt Nam. "Các yếu tố vẫn đang ủng hộ nhận định mặt bằng lãi suất liên ngân hàng có thể tiếp tục giảm nhẹ và duy trì ở mặt bằng thấp", nhóm phân tích đánh giá. Ngoài ra, VCBS giữ nguyên dự báo về các chính sách nới lỏng tiền tệ sẽ tiếp tục được duy trì ít nhất cho tới năm 2022 đối với nhiều ngân hàng trung ương lớn khi mục tiêu ưu tiên của giai đoạn này vẫn sẽ là hỗ trợ nền kinh tế hồi phục sau dịch bệnh
"""

# - Use TFRanking

ranking = TFRanking(config_file='./config_ranking.yaml', code_file='./stock_code.yaml')

out = ranking.get_rank(title=title, brief_content=brief_content, content=content, prior_category='banking')

print(out)

# - Use RuleRanking
ranking = RuleRanking(config_file='./config_ranking.yaml')

out = ranking.get_rank(title=title, brief_content=brief_content, content=content, prior_category='banking')

print(out)

# {'rank': 3, 'score': 0.02150537634408602, 'name_rank': 'import_or_export'}

```